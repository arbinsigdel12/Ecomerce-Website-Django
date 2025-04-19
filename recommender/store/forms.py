from django import forms
from .models import Feedback
from store import models

class UserFeedbackForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int, 
        widget=forms.RadioSelect(attrs={'class': 'star-rating'}),
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 40,
            'placeholder': 'Share your experience with this product...',
            'class': 'form-control'
        }),
        label="Your comments",
        required=False,
        help_text="Optional, but your detailed feedback helps others!"
    )

    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        error_messages = {
            'rating': {
                'required': 'Please select a rating',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            if field_name == 'rating':
                field.widget.attrs['class'] = 'star-rating'