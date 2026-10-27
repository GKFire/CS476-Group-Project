"""Tests for register and send borrow request (Smit)."""
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import sclibrary.models as M
from sclibrary.tests import make_borrower, make_item, make_lender

PW = "Str0ng-pass-476"


class RegisterTests(TestCase):
    def post(self, **over):
        data = {"username": "Alice", "email": "Alice@Example.com", "account_type": "BORROWER",
                "password1": PW, "password2": PW}
        data.update(over)
        return self.client.post(reverse("register"), data)

    def test_register_borrower_logs_in_and_hashes_password(self):
        r = self.post()
        self.assertRedirects(r, reverse("home"), fetch_redirect_response=False)
        u = M.UserAccount.objects.get(username="alice")
        self.assertEqual(u.user_type, "BORROWER")
        self.assertTrue(M.Borrower.objects.filter(pk=u.pk).exists())
        self.assertNotEqual(u.password, PW)
        self.assertTrue(u.check_password(PW))
        self.assertEqual(int(self.client.session["_auth_user_id"]), u.pk)

    def test_register_lender_gets_library(self):
        self.post(username="len", email="len@x.com", account_type="LENDER")
        lender = M.Lender.objects.get(username="len")
        self.assertTrue(M.Library.objects.filter(owner=lender).exists())

    def test_cannot_register_as_admin(self):
        r = self.post(account_type="ADMIN")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(M.UserAccount.objects.exists())

    def test_duplicate_email_rejected(self):
        make_borrower("bob")
        r = self.post(username="other", email="BOB@x.com")
        self.assertContains(r, "already exists")
        self.assertEqual(M.UserAccount.objects.count(), 1)

    def test_duplicate_username_rejected_case_insensitive(self):
        make_borrower("bob")
        r = self.post(username="BOB", email="new@x.com")
        self.assertContains(r, "already taken")

    def test_mismatched_passwords_rejected(self):
        r = self.post(password2="different-pass-1")
        self.assertContains(r, "do not match")
        self.assertFalse(M.UserAccount.objects.exists())

    def test_can_log_in_after_registering(self):
        self.post()
        self.client.logout()
        self.assertTrue(self.client.login(username="alice", password=PW))


class SendBorrowRequestTests(TestCase):
    def setUp(self):
        self.lender = make_lender()
        self.borrower = make_borrower()
        self.item = make_item(self.lender)
        self.url = reverse("create-request", args=[self.item.pk])
        self.start = date.today() + timedelta(days=1)
        self.ret = date.today() + timedelta(days=14)

    def send(self, start=None, ret=None):
        return self.client.post(self.url, {"start_date": start or self.start, "return_date": ret or self.ret})

    def test_borrower_can_send_request_and_lender_is_notified(self):
        self.client.login(username="bob", password="pw12345!")
        self.assertEqual(self.client.get(self.url).status_code, 200)
        r = self.send()
        self.assertRedirects(r, reverse("myprofile-requests"), fetch_redirect_response=False)
        req = M.BorrowRequest.objects.get()
        self.assertEqual((req.status, req.borrower_id, req.item_id), ("RQ", self.borrower.pk, self.item.pk))
        self.assertTrue(M.LenderNotification.objects.filter(recipient=self.lender).exists())

    def test_lender_cannot_send_request(self):
        self.client.login(username="lena", password="pw12345!")
        self.assertEqual(self.send().status_code, 403)
        self.assertFalse(M.BorrowRequest.objects.exists())

    def test_login_required(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_hidden_item_rejected(self):
        self.item.is_visible = False
        self.item.save()
        self.client.login(username="bob", password="pw12345!")
        self.assertEqual(self.send().status_code, 403)

    def test_item_already_on_loan_rejected(self):
        M.BorrowRequest.objects.create(borrower=self.borrower, item=self.item, start_date=self.start,
                                       return_date=self.ret, status="AC")
        self.client.login(username="bob", password="pw12345!")
        r = self.send()
        self.assertContains(r, "already being borrowed")
        self.assertEqual(M.BorrowRequest.objects.count(), 1)

    def test_past_and_reversed_dates_rejected(self):
        self.client.login(username="bob", password="pw12345!")
        self.assertContains(self.send(start=date.today() - timedelta(days=1)), "cannot be in the past")
        self.assertContains(self.send(ret=self.start), "must be after the start date")
        self.assertFalse(M.BorrowRequest.objects.exists())


class LogoutTests(TestCase):
    def test_sign_out_link_logs_out(self):
        make_borrower("bob")
        self.client.login(username="bob", password="pw12345!")
        r = self.client.get(reverse("logout"))
        self.assertRedirects(r, reverse("index"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)


class ItemFormRenderTests(TestCase):
    def test_add_item_form_uses_visible_fields_and_submits(self):
        lender = make_lender()
        self.client.login(username="lena", password="pw12345!")
        page = self.client.get(reverse("create-item"))
        self.assertContains(page, 'class="sc-form"')
        self.assertContains(page, "<select")
        data = {"title": "Zelda", "release": "2020-01-01", "producer": "Nintendo", "condition": "Good",
                "description": "d", "notes": "n", "item_format": "NS", "age_rating": "E"}
        r = self.client.post(reverse("create-item"), data)
        item = M.Item.objects.get(title="Zelda", library=lender.library)
        self.assertRedirects(r, reverse("view-item", args=[item.pk]), fetch_redirect_response=False)
