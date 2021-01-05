from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator



# Create your models here.

class MyUserManager(BaseUserManager):
    
    def create_user(self, phone, username, password=None, is_active=True, is_staff=False, is_admin=False):
        # import pdb; pdb.set_trace()
        if not phone:
            raise ValueError("User must have a phone number")
        if not username:
            raise ValueError("User must have an username")
        if not password:
            raise ValueError("User must have a password")

        user_obj = self.model(phone=phone)

        user_obj.set_password(password)

        user_obj.username = username
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, username, password=None):
        user = self.create_user(
            phone,
            username,
            password=password,
            is_staff=True
        )

        return user

    def create_superuser(self, phone, username, password=None):
        user = self.create_user(
            phone,
            username,
            password=password,
            is_staff=True,
            is_admin=True
        )

        return user

class MyUser(AbstractBaseUser, PermissionsMixin):
    #user = models.OneToOneField(MyUser, null=True, blank=True, on_delete=models.CASCADE, related_name='myuser')
    username = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)

    password = models.CharField(max_length=16)
    
    confirm_password = models.CharField(max_length=16)

    email = models.EmailField(max_length=200)
    
    #If you want to use regex as validation than use below & pass it as validator in "phone" field:
    #phoneregex = RegexValidator(regex="^[0-9]{10}$")

    phone = models.CharField(max_length=10, unique=True)
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=500)

    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    
    #timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = ['username']   #It will take 'phone' and 'password' as required one, by default 

    objects = MyUserManager()

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return self.username
    
    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class Task(models.Model):
    my_user = models.ForeignKey(MyUser, null=True, on_delete=models.SET_NULL, related_name='task')
    title = models.CharField(max_length=200, null=False)
    description = models.TextField()
    complete = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def task_description(self):
        return self.description
    
    class Meta:
        ordering = ['-date_created']


class SMTPTable(models.Model):
    name = models.CharField(max_length=120, unique=True)
    backend = models.CharField(max_length=500)
    host = models.CharField(max_length=500)
    port = models.IntegerField()
    tls = models.BooleanField(default=True)
    user = models.EmailField(max_length=200)
    user_password = models.CharField(max_length=20)

    def __str__(self):
        return self.name