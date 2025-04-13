from django import forms
from datetime import datetime
import re

class LoginForm(forms.Form):
    """Form for user login."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class SignupForm(forms.Form):
    """Form for user registration."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Basic phone number validation
        if not re.match(r'^\+?[0-9]{10,15}$', phone_number):
            raise forms.ValidationError('Enter a valid phone number.')
        return phone_number
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data

class BookingForm(forms.Form):
    """Form for booking appointments."""
    customer_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'})
    )
    customer_phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    service = forms.ChoiceField(
        choices=[],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stylist = forms.ChoiceField(
        choices=[],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date', 'min': datetime.now().strftime('%Y-%m-%d')}
        )
    )
    time = forms.ChoiceField(
        choices=[('', 'Select Time')],  # Default empty choice
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Special Requests', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services', [])
        stylists = kwargs.pop('stylists', [])
        time_slots = kwargs.pop('time_slots', [])
        
        super(BookingForm, self).__init__(*args, **kwargs)
        
        # Populate service choices
        self.fields['service'].choices = [(s['id'], f"{s['name']} (₹{s['price']})") for s in services]
        
        # Populate stylist choices
        self.fields['stylist'].choices = [(s['id'], s['name']) for s in stylists]
        
        # Populate time slot choices
        self.fields['time'].choices = [(t, t) for t in time_slots]

class ReviewForm(forms.Form):
    """Form for submitting reviews."""
    rating = forms.ChoiceField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Review', 'rows': 4})
    )

class ServiceForm(forms.Form):
    """Form for adding/editing services (admin)."""
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3})
    )
    category = forms.ChoiceField(
        choices=[],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'})
    )
    duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration (minutes)'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [(c['id'], c['name']) for c in categories]

class StylistForm(forms.Form):
    """Form for adding/editing stylists (admin)."""
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stylist Name'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bio', 'rows': 3})
    )
    profile_image = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Profile Image URL'})
    )
    experience_years = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    services = forms.MultipleChoiceField(
        required=False,
        choices=[],  # Will be populated dynamically
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services', [])
        super(StylistForm, self).__init__(*args, **kwargs)
        self.fields['services'].choices = [(s['id'], s['name']) for s in services]
