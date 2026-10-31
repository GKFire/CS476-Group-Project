from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
import sclibrary.models as SCLibraryModels
from sclibrary.forms.items import CreateItem
from django.shortcuts import get_object_or_404, redirect, render


@login_required
def create_item(request: HttpRequest):
    if request.user.user_type != SCLibraryModels.UserAccount.Types.LENDER:
        return HttpResponseForbidden("Only Lenders are able to create items")

    if request.method == "POST":
        form = CreateItem(request.POST)
        if form.is_valid():
            item = form.save(request)
            return redirect(item.get_absolute_url())
    else:
        form = CreateItem()
    return render(request, "sclibrary/item_form.html", {"form": form})