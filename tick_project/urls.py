urls_ = """tick_project URL Configuration

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

from Tick_server.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup-customer/phone-auth/', SignUpFirstCustomer.as_view()),
    path('signup-customer/confirm-phone/', SignUpSecondCustomer.as_view()),
    path('signup-customer/resend-code/', ResendCodeCustomer.as_view()),
    path('signup-customer/complete-info/', SignUpFinalCustomer.as_view()),
    path('login-customer/', LoginCustomer.as_view()),
    path('edit-profile-customer/', EditCustomerProfile.as_view()),
    path('customer-logout/', LogoutViewCustomer.as_view()),
    path('signup-salesman/email-auth/', SignUpFirstSalesman.as_view()),
    path('signup-salesman/confirm-email/', SignUpSecondSalesman.as_view()),
    path('signup-salesman/resend-code/', ResendCodeSalesman.as_view()),
    path('signup-salesman/complete-info/', SignUpFinalSalesman.as_view()),
    path('login-salesman/', LoginSalesman.as_view()),
    path('salesman-logout/', LogoutViewSalesman.as_view()),
    path('discounts/active/', ActiveDiscountListView.as_view()),
    path('discounts/inactive/', InactiveDiscountListView.as_view()),
    path('add-shop/', AddShop.as_view()),
    path('add-discount/', AddDiscount.as_view()),
    # path('discount-to-customer/', DiscountToCustomer.as_view()),
    path('cities/', GetCities.as_view()),
    path('shop-kinds/', GetShopKinds.as_view()),
    path('edit-profile-salesman/', EditSalesmanProfileView.as_view()),
    path('add-poll/', AddPoll.as_view()),
    path('submit-poll/', SubmitPoll.as_view()),
    path('my-polls/', MyPolls.as_view()),
    path('poll-to-customer/', PollToCustomer.as_view()),
    path('edit-shop/', EditShop.as_view()),
    path('shops/', GetShops.as_view())
]
