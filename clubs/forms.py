from django import forms, template
from django.core.validators import RegexValidator
from .models import User, Club
from django.contrib.auth import authenticate


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'chess_level','personal_statement']
        widgets = { 'bio': forms.Textarea(), 'personal_statement': forms.Textarea()}

class SignUpForm(forms.ModelForm):
    """Form to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'bio','chess_level','personal_statement']
        widgets = { 'bio': forms.Textarea(), 'personal_statement': forms.Textarea()}

    club = forms.ChoiceField(choices = [],label="Select the club you would like to apply for:")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['club'].choices = [(x.pk, x.__str__()) for x in Club.objects.all()]

    new_password = forms.CharField(
            label = 'Password',
            widget=forms.PasswordInput(),
            validators=[RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
                message='Password must contain an uppercase character, a lowercase '
                    'character and a number.'
            )]
        )
    password_confirmation = forms.CharField(label = 'Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
            chess_level=self.cleaned_data.get('chess_level'),
            personal_statement=self.cleaned_data.get('personal_statement'),
            club=self.cleaned_data.get('club')
        )

        return user
    register = template.Library()

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible"""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

        return user

class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number.'

            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class CreateClubForm(forms.ModelForm):
    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'location', 'description']
        widgets = { 'description': forms.Textarea()}

    def __init__(self, *args, **kwargs):
        super(CreateClubForm, self).__init__(*args, **kwargs)

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()

    def save(self):
        """Create a new club."""

        super().save(commit=False)
        club = Club(
            name=self.cleaned_data.get('name'),
            location=self.cleaned_data.get('location'),
            description=self.cleaned_data.get('description'),
        )
        club.save()
        return club
