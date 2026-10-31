from django.test import TestCase
from django.urls import reverse

from sclibrary.tests import make_lender, make_item


class ItemPermissionTests(TestCase):

    def setUp(self):
        self.owner = make_lender("owner")
        self.other_lender = make_lender("other")
        self.item = make_item(self.owner)

    def test_other_lender_cannot_edit_item(self):
        self.client.force_login(self.other_lender)

        url = reverse("edit-item", args=[self.item.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_owner_can_edit_item(self):
        self.client.force_login(self.owner)

        url = reverse("edit-item", args=[self.item.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_other_lender_cannot_delete_item(self):
        self.client.force_login(self.other_lender)

        url = reverse("delete-item", args=[self.item.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_owner_can_open_delete_page(self):
        self.client.force_login(self.owner)

        url = reverse("delete-item", args=[self.item.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_other_lender_cannot_submit_edit(self):
        self.client.force_login(self.other_lender)

        url = reverse("edit-item", args=[self.item.pk])

        response = self.client.post(url, {
            "condition": "Damaged",
            "description": "Changed by another lender",
            "notes": "Unauthorized edit",
            "is_visible": "on"
        })

        self.assertEqual(response.status_code, 404)

        self.item.refresh_from_db()
        self.assertEqual(self.item.condition, "Good")
        self.assertEqual(self.item.description, "d")

    def test_other_lender_cannot_submit_delete(self):
        self.client.force_login(self.other_lender)

        url = reverse("delete-item", args=[self.item.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            self.item.__class__.objects.filter(pk=self.item.pk).exists()
        )

    def test_owner_can_submit_edit(self):
        self.client.force_login(self.owner)

        url = reverse("edit-item", args=[self.item.pk])

        response = self.client.post(url, {
            "condition": "Like New",
            "description": "Updated by the owner",
            "notes": "Owner updated this item",
            "is_visible": "on"
        })

        self.assertEqual(response.status_code, 302)

        self.item.refresh_from_db()
        self.assertEqual(self.item.condition, "Like New")
        self.assertEqual(self.item.description, "Updated by the owner")

    def test_owner_can_submit_delete(self):
        self.client.force_login(self.owner)

        url = reverse("delete-item", args=[self.item.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            self.item.__class__.objects.filter(pk=self.item.pk).exists()
        )