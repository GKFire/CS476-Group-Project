from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
import sclibrary.models as SCLibraryModels

import sclibrary.forms.items as ItemForm

# change testing commit
# Create your views here.

def index(request: HttpRequest):
    libraries = SCLibraryModels.Library.objects.all()
    return render(request, "sclibrary/page_index.html", {"libraries": libraries})

def register(request: HttpRequest):
    return HttpResponse("Placeholder")

def login(request: HttpRequest):
    return HttpResponse("Placeholder")

def logout_view(request):
    logout(request)
    index(request)

@login_required
def home(request: HttpRequest):
    return render(request, "sclibrary/template_page_overview.html")

def borrowerRequests(request: HttpRequest):
     return HttpRequest("Placeholder")

@login_required
def mylibrary(request: HttpRequest):
    if (request.user.user_type != SCLibraryModels.UserAccount.Types.LENDER):
        return error_borrower_attempted_to_access_lender_only_page(request)
    return HttpResponse(request.user.lender.library)

@login_required
def search(request: HttpRequest):
    return get_list_or_404(SCLibraryModels.Item)

@login_required
def searchLibrary(request: HttpRequest, library_pk: int):
    library = SCLibraryModels.Library.objects.filter(id=library_pk).first()
    if (library == None):
        return HttpResponse("Library doesn't exist")
    return HttpResponse(library.item_set.add().values().to_string())

@login_required
def viewItem(request: HttpRequest, item_pk: int):
    item = get_object_or_404(SCLibraryModels.Item, pk=item_pk)
    return JsonResponse({
        "title": item.title,
        "library": item.library.name,
        "release": item.release,
        "producer": item.producer,
        "condition": item.condition,
        "notes": item.notes,
        "format": item.item_format,
        "rating": item.age_rating
    })

@login_required
def createItem(request: HttpRequest):
    if (request.user.user_type != SCLibraryModels.UserAccount.Types.LENDER):
            return error_borrower_attempted_to_access_lender_only_page(request)
    return ItemForm.CreateItem.as_view()(request)

@login_required
def editItem(request: HttpRequest, item_pk: int):
    if (request.user.user_type != SCLibraryModels.UserAccount.Types.LENDER):
            return error_borrower_attempted_to_access_lender_only_page(request)
    return ItemForm.EditItem.as_view()(request, pk=item_pk)

@login_required
def deleteItem(request: HttpRequest, item_pk: int):
    if (request.user.user_type != SCLibraryModels.UserAccount.Types.LENDER):
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
    if (request.user.user_type != SCLibraryModels.UserAccount.Types.BORROWER):
        return error_lender_attempted_to_access_borrower_only_page(request)
    return HttpResponse(request.user.borrowerwishlist_set.all().values().to_string())

@login_required
def viewNotifs(request: HttpRequest):
    if (request.user.user_type == SCLibraryModels.UserAccount.Types.BORROWER):
        return HttpResponse(request.user.borrower.borrowernotification_set.all().values())
    elif (request.user.user_type == SCLibraryModels.UserAccount.Types.LENDER):
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