"""Helpers for creating notifications so views never build them by hand."""
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
