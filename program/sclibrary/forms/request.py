"""Borrower-side form for sending a borrow request (Smit)."""
from django import forms
from django.utils import timezone


class BorrowRequestForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}),
                                 help_text="When would you like to start borrowing the item?")
    return_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}),
                                  help_text="When would you like to return the item? (At least one week after the start day)")

    def clean(self):
        cleaned = super().clean()
        start, ret = cleaned.get("start_date"), cleaned.get("return_date")
        today = timezone.localdate()
        if start and start < today:
            self.add_error("start_date", "The start date cannot be in the past.")
        if ret and ret < today:
            self.add_error("return_date", "The return date cannot be in the past.")
        if start and ret:
            if ret <= start:
                self.add_error("return_date", "The return date must be after the start date.")
            elif (ret - start).days < 7:
                self.add_error("return_date", "The return date must be at least one week after the start date.")
        return cleaned