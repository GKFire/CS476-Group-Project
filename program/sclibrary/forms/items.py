from django import forms

from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import sclibrary.models as SCLibraryModels

import django.views.generic as generic

def createNewItem(type: str):
    if not type:
        return CreateItem
    type = type.lower()
    if type == "videogame":
        return CreateVideoGameItem
    elif type == "movie":
        return CreateMovieItem
    elif type == "music":
        return CreateMusicItem
    elif type == "book":
        return CreateBookItem
    else:
        return CreateItem




class CreateItem(forms.Form):
    title = forms.CharField(max_length=127)
    release = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), help_text="When was the physical item released?")
    producer = forms.CharField(max_length=127, help_text="Production Company")
    condition = forms.CharField(max_length=127,required=False, help_text="Physical condition of the item")
    description = forms.CharField(widget=forms.Textarea, max_length=127,required=False)
    notes = forms.CharField(widget=forms.Textarea, max_length=127,required=False)

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
            item_type=SCLibraryModels.Item.Types.OTHER)

class CreateVideoGameItem(CreateItem):
    item_format = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.VideoGame.FORMAT_CHOICES)
    age_rating = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.VideoGame.AGE_RATING_CHOICES)

    def save(self, request):
        data = self.cleaned_data
        return SCLibraryModels.VideoGame.objects.create(library=request.user.lender.library, 
            title=data["title"],
            release=data["release"],
            producer=data["producer"],
            condition=data["condition"],
            description=data["description"],
            item_format=data["item_format"],
            age_rating=data["age_rating"],
            notes=data["notes"],
            item_type=SCLibraryModels.Item.Types.VIDEOGAME)

class CreateMovieItem(CreateItem):
    item_format = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Movie.FORMAT_CHOICES)
    age_rating = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Movie.AGE_RATING_CHOICES)

    def save(self, request):
        data = self.cleaned_data
        return SCLibraryModels.Movie.objects.create(library=request.user.lender.library, 
            title=data["title"],
            release=data["release"],
            producer=data["producer"],
            condition=data["condition"],
            description=data["description"],
            item_format=data["item_format"],
            age_rating=data["age_rating"],
            notes=data["notes"],
            item_type=SCLibraryModels.Item.Types.MOVIE)

class CreateMusicItem(CreateItem):
    item_format = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Music.FORMAT_CHOICES)
    age_rating = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Music.AGE_RATING_CHOICES)

    def save(self, request):
        data = self.cleaned_data
        return SCLibraryModels.Music.objects.create(library=request.user.lender.library, 
            title=data["title"],
            release=data["release"],
            producer=data["producer"],
            condition=data["condition"],
            description=data["description"],
            item_format=data["item_format"],
            age_rating=data["age_rating"],
            notes=data["notes"],
            item_type=SCLibraryModels.Item.Types.MUSIC)

class CreateBookItem(CreateItem):
    item_format = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Book.FORMAT_CHOICES)
    age_rating = forms.ChoiceField(widget=forms.Select, choices=SCLibraryModels.Book.AGE_RATING_CHOICES)

    def save(self, request):
        data = self.cleaned_data
        return SCLibraryModels.Book.objects.create(library=request.user.lender.library, 
            title=data["title"],
            release=data["release"],
            producer=data["producer"],
            condition=data["condition"],
            description=data["description"],
            item_format=data["item_format"],
            age_rating=data["age_rating"],
            notes=data["notes"],
            item_type=SCLibraryModels.Item.Types.BOOK)

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

class SearchView(generic.ListView):
    model = SCLibraryModels.Item
    template_name = 'sclibrary/page_search.html'

    def get_queryset(self):
        title_query = self.request.GET.get("title")
        format_query = self.request.GET.get("format")
        age_rating_query = self.request.GET.get("age_rating")

        query_list = SCLibraryModels.Item.objects.all()

        if title_query:
            query_list = query_list.filter(title__icontains=title_query)

        if format_query:
            query_list = query_list.filter()

        if age_rating_query:
            query_list = query_list.filter(age_rating=age_rating_query)