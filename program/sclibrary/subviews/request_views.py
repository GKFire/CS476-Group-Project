"""Requests + notifications views (lender workflow, borrower request list).

Wire-up (urls.py) is documented in CONTRIBUTION_NOTES.md.
"""
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

import sclibrary.models as M
from sclibrary import services

LENDER = M.UserAccount.Types.LENDER
BORROWER = M.UserAccount.Types.BORROWER


def _forbidden():
    return HttpResponseForbidden("Your account type does not allow you to access this page")


def _can_see_request(user, req: M.BorrowRequest) -> bool:
    if user.user_type == LENDER:
        return req.item.library.owner_id == user.pk
    if user.user_type == BORROWER:
        return req.borrower_id == user.pk
    return False


class ReturnDateForm(forms.Form):
    return_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


@login_required
def request_list(request: HttpRequest):
    """Lender: requests on items they own. Borrower: their own requests."""
    status = request.GET.get("status", "")
    if request.user.user_type == LENDER:
        qs = M.BorrowRequest.objects.filter(item__library__owner_id=request.user.pk)
    elif request.user.user_type == BORROWER:
        qs = M.BorrowRequest.objects.filter(borrower_id=request.user.pk)
    else:
        return _forbidden()
    if status in {"RQ", "AC", "RJ", "CD"}:
        qs = qs.filter(status=status)
    qs = qs.select_related("item", "borrower").order_by("-start_date")
    overdue_ids = set(services.overdue_requests().filter(pk__in=qs.values("pk")).values_list("pk", flat=True))
    return render(request, "sclibrary/request_list.html", {
        "requests": qs, "status": status, "overdue_ids": overdue_ids,
        "is_lender": request.user.user_type == LENDER,
    })


@login_required
def request_detail(request: HttpRequest, request_pk: int):
    req = get_object_or_404(M.BorrowRequest.objects.select_related("item", "borrower"), pk=request_pk)
    if not _can_see_request(request.user, req):
        return _forbidden()
    return render(request, "sclibrary/request_detail.html", {
        "req": req, "form": ReturnDateForm(initial={"return_date": req.return_date}),
        "is_lender": request.user.user_type == LENDER,
        "overdue": req.pk in set(services.overdue_requests().values_list("pk", flat=True)),
    })


@login_required
@require_POST
def request_decision(request: HttpRequest, request_pk: int):
    """Lender only. POST action=accept|decline|returned (+ optional return_date)."""
    if request.user.user_type != LENDER:
        return _forbidden()
    req = get_object_or_404(M.BorrowRequest, pk=request_pk)
    if not _can_see_request(request.user, req):
        return _forbidden()
    action = request.POST.get("action")
    form = ReturnDateForm(request.POST)
    try:
        if action == "accept":
            services.accept_request(req, form.cleaned_data.get("return_date") if form.is_valid() else None)
            messages.success(request, "Request accepted.")
        elif action == "decline":
            services.decline_request(req)
            messages.success(request, "Request declined.")
        elif action == "returned":
            services.mark_returned(req)
            messages.success(request, "Item marked as returned.")
        else:
            messages.error(request, "Unknown action.")
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
    return redirect("view-request", request_pk=req.pk)


@login_required
@require_POST
def toggle_item_visibility(request: HttpRequest, item_pk: int):
    """Lender only: mark an item available/unavailable (is_visible)."""
    if request.user.user_type != LENDER:
        return _forbidden()
    item = get_object_or_404(M.Item, pk=item_pk, library__owner_id=request.user.pk)
    try:
        services.set_item_visibility(item, not item.is_visible)
        messages.success(request, f"\"{item.title}\" is now {'available' if item.is_visible else 'hidden'}.")
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
    return redirect("view-item", item_pk=item.pk)


def _notif_qs(user):
    if user.user_type == LENDER:
        return M.LenderNotification.objects.filter(recipient_id=user.pk)
    if user.user_type == BORROWER:
        return M.BorrowerNotification.objects.filter(recipient_id=user.pk)
    return None


@login_required
def notifications_list(request: HttpRequest):
    qs = _notif_qs(request.user)
    if qs is None:
        return _forbidden()
    return render(request, "sclibrary/notifications.html", {"notifications": qs.order_by("-timestamp")})


@login_required
@require_POST
def notifications_mark_read(request: HttpRequest):
    qs = _notif_qs(request.user)
    if qs is None:
        return _forbidden()
    qs.filter(has_viewed=False).update(has_viewed=True)
    return redirect("view-notifications")
