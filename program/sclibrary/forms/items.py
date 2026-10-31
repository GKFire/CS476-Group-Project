from django import forms


from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import sclibrary.models as SCLibraryModels

class CreateItem(forms.Form):
    title = forms.CharField(max_length=127)
    release = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), help_text="When was the physical item released?")
    producer = forms.CharField(max_length=127)
    condition = forms.CharField(max_length=127,required=False)
    description = forms.CharField(widget=forms.Textarea, max_length=127,required=False)
    notes = forms.CharField(widget=forms.Textarea, max_length=127,required=False)
    item_format = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Item.FORMAT_CHOICES)
    age_rating = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Item.AGE_RATING_CHOICES)

    def clean(self):
        return super().clean()

    def save(self, request):
        data = self.cleaned_data
        return SCLibraryModels.Item.objects.create(library=request.user.lender.library, 
            title=data["title"],
            release=data["release"],
            producer=data["producer"],
            condition=data["condition"],
            description=data["description"],
            notes=data["notes"],
            item_format=data["item_format"],
            age_rating=data["age_rating"])

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