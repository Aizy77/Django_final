from django import forms  
from django.contrib.auth.models import User  
from django.core.validators import EmailValidator
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Q
from .models import *
# from .views import *
import re


# class CustomerProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

class CustomerProfileForm(forms.Form):
    class Meta:
        model = User
        fileds = '__all__'

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
          
class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    email = forms.EmailField(required=True, validators=[EmailValidator()])
    password1 = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput)

    # email = forms.EmailField(help_text='A valid email address, please.', required=True)

    # class Meta:
    #     model = get_user_model()
    #     fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_password2(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The passwords do not match.') 
        return 

    def clean_password1(self):
        cleaned_data = super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if len(password1) < 8:
            raise forms.ValidationError("Password must contain at least 8 characters")
        if not re.search('[A-Z]', password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter")
        if not re.search('[a-z]', password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter")
        if not re.search('[0-9]', password1):
            raise forms.ValidationError("Password must contain at least one number")
        return password1 
  
    def clean_email(self):  
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Already Exist.")
        return email  
    
    # def save(self, commit=True):
    #     user = super(RegistrationForm, self).save(commit=False)
    #     user.email = self.cleaned_data['email']
    #     if commit:
    #         user.save()

    #     return user
    
class ProfileForm(UserChangeForm, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({'class': 'form-control'})
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['birth_date'].widget.attrs.update({'class': 'form-control', 'placeholder': 'YYYY-MM-DD'})

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput)
    password = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput)

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'start_time', 'end_time']
        widgets = {
            'table' : forms.Select(attrs = {'class' : 'form-select form-control'}),
            'start_time' : forms.TextInput(attrs = {'type': 'datetime-local', 'class' : 'form-control'}),
            'end_time' : forms.TextInput(attrs={'type': 'datetime-local', 'class' : 'form-control'}),
        }

        def clean(self):
            cleaned_data = super().clean()
            table = cleaned_data.get('table')
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')

            reserved_tables = Reservation.objects.filter(
                Q(start_time__lte=end_time) & Q(end_time__gte=start_time)
            ).values_list('table_id', flat=True)
            available_table = Table.objects.exclude(id__in = reserved_tables)
            print(available_table)
            if table.id in reserved_tables:
                print("Error")
                raise forms.ValidationError("Sorry, this table is already reserved during the selected time slot.")
            
            return cleaned_data       

class Reservation_errorForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'start_time', 'end_time']
        widgets = {
            'table' : forms.Select(attrs = {'class' : 'form-select form-control'}),
            'start_time' : forms.TextInput(attrs = {'type': 'datetime-local', 'class' : 'form-control', 'readonly': True, 'placeholder' : ''}),
            'end_time' : forms.TextInput(attrs={'type': 'datetime-local', 'class' : 'form-control', 'readonly': True, 'placeholder' : ''}),
        }

    def __init__(self, *args, **kwargs):
        available_table = kwargs.pop('available_table')
        super().__init__(*args, **kwargs)
        self.fields['table'] = forms.ModelChoiceField(queryset=available_table, widget=forms.Select(attrs = {'class' : 'form-select form-control'}))

RATING_CHOICES = [
    (1, '1 star'),
    (2, '2 stars'),
    (3, '3 stars'),
    (4, '4 stars'),
    (5, '5 stars'),
]

class ReviewsForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select(attrs={'class': 'form-select form-control'}))
    
    class Meta:
        model = Review
        fields = ['content', 'rating']

        widgets = {
            'content' : forms.Textarea(attrs = {'class' : 'form-control'}),
        }