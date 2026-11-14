from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
import sclibrary.models as SCLibraryModels
from django import forms
from django.urls import reverse_lazy


class ChangeLibrary(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.Library
    fields = ["name", "default_item_visibility"]
    template_name="sclibrary/page_change_library.html"
    success_url = reverse_lazy("home")

    def clean(self):
        cleaned = super().clean()
        library_name = cleaned.get("name")
        if len(library_name) < 6:
            self.add_error("name", "name is too short!")
        return cleaned