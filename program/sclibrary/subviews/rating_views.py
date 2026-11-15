"""Rate an Item view (dopedgod).

Borrowers who have borrowed and returned an item can rate/review it (re-submitting
updates their rating). The lender who owns the item can only view ratings.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

import sclibrary.models as M
from sclibrary import services
from sclibrary.forms.rating import RatingForm

LENDER = M.UserAccount.Types.LENDER
BORROWER = M.UserAccount.Types.BORROWER


@login_required
def rate_item(request: HttpRequest, item_pk: int):
    item = get_object_or_404(M.Item, pk=item_pk)
    user = request.user

    # Same visibility rules as the item page.
    if user.user_type == LENDER and item.library.owner_id != user.pk:
        return HttpResponseForbidden("You are not the owner of this item, and thus are not allowed to view it")
    if user.user_type == BORROWER and not item.is_visible:
        return HttpResponseForbidden("This item has been hidden by it's owner")

    is_borrower = user.user_type == BORROWER
    existing = M.ItemRating.objects.filter(borrower_id=user.pk, item=item).first() if is_borrower else None

    if request.method == "POST":
        if not is_borrower:
            return HttpResponseForbidden("Only borrowers can rate items.")
        form = RatingForm(request.POST)
        if form.is_valid():
            try:
                services.rate_item(user.borrower, item,
                                   form.cleaned_data["stars"], form.cleaned_data["review"])
                messages.success(request, "Your rating has been saved.")
                return redirect("rate-item", item_pk=item.pk)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        initial = {"stars": existing.stars, "review": existing.review} if existing else None
        form = RatingForm(initial=initial)

    return render(request, "sclibrary/item_rating.html", {
        "item": item,
        "form": form,
        "can_rate": services.can_rate(user, item),
        "is_borrower": is_borrower,
        "existing": existing,
        "ratings": M.ItemRating.objects.filter(item=item).select_related("borrower"),
    })
