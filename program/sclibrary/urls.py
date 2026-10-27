from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from . import views
from . import borrower_views

urlpatterns = [
    path("", views.index, name="index"), # only seen by new users
    path("login/", LoginView.as_view(template_name="sclibrary/page_login.html"), name="login"),
    path("logout/", borrower_views.logout_view, name="logout"),
    path("register/", borrower_views.register, name="register"),
    path("home/", views.home, name="home"), # default for logged-in users

    path("myprofile/", views.myprofile, name="myprofile"), # borrower sees list of currently borrowed items, lender sees list of items in their library
    path("myprofile/requests/", views.myprofileRequests, name="myprofile-requests"), # borrower sees list of requests assoicated with them, lender sees list of requests on items they own

    path("search/", views.search, name="search"), # borrower only
    path("search/library/<int:library_pk>", views.searchLibrary, name="search-library"), # borrower only

    path("item/<int:item_pk>/", views.viewItem, name="view-item"),
    path("item/create/", views.createItem, name="create-item"), # lender only
    path("item/<int:item_pk>/edit/", views.editItem, name="edit-item"), # lender only
    path("item/<int:item_pk>/delete/", views.deleteItem, name="delete-item"), # lender only
    path("item/<int:item_pk>/rate/", views.rateItem, name="rate-item"), # borrower can append, lender can only view

    path("item/<int:item_pk>/requests/", views.viewBorrow, name="item-view-requests"),
    path("item/<int:item_pk>/requests/create/", borrower_views.send_borrow_request, name="create-request"), # borrower only
    path("request/<int:request_pk>/", views.viewBorrow, name="view-request"), # both borrower and lender can update (submit revision)
    path("request/<int:request_pk>/validate/", views.validateRequest, name="validate-request"), # lender only
    
    path("wishlist/", views.viewWishlist, name="view-wishlist"), # borrower only
    path("notifications/", views.viewNotifs, name="view-notifications"),
    
    path("user/borrower/<int:user_pk>/", views.viewBorrower, name="view-borrower"), # lender only
    path("user/lender/<int:user_pk>/", views.viewLender, name="view-lender"), # borrower only
]
