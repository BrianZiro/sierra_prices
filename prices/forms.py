from django import forms
from django.contrib.auth.models import User
from .models import Product, EmployeeProfile


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'buying_price', 'price']

    def clean(self):
        cleaned_data = super().clean()
        buying_price = cleaned_data.get('buying_price')
        price = cleaned_data.get('price')

        if buying_price is not None and price is not None and buying_price >= price:
            # Attach the error to the buying_price field only (no __all__ duplicate)
            self.add_error('buying_price', 'Buying price must be less than the selling price.')

        return cleaned_data


class UserEmailForm(forms.Form):
    email = forms.EmailField(label='Employee Email')


class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, added_by=None, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.is_staff = False
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            EmployeeProfile.objects.create(user=user, added_by=added_by)
        return user


class StaffCreationForm(forms.ModelForm):
    """Optional – used if you want a staff-creation form outside Django admin."""
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.is_staff = True
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user