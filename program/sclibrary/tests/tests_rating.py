"""Tests for Rate an Item (dopedgod)."""
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

import sclibrary.models as M
from sclibrary import services

PW = "pw12345!"


def make_lender(name="lena"):
    return M.Lender.objects.create_user(name, f"{name}@x.com", PW)


def make_borrower(name="bob"):
    return M.Borrower.objects.create_user(name, f"{name}@x.com", PW)


def make_item(lender, title="Zelda"):
    return M.VideoGame.objects.create(
        library=lender.library, title=title, release=date(2020, 1, 1), producer="Nintendo",
        condition="Good", description="d", notes="n", item_format="NS", age_rating="E",
    )


def borrow(borrower, item, returned=True):
    """Run a full loan through the real services: request -> accept (-> returned)."""
    today = date.today()
    req = services.create_request(borrower, item, today, today + timedelta(days=7))
    services.accept_request(req)
    if returned:
        services.mark_returned(req)
    return req


class RatingServiceTests(TestCase):
    def setUp(self):
        self.lender, self.borrower = make_lender(), make_borrower()
        self.item = make_item(self.lender)

    def test_borrower_can_rate_after_returning(self):
        borrow(self.borrower, self.item)
        rating = services.rate_item(self.borrower, self.item, 4, "  Great game  ")
        self.assertEqual(rating.stars, 4)
        self.assertEqual(rating.review, "Great game")
        self.assertEqual(M.ItemRating.objects.count(), 1)

    def test_new_rating_notifies_lender(self):
        borrow(self.borrower, self.item)
        before = M.UserNotification.objects.filter(recipient=self.lender).count()
        services.rate_item(self.borrower, self.item, 5)
        notes = M.UserNotification.objects.filter(recipient=self.lender)
        self.assertEqual(notes.count(), before + 1)
        self.assertTrue(notes.filter(subject="New item rating").exists())

    def test_cannot_rate_item_never_borrowed(self):
        with self.assertRaisesMessage(ValidationError, "borrowed and returned"):
            services.rate_item(self.borrower, self.item, 3)
        self.assertEqual(M.ItemRating.objects.count(), 0)

    def test_cannot_rate_while_still_on_loan(self):
        borrow(self.borrower, self.item, returned=False)
        with self.assertRaises(ValidationError):
            services.rate_item(self.borrower, self.item, 3)

    def test_cannot_rate_with_declined_request(self):
        today = date.today()
        req = services.create_request(self.borrower, self.item, today, today + timedelta(days=7))
        services.decline_request(req)
        with self.assertRaises(ValidationError):
            services.rate_item(self.borrower, self.item, 3)

    def test_other_borrowers_loan_does_not_count(self):
        borrow(make_borrower("sam"), self.item)
        self.assertFalse(services.can_rate(self.borrower, self.item))
        with self.assertRaises(ValidationError):
            services.rate_item(self.borrower, self.item, 3)

    def test_stars_out_of_range_rejected(self):
        borrow(self.borrower, self.item)
        for bad in (0, 6, -1):
            with self.assertRaises(ValidationError):
                services.rate_item(self.borrower, self.item, bad)

    def test_rating_again_updates_instead_of_duplicating(self):
        borrow(self.borrower, self.item)
        services.rate_item(self.borrower, self.item, 2, "meh")
        services.rate_item(self.borrower, self.item, 5, "grew on me")
        self.assertEqual(M.ItemRating.objects.count(), 1)
        rating = M.ItemRating.objects.get()
        self.assertEqual((rating.stars, rating.review), (5, "grew on me"))
        # only the first rating notifies the lender
        self.assertEqual(M.UserNotification.objects.filter(subject="New item rating").count(), 1)

    def test_lender_cannot_rate(self):
        self.assertFalse(services.can_rate(self.lender, self.item))

    def test_average_and_count(self):
        self.assertIsNone(self.item.get_average_rating())
        self.assertEqual(self.item.get_rating_count(), 0)
        sam = make_borrower("sam")
        borrow(self.borrower, self.item)
        borrow(sam, self.item)
        services.rate_item(self.borrower, self.item, 5)
        services.rate_item(sam, self.item, 2)
        self.assertEqual(self.item.get_average_rating(), 3.5)
        self.assertEqual(self.item.get_rating_count(), 2)

    def test_stars_display(self):
        borrow(self.borrower, self.item)
        rating = services.rate_item(self.borrower, self.item, 3)
        self.assertEqual(rating.get_stars_display(), "★★★☆☆")


class RatingViewTests(TestCase):
    def setUp(self):
        self.lender, self.borrower = make_lender(), make_borrower()
        self.item = make_item(self.lender)
        self.url = reverse("rate-item", args=[self.item.pk])

    def test_requires_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_eligible_borrower_sees_form_and_can_submit(self):
        borrow(self.borrower, self.item)
        self.client.login(username="bob", password=PW)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Submit rating")
        resp = self.client.post(self.url, {"stars": "4", "review": "Fun"})
        self.assertRedirects(resp, self.url)
        self.assertEqual(M.ItemRating.objects.get().stars, 4)

    def test_existing_rating_prefills_form(self):
        borrow(self.borrower, self.item)
        services.rate_item(self.borrower, self.item, 2, "old review")
        self.client.login(username="bob", password=PW)
        resp = self.client.get(self.url)
        self.assertContains(resp, "Update rating")
        self.assertContains(resp, "old review")

    def test_ineligible_borrower_gets_error_message(self):
        self.client.login(username="bob", password=PW)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Submit rating")
        resp = self.client.post(self.url, {"stars": "5"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "You can only rate items that you have borrowed and returned.")
        self.assertEqual(M.ItemRating.objects.count(), 0)

    def test_invalid_stars_rejected(self):
        borrow(self.borrower, self.item)
        self.client.login(username="bob", password=PW)
        resp = self.client.post(self.url, {"stars": "9"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(M.ItemRating.objects.count(), 0)

    def test_owner_lender_can_view_but_not_post(self):
        borrow(self.borrower, self.item)
        services.rate_item(self.borrower, self.item, 5, "Loved it")
        self.client.login(username="lena", password=PW)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Loved it")
        self.assertNotContains(resp, "Submit rating")
        self.assertEqual(self.client.post(self.url, {"stars": "1"}).status_code, 403)
        self.assertEqual(M.ItemRating.objects.get().stars, 5)

    def test_other_lender_forbidden(self):
        make_lender("otto")
        self.client.login(username="otto", password=PW)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_hidden_item_forbidden_for_borrower(self):
        self.item.is_visible = False
        self.item.save()
        self.client.login(username="bob", password=PW)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_item_page_shows_average_and_rate_link(self):
        borrow(self.borrower, self.item)
        services.rate_item(self.borrower, self.item, 4)
        self.client.login(username="bob", password=PW)
        resp = self.client.get(reverse("view-item", args=[self.item.pk]))
        self.assertContains(resp, "4.0 / 5")
        self.assertContains(resp, "Rate this Item")
