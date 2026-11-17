"""Robustness tests (Smit): a lender cannot hide or delete an item while it is on loan."""
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import sclibrary.models as M
from sclibrary.tests.tests import make_borrower, make_item, make_lender


class OnLoanProtectionTests(TestCase):
    def setUp(self):
        self.lender = make_lender()
        self.borrower = make_borrower()
        self.item = make_item(self.lender)
        self.client.login(username="lena", password="pw12345!")

    def lend(self, status="AC"):
        return M.BorrowRequest.objects.create(
            borrower=self.borrower, item=self.item, status=status,
            start_date=date.today(), return_date=date.today() + timedelta(days=14))

    def edit(self, visible):
        data = {"condition": "Good", "description": "d", "notes": "n",
                "item_format": self.item.item_format, "age_rating": self.item.age_rating}
        if visible:
            data["is_visible"] = "on"
        return self.client.post(reverse("edit-item", args=[self.item.pk]), data)

    def test_cannot_hide_item_while_on_loan(self):
        self.lend()
        r = self.edit(visible=False)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "cannot hide this item while it is being borrowed")
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_visible)

    def test_can_still_edit_other_fields_while_on_loan(self):
        self.lend()
        self.edit(visible=True)
        self.item.refresh_from_db()
        self.assertEqual(self.item.condition, "Good")
        self.assertTrue(self.item.is_visible)

    def test_can_hide_item_when_not_on_loan(self):
        self.edit(visible=False)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_visible)

    def test_can_hide_item_after_it_is_returned(self):
        self.lend(status="CD")
        self.edit(visible=False)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_visible)

    def test_cannot_delete_item_while_on_loan(self):
        self.lend()
        r = self.client.post(reverse("delete-item", args=[self.item.pk]))
        self.assertRedirects(r, reverse("view-item", args=[self.item.pk]), fetch_redirect_response=False)
        self.assertTrue(M.Item.objects.filter(pk=self.item.pk).exists())

    def test_can_delete_item_when_not_on_loan(self):
        self.client.post(reverse("delete-item", args=[self.item.pk]))
        self.assertFalse(M.Item.objects.filter(pk=self.item.pk).exists())
