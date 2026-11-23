"""Observer pattern tests (Smit): borrowers with an item on their wishlist are
notified when it becomes borrowed and when it becomes available again."""
from datetime import date, timedelta

from django.test import TestCase

import sclibrary.models as M
from sclibrary import services
from sclibrary.tests.tests import make_borrower, make_item, make_lender


class WishlistObserverTests(TestCase):
    def setUp(self):
        self.lender = make_lender()
        self.item = make_item(self.lender)
        self.requester = make_borrower("bob")
        self.watcher = make_borrower("wendy")
        self.other = make_borrower("olly")
        M.BorrowerWishList.objects.create(borrower=self.watcher, item=self.item)
        self.req = services.create_request(
            self.requester, self.item, date.today() + timedelta(days=1), date.today() + timedelta(days=14))

    def subjects(self, borrower):
        return list(M.UserNotification.objects.filter(recipient=borrower).values_list("subject", flat=True))

    def test_item_is_borrowed_property(self):
        self.assertFalse(self.item.is_borrowed)
        services.accept_request(self.req)
        self.assertTrue(self.item.is_borrowed)
        services.mark_returned(self.req)
        self.assertFalse(self.item.is_borrowed)

    def test_wishlister_notified_when_item_is_borrowed(self):
        services.accept_request(self.req)
        self.assertIn("Wishlist item unavailable", self.subjects(self.watcher))

    def test_wishlister_notified_when_item_is_returned(self):
        services.accept_request(self.req)
        services.mark_returned(self.req)
        self.assertIn("Wishlist item available", self.subjects(self.watcher))

    def test_only_wishlisters_are_notified(self):
        services.accept_request(self.req)
        services.mark_returned(self.req)
        self.assertNotIn("Wishlist item available", self.subjects(self.other))
        self.assertNotIn("Wishlist item unavailable", self.subjects(self.other))

    def test_borrower_of_the_item_is_not_notified_about_their_own_loan(self):
        M.BorrowerWishList.objects.create(borrower=self.requester, item=self.item)
        services.accept_request(self.req)
        services.mark_returned(self.req)
        self.assertNotIn("Wishlist item unavailable", self.subjects(self.requester))
        self.assertNotIn("Wishlist item available", self.subjects(self.requester))

    def test_removed_from_wishlist_means_no_notification(self):
        M.BorrowerWishList.objects.filter(borrower=self.watcher).delete()
        services.accept_request(self.req)
        self.assertNotIn("Wishlist item unavailable", self.subjects(self.watcher))
