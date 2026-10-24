from django.shortcuts import render
from django.contrib.auth import logout

from django.http import HttpResponse
import sclibrary.models as SCLibraryModels

# change testing commit
# Create your views here.

def index(request: HttpResponse):
    libraries = SCLibraryModels.Library.objects.all()
    return render(request, "sclibrary/page_index.html", {"libraries": libraries})

def register(request: HttpResponse):
    return HttpResponse("Placeholder")

def login(request: HttpResponse):
    return HttpResponse("Placeholder")

def logout_view(request):
    logout(request)
    index(request)

def home(request: HttpResponse):
    return HttpResponse("Placeholder")

def mylibrary(request: HttpResponse):
    return HttpResponse("Placeholder")

def viewItem(request: HttpResponse, item_id: int):
    return HttpResponse("Placeholder")

def viewBorrow(request: HttpResponse):
    return HttpResponse("Placeholder")

def viewWishlist(request: HttpResponse):
    return HttpResponse("Placeholder")

def viewNotifs(request: HttpResponse):
    return HttpResponse("Placeholder")

def viewBorrower(request: HttpResponse):
    return HttpResponse("Placeholder")

def viewLender(request: HttpResponse):
    return HttpResponse("Placeholder")

def rateItem(request: HttpResponse):
    return HttpResponse("Placeholder")

def addItem(request: HttpResponse):
    return HttpResponse("page_additem.html")

def validateRequest(request: HttpResponse):
    return HttpResponse("Placeholder")

def searchItem(request: HttpResponse):
    return HttpResponse("Placeholder")

def sendBorrowRequest(request: HttpResponse):
    return HttpResponse("Placeholder")
