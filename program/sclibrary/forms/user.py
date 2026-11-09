import sclibrary.models as SCLibraryModels

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

class ChangeUsername(forms.Form):
    newUsername1 = forms.CharField(label="New Username", max_length=63)
    newUsername2 = forms.CharField(label="Confirm New Username", max_length=63)

    def clean(self):
        cleaned = super().clean()
        newUsername1, newUsername2 = cleaned.get("newUsername1"), cleaned.get("newUsername2")
        if newUsername1 and newUsername2 and newUsername1 != newUsername2:
            self.add_error("newUsername2", "Usernames do not match!")
        if newUsername1 and SCLibraryModels.UserAccount.objects.filter(username=newUsername1).exists():
            self.add_error("newUsername1", "That username is already taken!")
        return cleaned

class ChangeEmail(forms.Form):
    currentEmail = forms.EmailField(label="Current Email", max_length=255)
    newEmail1 = forms.EmailField(label="New Email", max_length=255)
    newEmail2 = forms.EmailField(label="Confirm New Email", max_length=255)

    def clean(self):
        cleaned = super().clean()
        currentEmail, newEmail1, newEmail2 = cleaned.get("currentEmail"), cleaned.get("newEmail1"), cleaned.get("newEmail2")
        if newEmail1 and newEmail2 and newEmail1 != newEmail2:
            self.add_error("newEmail2", "Emails do not match!")
        if newEmail1 and SCLibraryModels.UserAccount.objects.filter(email=newEmail1).exists():
            self.add_error("newEmail1", "An account with that email already exists!")
        return cleaned

class ChangePassword(forms.Form):
    currentPassword = forms.CharField(label="Current Password", widget=forms.PasswordInput())
    newPassword1 = forms.CharField(label="New Password", widget=forms.PasswordInput())
    newPassword2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        currentPassword, newPassword1, newPassword2 = cleaned.get("currentPassword"), cleaned.get("newPassword1"), cleaned.get("newPassword2")
        if newPassword1 and newPassword2 and newPassword1 != newPassword2:
            self.add_error("newPassword2", "Passwords do not match!")
        return cleaned
                

