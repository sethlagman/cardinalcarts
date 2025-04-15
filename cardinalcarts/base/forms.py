from django import forms
from django.contrib.auth.models import User
from .models import Profile, Product

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=15)
    user_status = forms.ChoiceField(choices=Profile.USER_STATUS_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'description']