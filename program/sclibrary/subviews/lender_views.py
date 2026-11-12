from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
import sclibrary.models as SCLibraryModels
from sclibrary.forms.items import DeleteItem, getBorrowHistory
from sclibrary.forms.library import ChangeLibrary
from django.shortcuts import redirect, render

from django.apps import apps

LENDER = SCLibraryModels.UserAccount.Types.LENDER
sclibraryconfig = apps.get_app_config("sclibrary")

@login_required
def create_item(request: HttpRequest):
    if request.user.user_type != LENDER:
        return error_borrower_attempted_to_access_lender_only_page(request)

    if request.method == "POST":
        form = sclibraryconfig.item_factory.createNewItem(request.GET.get("type"))(request.POST)
        if form.is_valid():
            item = form.save(request)
            return redirect(item.get_absolute_url())
    else:
        form = sclibraryconfig.item_factory.createNewItem(request.GET.get("type"))
    return render(request, "sclibrary/item_form.html", {"form": form, "item_types": list(map(lambda type : type.lower(), SCLibraryModels.Item.Types))})

@login_required
def edit_item(request: HttpRequest, item_pk: int):
    if (request.user.user_type != LENDER):
        return error_borrower_attempted_to_access_lender_only_page(request)
    return sclibraryconfig.item_factory.editItem(item_pk).as_view()(request, pk=item_pk)

@login_required
def delete_item(request: HttpRequest, item_pk: int):
    if (request.user.user_type != LENDER):
        return error_borrower_attempted_to_access_lender_only_page(request)
    return DeleteItem.as_view()(request, pk=item_pk)

@login_required
def viewBorrower(request: HttpRequest, user_pk: int):
    if request.user.user_type != LENDER:
         return error_borrower_attempted_to_access_lender_only_page(request)
    borrow_history = getBorrowHistory(user_pk, request.user.lender.library.id)
    if not borrow_history:
        return render(request, "sclibrary/user_view.html", {"invalid": True})
    borrow_history["ongoing"] = list(map(lambda borrowrequest: (borrowrequest, sclibraryconfig.item_factory.getProperItem(borrowrequest.item)), borrow_history["ongoing"]))
    borrow_history["previous"] = list(map(lambda borrowrequest: (borrowrequest, sclibraryconfig.item_factory.getProperItem(borrowrequest.item)), borrow_history["previous"]))
    return render(request, "sclibrary/user_view.html", {"borrower": SCLibraryModels.Borrower.objects.get(id=user_pk), "borrow_history": borrow_history})

def error_borrower_attempted_to_access_lender_only_page(request: HttpRequest):
    return HttpResponseForbidden("Only Lenders are allowed to access this page.")

@login_required
def change_library(request: HttpRequest):
    if (request.user.user_type != LENDER):
        return error_borrower_attempted_to_access_lender_only_page(request)
    return ChangeLibrary.as_view()(request, pk=request.user.lender.library.id)