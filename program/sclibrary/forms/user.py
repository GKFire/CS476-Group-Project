from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.forms import ChoiceField
import sclibrary.models as SCLibraryModels

class CreateUser(CreateView):
    model = SCLibraryModels.UserAccount
    fields = ["username", "email", "password", "user_type"]
    # fields["user_type"] = ChoiceField(choices=SCLibraryModels.UserAccount.RESTRICTED_USER_TYPES)

    def form_valid(self, form):
        return super().form_valid(form)

class CreateBorrower(CreateView):
    model = SCLibraryModels.Lender
    fields = ["username", "email", "password"]
    def form_valid(self, form):
        return super().form_valid(form);

class CreateLender(CreateView):
    model = SCLibraryModels.Lender
    fields = ["username", "email", "password"]
    def form_valid(self, form):
        return super().form_valid(form);

class EditUser(LoginRequiredMixin, UpdateView):
    model = SCLibraryModels.UserAccount
    fields = ["username", "email", "password"]

class DeleteUser(LoginRequiredMixin, DeleteView):
    model = SCLibraryModels.UserAccount
    success_url = reverse_lazy("myprofile")