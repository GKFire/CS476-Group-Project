from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
import sclibrary.models as SCLibraryModels

class EditLibrary(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.Library
    fields = ["name", "default_item_visibility"]