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

    path("myprofile/", views.myprofile, name="myprofile"),
    path("mylibrary/requests/", views.mylibrary, name="mylibrary-requests"),

    path("item/<int:pk>/", views.viewItem, name="view-item"),
    path("item/add/", ItemForm.CreateItem.as_view(), name="add-item"),
    path("item/<int:pk>/edit/", ItemForm.EditItem.as_view(), name="edit-item"),
    path("item/<int:pk>/delete/", ItemForm.DeleteItem.as_view(), name="delete-item"),
    path("view/<int:pk>/rate/", views.rateItem, name="rate-item"),

    path("item/<int:pk>/request/", views.viewBorrow, name="view-requests"),
    path("item/<int:item_id>/request/<int:request_id>/", views.viewBorrow, name="view-request"),
    path("view/<int:item_id>/request/<int:request_id>/validate/", views.validateRequest, name="validate-request"),
    
    path("wishlist/", views.viewWishlist, name="view-wishlist"),
    path("notifications/", views.viewNotifs, name="view-notifications"),
    
    path("user/borrower/<int:user_id>/", views.viewBorrower, name="view-borrower"),
    path("user/lender/<int:user_id>/", views.viewLender, name="view-lender"),
]
