"""Business rules for the borrow-request lifecycle (RQ -> AC -> CD, or RQ -> RJ).

Kept out of the views so it is easy to unit test and to reuse from Smit's
borrower-side "send request" view.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

import sclibrary.models as M
from sclibrary import notifications


def item_is_on_loan(item: M.Item) -> bool:
    return item.borrowrequest_set.filter(status="AC").exists()


def validate_dates(start_date, return_date):
    if return_date < start_date:
        raise ValidationError("The return date cannot be before the borrowing start date.")


@transaction.atomic
def create_request(borrower: M.Borrower, item: M.Item, start_date, return_date) -> M.BorrowRequest:
    """Borrower-side entry point (Smit can call this from sendBorrowRequest)."""
    if not item.is_visible:
        raise ValidationError("This item is not available to borrow.")
    if item_is_on_loan(item):
        raise ValidationError("This item is already being borrowed.")
    validate_dates(start_date, return_date)
    req = M.BorrowRequest.objects.create(
        borrower=borrower, item=item, start_date=start_date,
        return_date=return_date, status="RQ",
    )
    notifications.notify_lender_new_request(req)
    return req


@transaction.atomic
def accept_request(req: M.BorrowRequest, return_date=None) -> M.BorrowRequest:
    if req.status != "RQ":
        raise ValidationError("Only pending requests can be accepted.")
    if item_is_on_loan(req.item):
        raise ValidationError("This item is already on loan.")
    if return_date is not None:
        req.return_date = return_date
    validate_dates(req.start_date, req.return_date)
    req.status = "AC"
    req.save()
    # any other pending requests for the same item can no longer be fulfilled
    for other in req.item.borrowrequest_set.filter(status="RQ").exclude(pk=req.pk):
        other.status = "RJ"
        other.save()
        notifications.notify_borrower_decision(other, accepted=False)
    notifications.notify_borrower_decision(req, accepted=True)
    return req


@transaction.atomic
def decline_request(req: M.BorrowRequest) -> M.BorrowRequest:
    if req.status != "RQ":
        raise ValidationError("Only pending requests can be declined.")
    req.status = "RJ"
    req.save()
    notifications.notify_borrower_decision(req, accepted=False)
    return req


@transaction.atomic
def mark_returned(req: M.BorrowRequest) -> M.BorrowRequest:
    if req.status != "AC":
        raise ValidationError("Only active loans can be marked as returned.")
    req.status = "CD"
    req.save()
    notifications.notify_borrower_returned(req)
    return req


def overdue_requests():
    return M.BorrowRequest.objects.filter(status="AC", return_date__lt=timezone.localdate())


def set_item_visibility(item: M.Item, visible: bool):
    """Mark item (un)available. Hiding an item that is on loan is an error (spec)."""
    if not visible and item_is_on_loan(item):
        raise ValidationError("You cannot hide an item while it is currently on loan.")
    item.is_visible = visible
    item.save()
