import pytz
import re

from datetime import date

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from tasks.models import Task, MyUser
from django.core.exceptions import ValidationError

utc = pytz.utc
utc_now = date.today()

class TaskForm(forms.ModelForm):
    
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Add new task.....'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Add Description of task.....'}))

    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['my_user']

class UserRegisterationForm(ModelForm):

    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = MyUser
        fields = ['username','firstname','lastname','email','password','confirm_password','birthdate','phone','address']

    '''def clean(self):
        cleaned_data = super(UserRegisterationForm, self).clean()
        password = cleaned_data["password"]
        password2 = cleaned_data["confirm_password"]
        print("***********Password clean***********")
        print('P1:', password)
        print('P2:', password2)
        if password != password2:
            raise forms.ValidationError("Password doesn't match")
        return password'''
    

    def clean_username(self):
        username = self.cleaned_data.get("username")
        print("***********Username clean***********")
        if MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken")
        return username

    
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        phone_validation = re.findall("\d", phone)
        print("***********Phone clean***********")
        if MyUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already taken")

        if len(phone)!=10:
            raise forms.ValidationError("The phone number must be of 10 digits")

        if len(phone_validation)!=10:
            raise forms.ValidationError("The phone number must be of numberic only")
        return phone


    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")
        print("***********DOB clean***********")
        if birthdate > utc_now:
            raise forms.ValidationError("Date of Birth cannot be in future")
        return birthdate


    def clean_firstname(self):
        firstname = self.cleaned_data.get("firstname")
        lastname = self.cleaned_data.get("lastname")
        print("***********Firstname clean***********")
        if firstname == lastname:
            raise ValidationError("Fisrtname and Lastname can't be same")

        return firstname

    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        print("***********Email clean***********")
        if len(email) > 6:
            if re.match('\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', email) != None:
                raise ValidationError("Email is not proper")
        return email