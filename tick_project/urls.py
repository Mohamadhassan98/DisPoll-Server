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
    InactiveDiscountListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/phone-auth', SignUpFirst.as_view(), name = 'signup_first'),
    path('signup/confirm-phone', SignUpSecond.as_view(), name = 'signup_second'),
    path('signup/resend-code', ResendCode.as_view(), name = 'resend_code'),
    path('signup/complete-info', SignUpFinal.as_view(), name = 'signup_final'),
    path('login/', Login.as_view(), name = 'login'),
    path('/discounts/active', ActiveDiscountListView.as_view(), name = 'active_discounts'),
    path('/discounts/inactive', InactiveDiscountListView.as_view(), name = 'inactive_discounts')
]
