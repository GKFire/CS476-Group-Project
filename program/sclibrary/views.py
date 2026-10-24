from django.shortcuts import render
from django.contrib.auth import logout

from django.http import HttpResponse
import sclibrary.models as SCLibraryModels


# Create your views here.

def index(request):
    libraries = SCLibraryModels.Library.objects.all()
    return render(request, "sclibrary/page_index.html", {"libraries": libraries})

def register(request):
    return HttpResponse("Placeholder")

def login(request):
    return HttpResponse("Placeholder")

def logout_view(request):
    logout(request)
    index(request)

def home(request: HttpResponse):
    return HttpResponse("Placeholder")

def mylibrary(request: HttpResponse):
    return HttpResponse("Placeholder")

def viewItem(request, item_id: int):
    return HttpResponse("Placeholder")

def viewBorrow(request):
    return HttpResponse("Placeholder")

def viewWishlist(request):
    return HttpResponse("Placeholder")

def viewNotifs(request):
    return HttpResponse("Placeholder")

def viewBorrower(request):
    return HttpResponse("Placeholder")

def viewLender(request):
    return HttpResponse("Placeholder")

def rateItem(request):
    return HttpResponse("Placeholder")

def addItem(request: HttpResponse):
    return HttpResponse("page_additem.html")

def validateRequest(request):
    return HttpResponse("Placeholder");

def searchItem(request):
    return HttpResponse("Placeholder");

def sendBorrowRequest(request):
    return HttpResponse("Placeholder");
