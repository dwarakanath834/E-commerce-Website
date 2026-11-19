from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=[(value, f"{value} star{'s' if value != 1 else ''}") for value in range(5, 0, -1)])

    class Meta:
        model = Review
        fields = ("rating", "title", "body")
        widgets = {"body": forms.Textarea(attrs={"rows": 4})}