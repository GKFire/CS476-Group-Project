from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden

from sclibrary.models import BorrowerWishList, Item, UserAccount

@login_required
@require_POST
def add_to_wishlist(request):
    if request.user.user_type != UserAccount.Types.BORROWER:
        return HttpResponseForbidden("Only borrowers can use the Wishlist")

    item_id = request.POST.get("item_id")

    if not item_id or not item_id.isdigit():
        return HttpResponseBadRequest("Invalid item ID")

    item = get_object_or_404(Item, pk=int(item_id), is_visible=True)

    BorrowerWishList.objects.get_or_create(
        borrower_id=request.user.pk,
        item=item
    )

    return redirect("view-wishlist")