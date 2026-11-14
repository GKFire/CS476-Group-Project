
from django.test import TestCase
from django.urls import reverse

from sclibrary.models import BorrowerWishList
from sclibrary.tests.tests import make_borrower, make_lender, make_item


class WishlistTests(TestCase):

    def setUp(self):
        self.borrower = make_borrower("wishlist_bob")
        self.other_borrower = make_borrower("wishlist_alice")
        self.lender = make_lender("wishlist_lena")
        self.item = make_item(self.lender, "Mario Kart")
        self.add_url = reverse("add-to-wishlist")
        self.remove_url = reverse("remove-from-wishlist")
        self.list_url = reverse("view-wishlist")
        self.client.force_login(self.borrower)

    def test_add_item(self):
        response = self.client.post(
            self.add_url,
            {"item_id": self.item.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            BorrowerWishList.objects.filter(
                borrower=self.borrower,
                item=self.item
            ).exists()
        )

    def test_duplicate_item(self):
        self.client.post(self.add_url, {"item_id": self.item.pk})
        self.client.post(self.add_url, {"item_id": self.item.pk})

        count = BorrowerWishList.objects.filter(
            borrower=self.borrower,
            item=self.item
        ).count()

        self.assertEqual(count, 1)

    def test_remove_item(self):
        BorrowerWishList.objects.create(
            borrower=self.borrower,
            item=self.item
        )

        response = self.client.post(
            self.remove_url,
            {"item_id": self.item.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            BorrowerWishList.objects.filter(
                borrower=self.borrower,
                item=self.item
            ).exists()
        )

    def test_cannot_remove_another_borrowers_item(self):
        BorrowerWishList.objects.create(
            borrower=self.other_borrower,
            item=self.item
        )

        self.client.post(
            self.remove_url,
            {"item_id": self.item.pk}
        )

        self.assertTrue(
            BorrowerWishList.objects.filter(
                borrower=self.other_borrower,
                item=self.item
            ).exists()
        )

    def test_borrower_sees_only_own_wishlist(self):
        other_item = make_item(self.lender, "Minecraft")

        BorrowerWishList.objects.create(
            borrower=self.borrower,
            item=self.item
        )

        BorrowerWishList.objects.create(
            borrower=self.other_borrower,
            item=other_item
        )

        response = self.client.get(self.list_url)
        saved_items = response.context["saved_items"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(saved_items.count(), 1)
        self.assertEqual(
            saved_items.first().item_id,
            self.item.pk
        )

    def test_lender_cannot_use_wishlist(self):
        self.client.force_login(self.lender)

        self.assertEqual(
            self.client.get(self.list_url).status_code, 403
        )
        self.assertEqual(
            self.client.post(
                self.add_url,
                {"item_id": self.item.pk}
            ).status_code, 403
        )
        self.assertEqual(
            self.client.post(
                self.remove_url,
                {"item_id": self.item.pk}
            ).status_code, 403
        )

    def test_invalid_item_id(self):
        self.assertEqual(
            self.client.post(
                self.add_url,
                {"item_id": "abc"}
            ).status_code, 400
        )
        self.assertEqual(
            self.client.post(
                self.remove_url,
                {"item_id": "abc"}
            ).status_code, 400
        )

    def test_cannot_add_hidden_item(self):
        self.item.is_visible = False
        self.item.save()

        response = self.client.post(
            self.add_url,
            {"item_id": self.item.pk}
        )

        self.assertEqual(response.status_code, 404)

    def test_can_remove_hidden_item(self):
        BorrowerWishList.objects.create(
            borrower=self.borrower,
            item=self.item
        )

        self.item.is_visible = False
        self.item.save()

        response = self.client.post(
            self.remove_url,
            {"item_id": self.item.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            BorrowerWishList.objects.filter(
                borrower=self.borrower,
                item=self.item
            ).exists()
        )

    def test_add_remove_require_post(self):
        self.assertEqual(
            self.client.get(self.add_url).status_code, 405
        )
        self.assertEqual(
            self.client.get(self.remove_url).status_code, 405
        )

    def test_login_required(self):
        self.client.logout()

        self.assertEqual(
            self.client.get(self.list_url).status_code, 302
        )
        self.assertEqual(
            self.client.post(
                self.add_url,
                {"item_id": self.item.pk}
            ).status_code, 302
        )
