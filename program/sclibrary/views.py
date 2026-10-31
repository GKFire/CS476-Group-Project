from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
import sclibrary.models as SCLibraryModels

import sclibrary.forms.items as ItemForm
import sclibrary.forms.user as UserForm


USER_TYPES = SCLibraryModels.UserAccount.Types


# Create your views here.

def index(request: HttpRequest):
    libraries = SCLibraryModels.Library.objects.all()
    return render(request, "sclibrary/page_index.html")

def register(request: HttpRequest):
    return UserForm.CreateUser.as_view()(request)

@login_required
def home(request: HttpRequest):
    libraries = SCLibraryModels.Library.objects.all()
    return render(request, "sclibrary/page_home.html", {"libraries": libraries, "user_type": request.user.user_type})

@login_required
def myprofile(request: HttpRequest):
    if (request.user.user_type == USER_TYPES.LENDER):
        return HttpResponse(request.user.lender.library)
    elif (request.user.user_type == USER_TYPES.BORROWER):
        return HttpResponse("Placeholder")

@login_required
def myprofileRequests(request: HttpRequest):
    if (request.user.user_type == USER_TYPES.LENDER):
        return HttpResponse(request.user.lender.library)
    elif (request.user.user_type == USER_TYPES.BORROWER):
        return HttpResponse("Placeholder")

@login_required
def search(request: HttpRequest):
    return get_list_or_404(SCLibraryModels.Item)

@login_required
def searchLibrary(request: HttpRequest, library_pk: int):
    library = SCLibraryModels.Library.objects.filter(id=library_pk).first()
    if (library == None):
        return HttpResponse("Library doesn't exist")
    return HttpResponse(library.item_set.all().values())

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
def editItem(request: HttpRequest, item_pk: int):
    if (request.user.user_type != USER_TYPES.LENDER):
            return error_borrower_attempted_to_access_lender_only_page(request)
    return ItemForm.EditItem.as_view()(request, pk=item_pk)

@login_required
def deleteItem(request: HttpRequest, item_pk: int):
    if (request.user.user_type != USER_TYPES.LENDER):
            return error_borrower_attempted_to_access_lender_only_page(request)
    return ItemForm.DeleteItem.as_view()(request, pk=item_pk)

@login_required
def rateItem(request: HttpRequest, item_pk: int):
    return HttpResponse("Currently cannot rate this item")

@login_required
def viewBorrow(request: HttpRequest, item_pk: int):
    item = SCLibraryModels.Item.objects.filter(id=item_pk).first()
    if (item == None):
        return HttpResponse("Item does not exist")
    item_requests = item.borrowrequest_set.all().values().to_string()
    return HttpResponse(item_requests)

@login_required
def viewWishlist(request: HttpRequest):
    if (request.user.user_type != USER_TYPES.BORROWER):
        return error_lender_attempted_to_access_borrower_only_page(request)
    return HttpResponse(request.user.borrowerwishlist_set.all().values().to_string())

@login_required
def viewNotifs(request: HttpRequest):
    if (request.user.user_type == USER_TYPES.BORROWER):
        return HttpResponse(request.user.borrower.borrowernotification_set.all().values())
    elif (request.user.user_type == USER_TYPES.LENDER):
        return HttpResponse(request.user.lender.lendernotification_set.all().values())
    else:
        return HttpResponse("Your account does not support notifications")

@login_required
def viewBorrower(request: HttpRequest, user_pk: int):
    return get_object_or_404(SCLibraryModels.Borrower, pk=user_pk)

@login_required
def viewLender(request: HttpRequest, user_pk: int):
    return get_object_or_404(SCLibraryModels.Lender, pk=user_pk)

@login_required
def validateRequest(request: HttpRequest):
    return HttpResponse("Placeholder")

@login_required
def sendBorrowRequest(request: HttpRequest):
    return HttpResponse("Placeholder")

def error_borrower_attempted_to_access_lender_only_page(request: HttpRequest):
    return HttpResponseForbidden("Your account type does not allow you to access this page")

def error_lender_attempted_to_access_borrower_only_page(request: HttpRequest):
    return HttpResponseForbidden("Your account type does not allow you to access this page")