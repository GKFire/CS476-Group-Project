"""Helpers for creating notifications so views never build them by hand."""
from urllib import request

import sclibrary.models as M
import sclibrary.views as V


def notify_lender_new_request(req: M.BorrowRequest):
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=req.item.library.owner.id),
        subject="New borrow request",
        description=(f"{req.borrower.username if req.borrower else 'A user'} wants to borrow "
                     f"\"{req.item.title}\" from {req.start_date} to {req.return_date}."),
    )


def notify_borrower_decision(req: M.BorrowRequest, accepted: bool):
    if req.borrower is None:
        return
    verb = "accepted" if accepted else "declined"
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=req.borrower.id),
        subject=f"Request {verb}",
        description=f"Your request for \"{req.item.title}\" was {verb}. Return date: {req.return_date}.",
    )


def notify_borrower_returned(req: M.BorrowRequest):
    if req.borrower is None:
        return
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=req.borrower.id),
        subject="Item marked returned",
        description=f"\"{req.item.title}\" was marked as returned. Thanks!",
    )


def notify_overdue(req: M.BorrowRequest):
    """Overdue notice to both sides."""
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=req.item.library.owner.id),
        subject="Item overdue",
        description=f"\"{req.item.title}\" was due {req.return_date} and has not been returned.",
    )
    if req.borrower is not None:
        M.UserNotification.objects.create(
            recipient=M.UserAccount.objects.get(id=req.borrower.id),
            subject="Item overdue",
            description=f"\"{req.item.title}\" was due {req.return_date}. Please return it.",
        )

def notify_wishlist_available(wishlist_item: M.Item, user: M.Borrower):
    """Notifies the user that a wishlist item is now available."""
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=user.id),
        subject="Wishlist item available",
        description=f"\"{wishlist_item.title}\" is now available for borrowing!",
    )

def notify_wishlist_unavailable(wishlist_item: M.Item, user: M.Borrower):
    """Notifies the user that a wishlist item is no longer available."""
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=user.id),
        subject="Wishlist item unavailable",
        description=f"\"{wishlist_item.title}\" is now unavailable!",
    )


def notify_lender_new_rating(rating: M.ItemRating):
    M.UserNotification.objects.create(
        recipient=M.UserAccount.objects.get(id=rating.item.library.owner.id),
        subject="New item rating",
        description=f"{rating.borrower.username} rated \"{rating.item.title}\" {rating.stars}/5.",
    )

def notify_username_change(user: M.Lender | M.Borrower):
    """Notifies the user that their username has been changed."""
    M.UserNotification.objects.create(
        recipient=user,
        subject="Username changed",                 
        description=f"Your username has been changed to \"{user.username}\".",  # Lets the user know their new username
    )
    """Sends an email to the user letting them know that their username has been changed."""
    V.send_email(
        subject="Username changed",
        recipient=user.email,
        template="sclibrary/change_username_email.html",  # Emails HTML content of "change_username_email.html", which is defined in templates, to the user
        context={"user": user},  # For specifically addressing the user in the email  
    )

def notify_password_change(user: M.Lender | M.Borrower):
    """Notifies the user that their password has been changed."""
    M.UserNotification.objects.create(
        recipient=user,
        subject="Password changed",
        description=f"Your password has been changed.",
    )
    """Sends an email to the user letting them know that their password has been changed."""
    V.send_email(
        subject="Password changed",
        recipient=user.email,
        template="sclibrary/change_password_email.html",
        context={"user": user},
    )

def notify_email_change(user: M.Lender | M.Borrower):
    """Notifies the user that their email has been changed."""
    M.UserNotification.objects.create(
        recipient=user,
        subject="Email changed",
        description=f"Your email has been changed to \"{user.email}\".",
    )
    """Sends an email to the user letting them know that their email has been changed."""
    V.send_email(
        subject="Email changed",
        recipient=user.email,
        template="sclibrary/change_email_email.html",
        context={"user": user},
    )