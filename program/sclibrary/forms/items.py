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

def editItem(item_id: int):
    item = SCLibraryModels.Item.objects.get(id=item_id)
    if item == None:
        return None
    type = item.item_type.lower()
    if type == "videogame":
        return EditVideoGameItem
    elif type == "movie":
        return EditMovieItem
    elif type == "music":
        return EditMusicItem
    elif type == "book":
        return EditBookItem
    else:
        return EditItem

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


class EditVideoGameItem(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.VideoGame
    fields = ["condition", "description", "notes", "item_format", "age_rating", "is_visible"]
    template_name="sclibrary/item_form.html"

    def get_queryset(self):
        return SCLibraryModels.VideoGame.objects.filter(
            library__owner_id=self.request.user.pk
        )

class EditMovieItem(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.Movie
    fields = ["condition", "description", "notes", "item_format", "age_rating", "is_visible"]
    template_name="sclibrary/item_form.html"

    def get_queryset(self):
        return SCLibraryModels.Movie.objects.filter(
            library__owner_id=self.request.user.pk
        )

class EditMusicItem(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.Music
    fields = ["condition", "description", "notes", "item_format", "age_rating", "is_visible"]
    template_name="sclibrary/item_form.html"

    def get_queryset(self):
        return SCLibraryModels.Music.objects.filter(
            library__owner_id=self.request.user.pk
        )

class EditBookItem(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.Book
    fields = ["condition", "description", "notes", "item_format", "age_rating", "is_visible"]
    template_name="sclibrary/item_form.html"

    def get_queryset(self):
        return SCLibraryModels.Book.objects.filter(
            library__owner_id=self.request.user.pk
        )

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = SCLibraryModels.Item
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return SCLibraryModels.Item.objects.filter(
            library__owner_id=self.request.user.pk
        )

def get_searchset(request):
    library_query = request.GET.get("library")
    title_query = request.GET.get("title")
    format_query = request.GET.get("format")

    query_list = SCLibraryModels.Item.objects.all().order_by('title')

    if library_query and int(library_query) != 0:
        query_list = query_list.filter(library=SCLibraryModels.Library.objects.get(id=library_query))

    if format_query and format_query != "Any":
        query_list = query_list.filter(item_type=format_query)

    if title_query:
        query_list = query_list.filter(title__icontains=title_query)

    return query_list


def getBorrowHistory(borrower_id: int, library_id: int):
    borrower = SCLibraryModels.Borrower.objects.get(id=borrower_id)
    library = SCLibraryModels.Library.objects.get(id=library_id)
    if not borrower or not library: return None

    history = SCLibraryModels.BorrowRequest.objects.filter(borrower=borrower,item__library=library)

    return {
        "ongoing": (history.filter(status="RQ") | history.filter(status="AC")).order_by("-status"),
        "previous": (history.filter(status="CD") | history.filter(status="RJ")).order_by("status")
    }