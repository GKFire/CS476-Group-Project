from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

import sclibrary.models as M
from sclibrary import services


def make_lender(name="lena"):
    return M.Lender.objects.create_user(name, f"{name}@x.com", "pw12345!")


def make_borrower(name="bob"):
    return M.Borrower.objects.create_user(name, f"{name}@x.com", "pw12345!")


def make_item(lender, title="Zelda"):
    return M.Item.objects.create(
        library=lender.library, title=title, release=date(2020, 1, 1), producer="Nintendo",
        condition="Good", description="d", notes="n", item_format="NS", age_rating="E",
    )


class LibrarySignalTests(TestCase):
    def test_new_lender_gets_library(self):
        lender = make_lender()
        self.assertTrue(M.Library.objects.filter(owner=lender).exists())

    def test_resaving_lender_does_not_create_second_library(self):
        lender = make_lender()
        lender.save()
        self.assertEqual(M.Library.objects.filter(owner=lender).count(), 1)

    def test_deleting_library_cascades_to_items_and_requests(self):
        lender, borrower = make_lender(), make_borrower()
        item = make_item(lender)
        today = date.today()
        services.create_request(borrower, item, today, today + timedelta(days=3))
        lender.library.delete()
        self.assertEqual(M.Item.objects.count(), 0)
        self.assertEqual(M.BorrowRequest.objects.count(), 0)


class RequestServiceTests(TestCase):
    def setUp(self):
        self.lender, self.borrower = make_lender(), make_borrower()
        self.item = make_item(self.lender)
        self.today = date.today()

    def _req(self, days=3):
        return services.create_request(self.borrower, self.item, self.today, self.today + timedelta(days=days))

    def test_create_notifies_lender(self):
        self._req()
        self.assertEqual(M.LenderNotification.objects.filter(recipient=self.lender).count(), 1)

    def test_return_date_before_start_rejected(self):
        with self.assertRaises(ValidationError):
            services.create_request(self.borrower, self.item, self.today, self.today - timedelta(days=1))

    def test_accept_sets_active_and_notifies_borrower(self):
        req = services.accept_request(self._req())
        self.assertEqual(req.status, "AC")
        self.assertEqual(M.BorrowerNotification.objects.filter(recipient=self.borrower).count(), 1)

    def test_accept_can_change_return_date_but_not_before_start(self):
        req = self._req()
        with self.assertRaises(ValidationError):
            services.accept_request(req, self.today - timedelta(days=2))

    def test_cannot_request_item_already_on_loan(self):
        services.accept_request(self._req())
        with self.assertRaises(ValidationError):
            self._req()

    def test_accepting_one_rejects_other_pending(self):
        other = make_borrower("sam")
        first = self._req()
        second = services.create_request(other, self.item, self.today, self.today + timedelta(days=5))
        services.accept_request(first)
        second.refresh_from_db()
        self.assertEqual(second.status, "RJ")

    def test_decline_and_return_flow(self):
        req = services.decline_request(self._req())
        self.assertEqual(req.status, "RJ")
        with self.assertRaises(ValidationError):
            services.mark_returned(req)
        req2 = services.accept_request(self._req())
        self.assertEqual(services.mark_returned(req2).status, "CD")

    def test_cannot_hide_item_on_loan(self):
        services.accept_request(self._req())
        with self.assertRaises(ValidationError):
            services.set_item_visibility(self.item, False)

    def test_hidden_item_cannot_be_requested(self):
        services.set_item_visibility(self.item, False)
        with self.assertRaises(ValidationError):
            self._req()

    def test_overdue_command(self):
        req = services.accept_request(services.create_request(
            self.borrower, self.item, self.today - timedelta(days=10), self.today - timedelta(days=1)))
        call_command("send_overdue_notifications")
        self.assertIn(req.pk, services.overdue_requests().values_list("pk", flat=True))
        self.assertTrue(M.LenderNotification.objects.filter(subject="Item overdue").exists())
        self.assertTrue(M.BorrowerNotification.objects.filter(subject="Item overdue").exists())


class RequestViewTests(TestCase):
    def setUp(self):
        self.lender, self.other_lender = make_lender(), make_lender("lou")
        self.borrower = make_borrower()
        self.item = make_item(self.lender)
        today = date.today()
        self.req = services.create_request(self.borrower, self.item, today, today + timedelta(days=3))

    def test_lender_can_accept(self):
        self.client.force_login(self.lender)
        r = self.client.post(reverse("validate-request", args=[self.req.pk]), {"action": "accept"})
        self.assertEqual(r.status_code, 302)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "AC")

    def test_other_lender_forbidden(self):
        self.client.force_login(self.other_lender)
        r = self.client.post(reverse("validate-request", args=[self.req.pk]), {"action": "accept"})
        self.assertEqual(r.status_code, 403)

    def test_borrower_cannot_decide(self):
        self.client.force_login(self.borrower)
        r = self.client.post(reverse("validate-request", args=[self.req.pk]), {"action": "accept"})
        self.assertEqual(r.status_code, 403)

    def test_borrower_cannot_open_someone_elses_request(self):
        self.client.force_login(make_borrower("eve"))
        self.assertEqual(self.client.get(reverse("view-request", args=[self.req.pk])).status_code, 403)

    def test_lists_are_scoped(self):
        self.client.force_login(self.lender)
        self.assertContains(self.client.get(reverse("myprofile-requests")), "Zelda")
        self.client.force_login(self.other_lender)
        self.assertNotContains(self.client.get(reverse("myprofile-requests")), "Zelda")

    def test_notifications_page_and_mark_read(self):
        self.client.force_login(self.lender)
        self.assertContains(self.client.get(reverse("view-notifications")), "New borrow request")
        self.client.post(reverse("notifications-mark-read"))
        self.assertFalse(M.LenderNotification.objects.filter(has_viewed=False).exists())

    def test_toggle_visibility_owner_only(self):
        self.client.force_login(self.other_lender)
        self.assertEqual(self.client.post(reverse("toggle-item-visibility", args=[self.item.pk])).status_code, 404)
