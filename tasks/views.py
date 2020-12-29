from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.db import models

from tasks.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from tasks.forms import UserRegisterationForm, TaskForm
from .decorators import unauthenticated_user

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from ToDo3.settings import *
from .utils import token_generator

from django.contrib.auth.hashers import make_password

import pytz
from datetime import date
import re

# Create your views here.

utc = pytz.utc
utc_now = date.today()

def registerPage(request):
    form = UserRegisterationForm()

    if request.method =="POST":
        form = UserRegisterationForm(request.POST)
        print("Errors---------> : ",form.errors)
        if form.is_valid():
            user_form = form.save(commit=False)
            
            password1=form.cleaned_data.get('password')
            password2=form.cleaned_data.get('confirm_password')
            
            user_email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            
            name = form.cleaned_data.get('first_name')
            DOB = form.cleaned_data.get('birthdate')

            print("TYPE OF DOB: --------> :", type(DOB))
            
            username = form.cleaned_data.get('username')
            firstname = form.cleaned_data.get('first_name')
            lastname = form.cleaned_data.get('last_name')
            
            phone_validation = re.findall("\d", phone)

            if MyUser.objects.filter(username=username).exists():
                messages.error(request,"This username is already exists")

                return redirect('register')
            elif MyUser.objects.filter(phone=phone).exists():
                print("*********Entered phone elif block*********")
                messages.error(request,"This phone number already exists")
            
                return redirect('register')
            else:
                
                if password1!=password2:
                    messages.error(request,"Passwords does not match")

                    return redirect('register')
                elif DOB > utc_now:
                    messages.error(request,"Date of Birth cannot be in future")

                    return redirect('register')
                elif firstname == lastname:
                    messages.error(request,"Fisrtname and Lastname can't be same")

                    return redirect('register')
                elif len(phone_validation) != 10:
                    messages.error(request,"Phone number should be 10 digits and numeric only")

                    return redirect('register')
                
                else:
                    #import pdb; pdb.set_trace()
                    #user=MyUser.objects.create_user(phone=phone,username=username,password=password1)
                    user_form.password=make_password(password1)
                    user_form.save()
                    user_pk = user_form.pk
                    
                    user = MyUser.objects.get(pk=user_pk)
                    print('user:',user)
                    print('user pk is:',user_pk)

                    current_site = get_current_site(request)
                    email_subject = 'Activation of your ToDoApp Account'
                    message = render_to_string('tasks/email_template.html',

                    {
                        'user':user,
                        'domain':current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':token_generator.make_token(user),
                        'name':name,
                    }
                    )

                    email_message = EmailMessage(
                        email_subject,
                        message,
                        EMAIL_HOST_USER,
                        [user_email]
                    )

                    # email.fail_silently=False
                    email_message.send()

                    

                    #messages.success(request,'ACCOUNT IS ACTIVATED SUCCESSFULLY')

                    return HttpResponse("Please first confirm your email address to complete the registeration")

    context = {'form':form}
    return render(request,'tasks/register.html',context)


def loginPage(request):
    if request.method == "POST":
        
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)
            return redirect('user')
        else:
            messages.info(request,'Phone Number or Password is incorrect')

    context = {}
    return render(request,'tasks/login.html',context)

def logoutPage(request):
    
    logout(request)

    return redirect('login')

def home(request):
    
    context ={}

    return render(request, 'tasks/home.html', context)

def updateTask(request, pk):
    task = Task.objects.get(id=pk)

    form  = TaskForm(instance=task)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid:
            form.save()
            #messages.info(request,"{} got updated".format(task))
            return redirect('user')
    
    
    context = {'form':form}
    return render(request,'tasks/update_task.html',context)

def deleteTask(request, pk):
    item = Task.objects.get(id = pk)

    if request.method == 'POST':
        item.delete()
        return redirect('user')


    context = {'item':item}
    return render(request, 'tasks/delete.html',context)

def userPage(request):
    tasks = Task.objects.filter(my_user=request.user)

    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid:
            Task_form = form.save(commit=False)
            Task_form.my_user = request.user
            Task_form.save()
        return redirect('user')

    context ={'TASKS':tasks, 'form':form}

    return render(request,'tasks/user.html',context)

def AboutusPage(request):

    context = {}

    return render(request,'tasks/Aboutus.html',context)


def ContactusPage(request):

    context = {}

    return render(request,'tasks/Contactus.html',context)


def TeamPage(request):

    context = {}

    return render(request,'tasks/Team.html',context)


def PrivacyPolicyPage(request):

    context = {}

    return render(request,'tasks/PrivacyPolicy.html',context)


def PricingPage(request):

    context = {}

    return render(request,'tasks/Pricing.html',context)


def PremiumPage(request):

    context = {}

    return render(request,'tasks/Premium.html',context)



def ActivateAccountView(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except Exception as identifier:
        user = None
    if user is not None and token_generator.check_token(user, token):
        user.save()
        messages.add_message(request,messages.INFO,'ACCOUNT IS ACTIVATED SUCCESSFULLY')
        return redirect('login')
    else:
        return render(request,'tasks/activate_failed.html',status=401)