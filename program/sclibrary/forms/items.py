from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import sclibrary.models as SCLibraryModels

class CreateItem(LoginRequiredMixin, CreateView):
    model = SCLibraryModels.Item
    fields = ["title", "release", "producer", "condition", "description", "notes", "item_format", "age_rating"]
    def form_valid(self, form):
        if self.request.user.user_type != SCLibraryModels.UserAccount.Types.LENDER:
            return JsonResponse(form.errors, status=401)
        library = self.request.user.lender.library
        form.instance.library = library
        form.instance.is_visible = library.default_item_visibility
        return super().form_valid(form);

class EditItem(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.Item
    fields = ["condition", "description", "notes", "is_visible"]

    def get_queryset(self):
        return SCLibraryModels.Item.objects.filter(
            library__owner_id=self.request.user.pk
        )

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = SCLibraryModels.Item
    success_url = reverse_lazy("myprofile")

    def get_queryset(self):
        return SCLibraryModels.Item.objects.filter(
            library__owner_id=self.request.user.pk
        )