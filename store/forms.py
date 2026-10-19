from .models import Review
from django import forms


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Write your review...'
                }
            ),
        }