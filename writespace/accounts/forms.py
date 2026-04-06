from django import forms
from django.contrib.auth.models import User


TAILWIND_INPUT_CLASSES = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm '
    'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 '
    'dark:bg-gray-700 dark:border-gray-600 dark:text-white '
    'dark:focus:ring-blue-400 dark:focus:border-blue-400'
)

TAILWIND_SELECT_CLASSES = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm '
    'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 '
    'dark:bg-gray-700 dark:border-gray-600 dark:text-white '
    'dark:focus:ring-blue-400 dark:focus:border-blue-400'
)


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Username',
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        }),
    )


class RegisterForm(forms.Form):
    display_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Display Name',
        }),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Username',
            'autocomplete': 'username',
        }),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['display_name'],
        )
        return user


class CreateUserForm(forms.Form):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]

    display_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Display Name',
        }),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Username',
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': TAILWIND_SELECT_CLASSES,
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def save(self):
        is_admin = self.cleaned_data['role'] == 'admin'
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['display_name'],
            is_staff=is_admin,
            is_superuser=is_admin,
        )
        return user