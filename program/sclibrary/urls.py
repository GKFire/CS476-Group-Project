from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("", views.register, name="register"),
    path("", views.mainB, name="mainB"),
    path("", views.mainL, name="mainL"),
    path("", views.viewItem, name="viewItem"),
    path("", views.viewBorrowB, name="viewBorrowB"),
    path("", views.viewBorrowL, name="viewBorrowL"),
    path("", views.viewWishlist, name="viewWishlist"),
    path("", views.viewNotifs, name="viewNotifs"),
    path("", views.viewBorrower, name="viewBorrower"),
    path("", views.viewLender, name="viewLender"),
    path("", views.rateItem, name="rateItem"),
    path("", views.addItem, name="addItem"),
    path("", views.validateRequest, name="validateRequest")
]
