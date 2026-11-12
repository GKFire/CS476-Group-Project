
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import sclibrary.models as M
from sclibrary.tests.tests import make_borrower, make_lender, make_item


class BorrowerProfileTests(TestCase):

    def setUp(self):
        self.borrower = make_borrower("profile_bob")
        self.other_borrower = make_borrower("profile_alice")
        self.lender = make_lender("profile_lena")
        self.item = make_item(self.lender, "Mario Kart")

        self.url = reverse("myprofile-requests")
        self.client.force_login(self.borrower)

    def create_loan(self, status, borrower=None, item=None):
        return M.BorrowRequest.objects.create(
            borrower=borrower or self.borrower,
            item=item or self.item,
            start_date=date.today(),
            return_date=date.today() + timedelta(days=7),
            status=status
        )

    def test_active_loan(self):
        loan = self.create_loan("AC")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_loans"].count(), 1)
        self.assertEqual(response.context["active_loans"].first(), loan)
        self.assertContains(response, "Mario Kart")

    def test_borrowing_history(self):
        loan = self.create_loan("CD")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["borrowing_history"].count(), 1)
        self.assertEqual(response.context["borrowing_history"].first(), loan)

    def test_pending_and_rejected_requests(self):
        self.create_loan("RQ")
        self.create_loan("RJ")

        response = self.client.get(self.url)

        self.assertEqual(response.context["active_loans"].count(), 0)
        self.assertEqual(response.context["borrowing_history"].count(), 0)

    def test_borrower_sees_only_own_loans(self):
        other_item = make_item(self.lender, "Minecraft")

        self.create_loan("AC")
        self.create_loan("AC", self.other_borrower, other_item)

        response = self.client.get(self.url)

        self.assertContains(response, "Mario Kart")
        self.assertNotContains(response, "Minecraft")
        self.assertEqual(response.context["active_loans"].count(), 1)

    def test_empty_profile(self):
        response = self.client.get(self.url)

        self.assertContains(response, "You have no items currently borrowed.")
        self.assertContains(response, "No borrowing history yet.")

    def test_lender_profile_unchanged(self):
        self.client.force_login(self.lender)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "My Borrower Profile")

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
