from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
import sclibrary.models as SCLibraryModels
from sclibrary.forms.items import createNewItem, editItem, DeleteItem
from django.shortcuts import redirect, render

LENDER = SCLibraryModels.UserAccount.Types.LENDER


@login_required
def create_item(request: HttpRequest):
    if request.user.user_type != LENDER:
        return error_borrower_attempted_to_access_lender_only_page(request)

    if request.method == "POST":
        form = createNewItem(request.GET.get("type"))(request.POST)
        if form.is_valid():
            item = form.save(request)
            return redirect(item.get_absolute_url())
    else:
        form = createNewItem(request.GET.get("type"))
    return render(request, "sclibrary/item_form.html", {"form": form, "item_types": list(map(lambda type : type.lower(), SCLibraryModels.Item.Types))})

@login_required
def edit_item(request: HttpRequest, item_pk: int):
    if (request.user.user_type != LENDER):
            return error_borrower_attempted_to_access_lender_only_page(request)
    return editItem(item_pk)(request, pk=item_pk)

@login_required
def delete_item(request: HttpRequest, item_pk: int):
    if (request.user.user_type != LENDER):
            return error_borrower_attempted_to_access_lender_only_page(request)
    return DeleteItem.as_view()(request, pk=item_pk)


def error_borrower_attempted_to_access_lender_only_page(request: HttpRequest):
    return HttpResponseForbidden("Only Lenders are allowed to access this page.")
