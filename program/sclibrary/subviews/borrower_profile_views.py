from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

import sclibrary.models as M


@login_required
def borrower_profile(request):
    if request.user.user_type != M.UserAccount.Types.BORROWER:
        return HttpResponseForbidden("Only borrowers can view this page.")

    active_loans = M.BorrowRequest.objects.filter(
        borrower_id=request.user.pk,
        status="AC"
    ).select_related("item", "item__library").order_by("-start_date")

    borrowing_history = M.BorrowRequest.objects.filter(
        borrower_id=request.user.pk,
        status="CD"
    ).select_related("item", "item__library").order_by("-start_date")

    return render(request, "sclibrary/page_borrower_profile.html", {
        "active_loans": active_loans,
        "borrowing_history": borrowing_history
    })