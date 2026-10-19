from django.contrib import admin

# Register your models here.

import sclibrary.models as SCLibraryModels


admin.site.register(SCLibraryModels.Lender)
admin.site.register(SCLibraryModels.Borrower)
admin.site.register(SCLibraryModels.Library)
admin.site.register(SCLibraryModels.Item)
admin.site.register(SCLibraryModels.BorrowRequest)
admin.site.register(SCLibraryModels.LenderMessage)
admin.site.register(SCLibraryModels.BorrowerMessage)
admin.site.register(SCLibraryModels.BorrowerWishList)
admin.site.register(SCLibraryModels.LenderNotification)
admin.site.register(SCLibraryModels.BorrowerNotification)
