"""Borrower-side form for rating an item (dopedgod)."""
from django import forms

STAR_CHOICES = [(n, f"{n} star{'s' if n > 1 else ''}") for n in range(5, 0, -1)]


class RatingForm(forms.Form):
    stars = forms.TypedChoiceField(choices=STAR_CHOICES, coerce=int, widget=forms.RadioSelect,
                                   label="Your rating")
    review = forms.CharField(required=False, max_length=2000, widget=forms.Textarea,
                             label="Review (optional)")
