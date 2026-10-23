from django.shortcuts import render
from django.contrib.auth import logout

from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, "sclibrary/page_index.html");

def register(request):
    return HttpResponse("Placeholder");

def login(request):
    return HttpResponse("Placeholder");

def logout_view(request):
    logout(request)
    index(request)

def mainB(request):
    return HttpResponse("Placeholder");

def mainL(request):
    return HttpResponse("Placeholder");

def viewItem(request):
    return HttpResponse("Placeholder");

def viewBorrowB(request):
    return HttpResponse("Placeholder");

def viewBorrowL(request):
    return HttpResponse("Placeholder");

def viewWishlist(request):
    return HttpResponse("Placeholder");

def viewNotifs(request):
    return HttpResponse("Placeholder");

def viewBorrower(request):
    return HttpResponse("Placeholder");

def viewLender(request):
    return HttpResponse("Placeholder");

def rateItem(request):
    return HttpResponse("Placeholder");

def addItem(request):
    return HttpResponse("Placeholder");

def validateRequest(request):
    return HttpResponse("Placeholder");

def searchItem(request):
    return HttpResponse("Placeholder");

def sendBorrowRequest(request):
    return HttpResponse("Placeholder");
