import pytz
import re

from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.db import models
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView

from ToDo3.settings import *
from tasks.forms import UserRegisterationForm, TaskForm
from tasks.models import *
from .decorators import unauthenticated_user
from .utils import token_generator

# Create your views here.

@unauthenticated_user
def registerPage(request):
    regform = UserRegisterationForm()

    if request.method == "POST":       
        regform = UserRegisterationForm(request.POST)
        if regform.is_valid(): 
            user_form = regform.save(commit=False)
            
            password = regform.cleaned_data.get('password')
            user_email = regform.cleaned_data.get('email')
            name = regform.cleaned_data.get('firstname')
                
            user_form.password=make_password(password)
            user_form.save()
            user_pk = user_form.pk
            
            user = MyUser.objects.get(pk=user_pk)

            email_settings = SMTPTable.objects.get(name='registration')
            my_backend = email_settings.backend
            my_host = email_settings.host
            my_port = email_settings.port
            my_user = email_settings.user
            myuser_password = email_settings.user_password
            my_tls = email_settings.tls

            current_site = get_current_site(request)
            email_subject = 'Activation of your ToDoApp Account'
            message = render_to_string('tasks/email_template.html',
            {
                'user':user, 'domain':current_site.domain, 'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':token_generator.make_token(user), 'name':name,
            }
            )

            connection = mail.get_connection(backend=my_backend,host=my_host, 
                            port=my_port, 
                            username=my_user, 
                            password=myuser_password, 
                            use_tls=my_tls)
            print("Conn ------>",connection)
            connection.open()
            email_registartion = mail.EmailMessage(email_subject,message,my_user,[user_email],connection=connection)
            email_registartion.send()
            connection.close()

            return HttpResponse("Please first confirm your email address to complete the registeration")
    else:
        regform = UserRegisterationForm()

    context = {'myform':regform}
    return render(request,'tasks/register.html',context)


@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user_var = MyUser.objects.get(phone=phone)
        user_mail = user_var.email
        user = authenticate(request, phone=phone, password=password)

        email_settings = SMTPTable.objects.get(name='login')
        my_backend = email_settings.backend
        my_host = email_settings.host
        my_port = email_settings.port
        my_user = email_settings.user
        myuser_password = email_settings.user_password
        my_tls = email_settings.tls
        
        if user is not None:
            login(request, user)
            email_subject = 'Welcome to ToDo App'
            message = render_to_string('tasks/email_template_2.html')

            connection = mail.get_connection(backend=my_backend,host=my_host, 
                            port=my_port, 
                            username=my_user, 
                            password=myuser_password, 
                            use_tls=my_tls)
            connection.open()
            email_login = mail.EmailMessage(email_subject,message,my_user,[user_mail],connection=connection)
            email_login.send()
            connection.close()
            return redirect('user')
        else:
            messages.info(request,'Phone Number or Password is incorrect')

    context = {}
    return render(request,'tasks/login.html',context)

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, 'tasks/home.html')


@login_required(login_url='login')
def updateTask(request, pk):
    task = Task.objects.get(id=pk)
    form  = TaskForm(instance=task)

    user_name = request.user.firstname
    user_mail = request.user.email

    email_settings = SMTPTable.objects.get(name="create_and_update")
    my_backend = email_settings.backend
    my_host = email_settings.host
    my_port = email_settings.port
    my_user = email_settings.user
    myuser_password = email_settings.user_password
    my_tls = email_settings.tls

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid:
            form.save()

            email_subject = 'Update in your ToDo Task'
            message = render_to_string('tasks/email_template_update.html',{'name':user_name})

            connection = mail.get_connection(backend=my_backend,host=my_host, 
                            port=my_port, 
                            username=my_user, 
                            password=myuser_password, 
                            use_tls=my_tls)
            connection.open()
            email_login = mail.EmailMessage(email_subject,message,my_user,[user_mail],connection=connection)
            email_login.send()
            connection.close()
            return redirect('user')
    
    context = {'form':form}
    return render(request,'tasks/user.html',context)


@login_required(login_url='login')
def deleteTask(request, pk):
    item = Task.objects.get(id = pk)

    if request.method == 'POST':
        item.delete()
        return redirect('user')

    context = {'item':item}
    return render(request, 'tasks/delete.html',context)


@login_required(login_url='login')
def userPage(request):
    tasks = Task.objects.filter(my_user=request.user)

    form = TaskForm()

    user_mail = request.user.email
    user_name = request.user.firstname

    email_settings = SMTPTable.objects.get(name="create_and_update")
    my_backend = email_settings.backend
    my_host = email_settings.host
    my_port = email_settings.port
    my_user = email_settings.user
    myuser_password = email_settings.user_password
    my_tls = email_settings.tls

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid:
            Task_form = form.save(commit=False)
            Task_form.my_user = request.user
            Task_form.save()

            email_subject = 'New Creation of task in your ToDo Task'
            message = render_to_string('tasks/email_template_create.html',{'name':user_name})

            connection = mail.get_connection(backend=my_backend,host=my_host, 
                            port=my_port, 
                            username=my_user, 
                            password=myuser_password, 
                            use_tls=my_tls)
            connection.open()
            email_login = mail.EmailMessage(email_subject,message,my_user,[user_mail],connection=connection)
            email_login.send()
            connection.close()
        return redirect('user')

    context ={'TASKS':tasks, 'form':form}

    return render(request,'tasks/user.html',context)

def aboutuspage(request):
    return render(request,'tasks/Aboutus.html')


def contactuspage(request):
    return render(request,'tasks/Contactus.html')


def teampage(request):
    return render(request,'tasks/Team.html')


def privacypolicypage(request):
    return render(request,'tasks/PrivacyPolicy.html')


def pricingpage(request):
    return render(request,'tasks/Pricing.html')


def premiumpage(request):
    return render(request,'tasks/Premium.html')


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