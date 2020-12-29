from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from tasks.models import Task, MyUser
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
        fields = ['username','first_name','last_name','email','password','confirm_password','birthdate','phone','address']

        def clean(self):
            cleaned_data = super(UserRegisterationForm, self).clean()
            password = cleaned_data.get("password")
            confirm_password = cleaned_data.get("confirm_password")

            if password != confirm_password:
                raise forms.ValidationError("password and confirm_password doesn't match")