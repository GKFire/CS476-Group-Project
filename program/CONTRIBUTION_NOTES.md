# Lender request workflow, notifications, library signal (dopedgod)

## New files (no merge conflicts expected)
- sclibrary/signals.py, services.py, notifications.py, request_views.py
- sclibrary/management/commands/send_overdue_notifications.py
- templates/sclibrary/{base_simple,request_list,request_detail,notifications}.html
- tests.py (replaces the empty stub)

## Edited files
- sclibrary/apps.py: adds `ready()` to register signals
- sclibrary/urls.py: replace these routes (and `from . import request_views`):

    path("myprofile/requests/", request_views.request_list, name="myprofile-requests"),
    path("item/<int:item_pk>/requests/", views.viewBorrow, name="item-view-requests"),   # unchanged
    path("request/<int:request_pk>/", request_views.request_detail, name="view-request"),
    path("request/<int:request_pk>/validate/", request_views.request_decision, name="validate-request"),
    path("item/<int:item_pk>/visibility/", request_views.toggle_item_visibility, name="toggle-item-visibility"),
    path("notifications/", request_views.notifications_list, name="view-notifications"),
    path("notifications/read/", request_views.notifications_mark_read, name="notifications-mark-read"),

## Hook for Smit
`services.create_request(borrower, item, start, return_date)` does the validation (hidden item,
already on loan, return before start) and notifies the lender. Call it from `sendBorrowRequest`.

## Run
    python manage.py makemigrations sclibrary && python manage.py migrate
    python manage.py test sclibrary
    python manage.py send_overdue_notifications   # run daily (cron) in production
