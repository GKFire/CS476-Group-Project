from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from . import views
import sclibrary.forms.items as ItemForm

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", LoginView.as_view(template_name="sclibrary/page_login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("home/", views.home, name="home"),

    path("home/requests/", views.borrowerRequests, name="borrower-view-requests"),

    path("mylibrary/", views.mylibrary, name="mylibrary"),
    path("mylibrary/requests/", views.mylibrary, name="mylibrary-view-requests"),

    path("search/", views.search, name="search"),
    path("search/library/<int:library_pk>", views.searchLibrary, name="search"),

    path("item/<int:item_pk>/", views.viewItem, name="view-item"),
    path("item/create/", views.createItem, name="create-item"),
    path("item/<int:item_pk>/edit/", views.editItem, name="edit-item"),
    path("item/<int:item_pk>/delete/", views.deleteItem, name="delete-item"),
    path("item/<int:item_pk>/rate/", views.rateItem, name="rate-item"),

    path("item/<int:item_pk>/requests/", views.viewBorrow, name="item-view-requests"),
    path("item/<int:item_pk>/requests/create/", views.sendBorrowRequest, name="create-request"),
    path("request/<int:request_pk>/", views.viewBorrow, name="view-request"),
    path("request/<int:request_pk>/validate/", views.validateRequest, name="validate-request"),
    
    path("wishlist/", views.viewWishlist, name="view-wishlist"),
    path("notifications/", views.viewNotifs, name="view-notifications"),
    
    path("user/borrower/<int:user_pk>/", views.viewBorrower, name="view-borrower"),
    path("user/lender/<int:user_pk>/", views.viewLender, name="view-lender"),
]
