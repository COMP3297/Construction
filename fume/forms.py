from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NameForm(forms.Form):
    tag_name = forms.CharField(label='tag_name', max_length=100)

class LoginForm(forms.Form):
    email = forms.CharField(label=(u'Email'), max_length=30)
    password = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False), max_length=30)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class PlatformForm(forms.Form):
    PlatformChoice = [
        ('WINDOWS','Windows'),
        ('MAC','Mac'),
        ('LINUX','Linux'),
        ]
    platform = forms.ChoiceField(choices=PlatformChoice)
class RewardChoosingForm(forms.Form):
    RewardAmount = [
        (0,'0'),
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        (6,'6'),
        (7,'7'),
        (8,'8'),
        (9,'9'),
        (10,'10'),
    ]
    Reward_amount = forms.ChoiceField(choices=RewardAmount)
