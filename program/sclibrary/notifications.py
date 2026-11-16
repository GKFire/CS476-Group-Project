"""Helpers for creating notifications so views never build them by hand."""
from urllib import request

import sclibrary.models as M


def notify_lender_new_request(req: M.BorrowRequest):
    M.LenderNotification.objects.create(
        recipient=req.item.library.owner,
        subject="New borrow request",
        description=(f"{req.borrower.username if req.borrower else 'A user'} wants to borrow "
                     f"\"{req.item.title}\" from {req.start_date} to {req.return_date}."),
    )


def notify_borrower_decision(req: M.BorrowRequest, accepted: bool):
    if req.borrower is None:
        return
    verb = "accepted" if accepted else "declined"
    M.BorrowerNotification.objects.create(
        recipient=req.borrower,
        subject=f"Request {verb}",
        description=f"Your request for \"{req.item.title}\" was {verb}. Return date: {req.return_date}.",
    )


def notify_borrower_returned(req: M.BorrowRequest):
    if req.borrower is None:
        return
    M.BorrowerNotification.objects.create(
        recipient=req.borrower,
        subject="Item marked returned",
        description=f"\"{req.item.title}\" was marked as returned. Thanks!",
    )


def notify_overdue(req: M.BorrowRequest):
    """Overdue notice to both sides."""
    M.LenderNotification.objects.create(
        recipient=req.item.library.owner,
        subject="Item overdue",
        description=f"\"{req.item.title}\" was due {req.return_date} and has not been returned.",
    )
    if req.borrower is not None:
        M.BorrowerNotification.objects.create(
            recipient=req.borrower,
            subject="Item overdue",
            description=f"\"{req.item.title}\" was due {req.return_date}. Please return it.",
        )

def notify_wishlist_available(wishlist_item: M.Item, user: M.Borrower):
    """Notify the user that a wishlist item is now available."""
    M.BorrowerNotification.objects.create(
        recipient=user,
        subject="Wishlist item available",
        description=f"\"{wishlist_item.title}\" is now available for borrowing!",
    )

def notify_wishlist_unavailable(wishlist_item: M.Item, user: M.Borrower):
    """Notify the user that a wishlist item is no longer available."""
    M.BorrowerNotification.objects.create(
        recipient=user,
        subject="Wishlist item unavailable",
        description=f"\"{wishlist_item.title}\" is now unavailable!",
    )


def notify_lender_new_rating(rating: M.ItemRating):
    M.LenderNotification.objects.create(
        recipient=rating.item.library.owner,
        subject="New item rating",
        description=f"{rating.borrower.username} rated \"{rating.item.title}\" {rating.stars}/5.",
    )

def notify_username_change(user: M.Lender | M.Borrower):
    """Notify the user that their username has been changed."""
    M.UserNotification.objects.create(
        recipient=user,
        subject="Username changed",                 
        description=f"Your username has been changed to \"{user.username}\".",
    )

def notify_password_change(user: M.Lender | M.Borrower):
    """Notify the user that their password has been changed."""
    M.UserNotification.objects.create(
        recipient=user,
        subject="Password changed",
        description=f"Your password has been changed.",
    )

def notify_email_change(user: M.Lender | M.Borrower):
    """Notify the user that their email has been changed."""
    M.UserNotification.objects.create(
        recipient=user,
        subject="Email changed",
        description=f"Your email has been changed to \"{user.email}\".",
    )