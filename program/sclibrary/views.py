from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
import sclibrary.models as SCLibraryModels
from sclibrary.forms.user import RegisterForm
from django.contrib.auth import login, logout
import sclibrary.forms.user as UserForm

from django.apps import apps

USER_TYPES = SCLibraryModels.UserAccount.Types
sclibraryconfig = apps.get_app_config("sclibrary")

# Create your views here.

def index(request: HttpRequest):
    libraries = SCLibraryModels.Library.objects.all()
    return render(request, "sclibrary/page_index.html")

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
def home(request: HttpRequest):
    if request.user.user_type == USER_TYPES.BORROWER:
        return render(request, "sclibrary/page_home.html", {"borrowing_list": list(map(lambda request: (request, sclibraryconfig.item_factory.getProperItem(request.item)), SCLibraryModels.BorrowRequest.objects.filter(status="AC",borrower=request.user.borrower)))})
    if request.user.user_type == USER_TYPES.LENDER:
        return render(request, "sclibrary/page_home.html", {"library": (request.user.lender.library.name, sclibraryconfig.item_factory.getProperItems(SCLibraryModels.Library.objects.get(owner=request.user.lender).item_set.all()))})
    libraries_buffer = SCLibraryModels.Library.objects.all()
    libraries = list(map(lambda library: (library, sclibraryconfig.item_factory.getProperItems(library.item_set.all())), libraries_buffer))
    return render(request, "sclibrary/page_home.html", {"libraries": libraries})

@login_required
def change_info(request: HttpRequest):
    return render(request, "sclibrary/page_change_info.html")

@login_required
def change_username(request: HttpRequest):
    if request.method == "POST":
        form = UserForm.ChangeUsername(request.POST)
        if form.is_valid():
            newUsername = form.cleaned_data["newUsername1"]
            request.user.username = newUsername
            request.user.save()
            return redirect("home")
    else:
        form = UserForm.ChangeUsername()
    return render(request, "sclibrary/page_change_username.html", {"form": form})

@login_required
def change_password(request: HttpRequest):
    if request.method == "POST":
        form = UserForm.ChangePassword(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data["currentPassword"]
            new_password = form.cleaned_data["newPassword1"]
            if not request.user.check_password(current_password):
                form.add_error("currentPassword", "That was not your current password!")
                return render(request, "sclibrary/page_change_password.html", {"form": form})
            
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            return redirect("home")
    else:
        form = UserForm.ChangePassword()
    return render(request, "sclibrary/page_change_password.html", {"form": form})

@login_required
def change_email(request: HttpRequest):
    if request.method == "POST":
        form = UserForm.ChangeEmail(request.POST)
        if form.is_valid():
            current_email = form.cleaned_data["currentEmail"]
            new_email = form.cleaned_data["newEmail1"]
            if current_email != request.user.email:
                form.add_error("currentEmail", "This is not your current email!")
                return render(request, "sclibrary/page_change_email.html", {"form": form})
            
            request.user.email = form.cleaned_data["newEmail1"]
            request.user.save()
            return redirect("home")
    else:
        form = UserForm.ChangeEmail()
    return render(request, "sclibrary/page_change_email.html", {"form": form})

@login_required
def myprofileRequests(request: HttpRequest):
    if (request.user.user_type == USER_TYPES.LENDER):
        return HttpResponse(request.user.lender.library)
    elif (request.user.user_type == USER_TYPES.BORROWER):
        return HttpResponse("Placeholder")

@login_required
def viewItem(request: HttpRequest, item_pk: int):
    item = get_object_or_404(SCLibraryModels.Item, pk=item_pk)

    if request.user.user_type == USER_TYPES.LENDER and request.user.lender != item.library.owner:
        return HttpResponseForbidden("You are not the owner of this item, and thus are not allowed to view it")
    if item.is_visible == False and request.user.user_type == USER_TYPES.BORROWER:
        return HttpResponseForbidden("This item has been hidden by it's owner")

    borrow_request = SCLibraryModels.BorrowRequest.objects.filter(item=item_pk,status="AC").first()
    return render(request, "sclibrary/item_view.html", {"item": item, "borrow_request": borrow_request})

@login_required
def rateItem(request: HttpRequest, item_pk: int):
    return HttpResponse("Currently cannot rate this item")

@login_required
def viewBorrow(request: HttpRequest, item_pk: int):
    item = SCLibraryModels.Item.objects.filter(id=item_pk).first()
    if (item == None):
        return HttpResponse("Item does not exist")
    item_requests = item.borrowrequest_set.all().values()
    return HttpResponse(item_requests)

@login_required
def viewWishlist(request: HttpRequest):
    if (request.user.user_type != USER_TYPES.BORROWER):
        return error_lender_attempted_to_access_borrower_only_page(request)
    saved_items = SCLibraryModels.BorrowerWishList.objects.filter(
        borrower_id=request.user.pk
    )
    available_items = SCLibraryModels.Item.objects.filter(
        is_visible=True
    ).order_by("title")
    return render(
        request,
        "sclibrary/page_wishlist.html",
        {
            "saved_items": saved_items,
            "available_items": available_items
        }
    )

def logout_view(request: HttpRequest):
    """Sign out from a normal link. Django 5+ LogoutView only accepts POST,
    which made the top bar's "Sign out" link return HTTP 405."""
    logout(request)
    return redirect("index")


def error_lender_attempted_to_access_borrower_only_page(request: HttpRequest):
    return HttpResponseForbidden("Your account type does not allow you to access this page")
