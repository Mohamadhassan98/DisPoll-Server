"""tick_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from Tick_server.views import SignUpFirst, SignUpSecond, ResendCode, Login, SignUpFinal, ActiveDiscountListView, \
    InactiveDiscountListView, SignUpFirstSalesman, SignUpSecondSalesman, ResendCodeSalesman, SignUpFinalSalesman, \
    LoginSalesman, AddShop

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup-customer/phone-auth/', SignUpFirst.as_view()),
    path('signup-customer/confirm-phone/', SignUpSecond.as_view()),
    path('signup-customer/resend-code/', ResendCode.as_view()),
    path('signup-customer/complete-info/', SignUpFinal.as_view()),
    path('login-customer/', Login.as_view()),
    path('signup-salesman/email-auth/', SignUpFirstSalesman.as_view()),
    path('signup-salesman/confirm-email/', SignUpSecondSalesman.as_view()),
    path('signup-salesman/resend-code/', ResendCodeSalesman.as_view()),
    path('signup-salesman/complete-info/', SignUpFinalSalesman.as_view()),
    path('login-salesman/', LoginSalesman.as_view()),
    path('discounts/active/', ActiveDiscountListView.as_view()),
    path('discounts/inactive/', InactiveDiscountListView.as_view()),
    path('add-shop/', AddShop.as_view()),
]
