from django.contrib.auth.forms import UserCreationForm
from django.forms import *
from ask.models import Question
from django import forms
from ask.models import *


class TagsField(forms.CharField):
    def to_python(self, value):
        # Return an empty list if no input was given.
        if not value:
            return []
        tags = value.split(',')

        cleaned_tags = []

        for tag in tags:
            tag = str(tag).strip()
            if tag != '':
                if tag[-1] != ',':
                    tag = tag[0:-1]

                if not cleaned_tags.__contains__(tag):
                    cleaned_tags.append(tag)

        return cleaned_tags

    def validate(self, value):
        # Use the parent's handling of required fields, etc.
        super(TagsField, self).validate(value)

        for tag in value:
            print tag

        if len(value) > 3:
            raise forms.ValidationError("Should be 0-3 tags in here")


class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, widget=TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'What\'s your problem?'
    }))
    content = forms.CharField(max_length=2048, widget=Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Place detailed information here...'
    }))
    tags = TagsField(required=False, widget=TextInput( attrs={
        'class': 'form-control',
        'placeholder': 'tag1, tag2, tag3'
    }))


class AnswerForm(forms.Form):
    content = forms.CharField(max_length=1024, widget=Textarea(attrs={
        'id': 'id_answer_content',
        'class': 'form-control',
        'placeholder': 'Put your answer here...'
    }))


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user