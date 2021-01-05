from django.urls import path
from tasks import views
from .views import *

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    
    path('',views.home, name='home'),
    path('user/', views.userPage, name='user'),
    path('update/<str:pk>/',views.updateTask, name='update'),
    path('delete/<str:pk>/',views.deleteTask, name='delete'),

    path('aboutus/', views.aboutuspage, name='aboutus'),
    path('contactus/', views.contactuspage, name='contactus'),
    path('privacypolicy/', views.privacypolicypage, name='privacypolicy'),
    path('premium/', views.premiumpage, name='premium'),
    path('pricing/', views.pricingpage, name='pricing'),
    path('team/', views.teampage, name='team'),

    path('activate/<uidb64>/<token>',views.ActivateAccountView,name='activate'),
]