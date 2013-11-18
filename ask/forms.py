from django.forms import *
from ask.models import Question
from django import forms


class TagsField(forms.CharField):
    def to_python(self, value):
        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(', ')

    def validate(self, value):
        # Use the parent's handling of required fields, etc.
        super(TagsField, self).validate(value)

        if len(value) >= 3:
            raise forms.ValidationError("Should be 0-3 tags in here")


class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, widget=TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'What\'s your problem?'}))
    content = forms.CharField(max_length=2048, widget=Textarea(attrs={
                              'class': 'form-control',
                              'placeholder': 'Place detailed information here...'}))
    tags = TagsField(required=False, widget=TextInput( attrs={
                    'class': 'form-control',
                    'placeholder': 'tag1, tag2, tag3'}))