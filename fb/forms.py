from django.forms import (
    Form, CharField, Textarea, PasswordInput, ChoiceField, DateField,
    ImageField, ModelForm, TextInput
)

from fb.models import UserProfile, UserPost


class UserPostForm(ModelForm):

    class Meta:
        model = UserPost
        fields = ('text', 'img')
        widgets = {
            'text' : Textarea(attrs={
                    'class' : 'form-control',
                    'placeholder' : "What's on your mind?",
                    'rows' : 1,
                })
        }


class SearchForm(Form):
    q = CharField(widget=TextInput(
        attrs={
            'placeholder': "Search",
            'class' : 'form-control',
        }))


class UserPostCommentForm(Form):
    text = CharField(widget=Textarea(
        attrs={'rows': 1, 'cols': 50, 'class': 'form-control', 'placeholder': "Write a comment..."}))


class UserLogin(Form):
    username = CharField(max_length=30)
    password = CharField(widget=PasswordInput)


class UserProfileForm(Form):
    first_name = CharField(max_length=100, required=False)
    last_name = CharField(max_length=100, required=False)
    gender = ChoiceField(choices=UserProfile.GENDERS, required=False)
    date_of_birth = DateField(required=False)
    avatar = ImageField(required=False)

