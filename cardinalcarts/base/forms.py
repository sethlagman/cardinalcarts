from django import forms
from django.contrib.auth.models import User
from .models import Profile, Product
import re

from django import forms
from django.contrib.auth.models import User
from base.models import Profile
import re

class RegisterForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)
    user_status = forms.ChoiceField(choices=Profile.USER_STATUS_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'user_status', 'password']

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name'].strip().lower()
        if len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters.")
        if not first_name.isalpha():
            raise forms.ValidationError("First name must contain only alphabetic characters with no spaces.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name'].strip().lower()
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters.")
        if not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only alphabetic characters with no spaces.")
        return last_name

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if len(username) < 2:
            raise forms.ValidationError("Username must be at least 2 characters long.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip()
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")
        if len(phone) < 7 or len(phone) > 15:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*()_+=\-]', password):
            raise forms.ValidationError("Password must contain at least one special character (!@#$%^&*()_+=-).")
        return password

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'quantity']
        widgets = {
            'category': forms.TextInput(attrs={})
        }