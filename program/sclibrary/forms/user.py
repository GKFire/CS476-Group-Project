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

# ---------------------------------------------------------------------------
# Registration (Smit)
# Creates a real Lender or Borrower through their managers, so the password is
# hashed and the Library signal fires for new lenders.
# ---------------------------------------------------------------------------
from django import forms
from django.contrib.auth import password_validation


class RegisterForm(forms.Form):
    ACCOUNT_TYPES = [
        (SCLibraryModels.UserAccount.Types.BORROWER, "Borrower (I want to borrow items)"),
        (SCLibraryModels.UserAccount.Types.LENDER, "Lender (I want to lend out my items)"),
    ]

    username = forms.CharField(max_length=63)
    email = forms.EmailField(max_length=255)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES, widget=forms.RadioSelect,
                                     initial=SCLibraryModels.UserAccount.Types.BORROWER)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip().lower()
        if SCLibraryModels.UserAccount.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if SCLibraryModels.UserAccount.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with that email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "The passwords do not match.")
        if p1:
            try:
                password_validation.validate_password(p1)
            except forms.ValidationError as e:
                self.add_error("password1", e)
        return cleaned

    def save(self):
        d = self.cleaned_data
        model = (SCLibraryModels.Lender if d["account_type"] == SCLibraryModels.UserAccount.Types.LENDER
                 else SCLibraryModels.Borrower)
        return model.objects.create_user(d["username"], d["email"], d["password1"])
