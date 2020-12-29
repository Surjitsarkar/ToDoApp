from django.urls import path
from tasks import views
from .views import *

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    
    path('',views.home, name='home'),
    path('user/', views.userPage, name='user'),

    path('update_task/<str:pk>/',views.updateTask, name='update_task'),
    path('delete/<str:pk>/',views.deleteTask    , name='delete'),

    path('AboutUs/', views.AboutusPage, name='AboutUs'),
    path('ContactUs/', views.ContactusPage, name='ContactUs'),
    path('Team/', views.TeamPage, name='Team'),
    path('PrivacyPolicy/', views.PrivacyPolicyPage, name='PrivacyPolicy'),
    path('Premium/', views.PremiumPage, name='Premium'),
    path('Pricing/', views.PricingPage, name='Pricing'),

    path('activate/<uidb64>/<token>',views.ActivateAccountView,name='activate'),
]