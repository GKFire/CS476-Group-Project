
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
        loan_1 = self.create_loan("AC")
        loan_2 = self.create_loan("AC")

        response = self.client.get(self.url, headers={"status": "AC"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["requests"].count(), 2)
        self.assertEqual(response.context["requests"].first(), loan_1)
        self.assertEqual(response.context["requests"][1], loan_2)
        self.assertContains(response, "Mario Kart")

    def test_borrowing_history(self):
        loan = self.create_loan("CD")

        response = self.client.get(self.url, query_params={"status": "CD"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["requests"].count(), 1)
        self.assertEqual(response.context["requests"].first(), loan)

    def test_pending_and_rejected_requests(self):
        loan_1 = self.create_loan("RQ")
        loan_2 = self.create_loan("RJ")

        response_active = self.client.get(self.url, query_params={"status": "AC"})
        self.assertEqual(response_active.context["requests"].count(), 0)

        response_concluded = self.client.get(self.url, query_params={"status": "CD"})
        self.assertEqual(response_concluded.context["requests"].count(), 0)

        response_requested = self.client.get(self.url, query_params={"status": "RQ"})
        self.assertEqual(response_requested.context["requests"].count(), 1)
        self.assertEqual(response_requested.context["requests"].first(), loan_1)

        response_rejected = self.client.get(self.url, query_params={"status": "RJ"})
        self.assertEqual(response_rejected.context["requests"].count(), 1)
        self.assertEqual(response_rejected.context["requests"].first(), loan_2)


    def test_borrower_sees_only_own_loans(self):
        other_item = make_item(self.lender, "Minecraft")

        self.create_loan("AC")
        self.create_loan("AC", self.other_borrower, other_item)

        response = self.client.get(self.url, query_params={"status": "AC"})

        self.assertContains(response, "Mario Kart")
        self.assertNotContains(response, "Minecraft")
        self.assertEqual(response.context["requests"].count(), 1)

    def test_empty_profile(self):
        response = self.client.get(self.url, query_params={"status": "RQ"})
        self.assertContains(response, "No requests.")

        response = self.client.get(self.url, query_params={"status": "AC"})
        self.assertContains(response, "No requests.")

        response = self.client.get(self.url, query_params={"status": "CD"})
        self.assertContains(response, "No requests.")

        response = self.client.get(self.url, query_params={"status": "RJ"})
        self.assertContains(response, "No requests.")

    def test_lender_profile_unchanged(self):
        self.client.force_login(self.lender)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "My Borrower Profile")

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
