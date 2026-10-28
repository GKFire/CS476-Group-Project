"""Register and Send Borrow Request views (Smit).

Kept in their own module, like request_views.py, so they don't collide with
edits to views.py.
"""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

import sclibrary.models as M
from sclibrary import services
from sclibrary.forms.request import BorrowRequestForm
from sclibrary.forms.user import RegisterForm

BORROWER = M.UserAccount.Types.BORROWER


def register(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "sclibrary/page_register.html", {"form": form})


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


def logout_view(request: HttpRequest):
    """Sign out from a normal link. Django 5+ LogoutView only accepts POST,
    which made the top bar's "Sign out" link return HTTP 405."""
    logout(request)
    return redirect("index")
