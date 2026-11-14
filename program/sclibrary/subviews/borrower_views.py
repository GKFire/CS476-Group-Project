"""Register and Send Borrow Request views (Smit).

Kept in their own module, like request_views.py, so they don't collide with
edits to views.py.
"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

import sclibrary.models as M
from sclibrary import services
from sclibrary.forms.request import BorrowRequestForm
from django.apps import apps

from sclibrary.forms.items import get_searchset, getBorrowHistory

BORROWER = M.UserAccount.Types.BORROWER
sclibraryconfig = apps.get_app_config("sclibrary")

@login_required
def search(request: HttpRequest):
    if request.user.user_type != BORROWER:
        return HttpResponseForbidden("Only borrowers can access the search.")
    library = None
    if request.GET.get("library") != None:
        library = int(request.GET.get("library"))
    return render(request, "sclibrary/page_search.html", {"item_list": sclibraryconfig.item_factory.getProperItems(get_searchset(request)), "library": M.Library.objects.filter(id=library).first(), "libraries": M.Library.objects.all(), "type_list": M.Item.Types})


@login_required
def send_borrow_request(request: HttpRequest, item_pk: int):
    if request.user.user_type != BORROWER:
        return HttpResponseForbidden("Only borrowers can send borrow requests.")
    item = get_object_or_404(M.Item, pk=item_pk)
    if not item.is_visible:
        return HttpResponseForbidden("This item has been hidden by its owner.")

    if request.method == "POST":
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            try:
                services.create_request(
                    request.user.borrower, item,
                    form.cleaned_data["start_date"], form.cleaned_data["return_date"],
                )
                return redirect("myprofile-requests")
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = BorrowRequestForm()
    return render(request, "sclibrary/request_form.html", {"form": form, "item": item})

@login_required
def viewLender(request: HttpRequest, user_pk: int):
    lender = M.Lender.objects.get(id=user_pk)
    if not lender:
        return render(request, "sclibrary/user_view.html", {"invalid": True})
    borrow_history = getBorrowHistory(request.user.id, lender.library.id)
    borrow_history["ongoing"] = list(map(lambda borrowrequest: (borrowrequest, sclibraryconfig.item_factory.getProperItem(borrowrequest.item)), borrow_history["ongoing"]))
    borrow_history["previous"] = list(map(lambda borrowrequest: (borrowrequest, sclibraryconfig.item_factory.getProperItem(borrowrequest.item)), borrow_history["previous"]))
    return render(request, "sclibrary/user_view.html", {"lender": lender, "borrow_history": borrow_history})
