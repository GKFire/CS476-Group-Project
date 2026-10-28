"""Borrower-side form for sending a borrow request (Smit)."""
from django import forms
from django.utils import timezone


class BorrowRequestForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}),
                                 help_text="What's the earliest you'd like to return the item?")
    return_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}),
                                  help_text="What's the latest you'd like to return the item? (At least one week after the earliest day)")

    def clean(self):
        cleaned = super().clean()
        start, ret = cleaned.get("start_date"), cleaned.get("return_date")
        today = timezone.localdate()
        if start and start < today:
            self.add_error("start_date", "The earliest date cannot be in the past.")
        if ret and ret < today:
            self.add_error("return_date", "The latest date cannot be in the past.")
        if start and ret and ret <= start:
            self.add_error("return_date", "The latest date must be after the earliest date.")
        days_difference = (ret - start).days
        if days_difference < 7:
            self.add_error("return_date", "The latest date must be at least one week after the earliest date.")
        return cleaned
