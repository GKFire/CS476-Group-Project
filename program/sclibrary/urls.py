from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", LoginView.as_view(template_name="sclibrary/page_login.html"), {'next_page': settings.LOGIN_REDIRECT_URL}, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("main/", views.mainB, name="mainB"),
    path("main/", views.mainL, name="mainL"),
    path("view/<int:item_id>/", views.viewItem, name="viewItem"),
    path("view/<int:item_id>/request/<int:request_id>/", views.viewBorrowB, name="viewBorrowB"),
    path("view/<int:item_id>/request/<int:request_id>/", views.viewBorrowL, name="viewBorrowL"),
    path("wishlist/", views.viewWishlist, name="viewWishlist"),
    path("notifications/", views.viewNotifs, name="viewNotifs"),
    path("user/borrower/<int:borrower_id>/", views.viewBorrower, name="viewBorrower"),
    path("user/lender/<int:lender_id>/", views.viewLender, name="viewLender"),
    path("view/<int:item_id>/rate/", views.rateItem, name="rateItem"),
    path("view/additem/", views.addItem, name="addItem"),
    path("view/<int:item_id>/request/<int:request_id>/validate/", views.validateRequest, name="validateRequest")
]
