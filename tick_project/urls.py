from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include

from Tick_server.views import *
from tick_project import settings

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
urlpatterns_customer = [
    url('signup/phone-auth/', SignUpFirstCustomer.as_view(),
        name = 'Signup_Customer_first_step,_Phone_authentication'),
    url('signup/confirm-phone/', SignUpSecondCustomer.as_view(),
        name = 'Signup_Customer_second_step,_Code_authentication'),
    url('signup/complete-info/', SignUpFinalCustomer.as_view(),
        name = 'Signup_Customer_final_step,_Complete_information'),
    url('signup/resend-code/', ResendCodeCustomer.as_view(),
        name = "Signup_Customer,_Resend_code_to_customer_phone"),
    url('login/', LoginCustomer.as_view(), name = 'Login_customer'),
    url('edit-profile/', EditCustomerProfile.as_view(), name = 'Edit_profile_of_customer'),
    url('logout/', LogoutViewCustomer.as_view(), name = 'Logout_customer'),
    url('discounts/active/', ActiveDiscountListView.as_view(),
        name = 'Get_customer_active_discounts_by_page_and_offset'),
    url('discounts/inactive/', InactiveDiscountListView.as_view(),
        name = 'Get_customer_inactive_discounts_by_page_and_offset'),
    url('submit-poll/', SubmitPoll.as_view(), name = 'submit_poll_by_customer'),
    url('my-polls/', MyPolls.as_view(), name = 'Get_customer_active_(not_completed)_polls'),
    url('shops/', GetShops.as_view(), name = 'Get_all_shops_with_some_criteria_by_page_and_offset'),
    url('ads/', GetAds.as_view(), name = 'Get_ads_for_a_shop'),
]

urlpatterns_salesman = [
    url('signup/email-auth/', SignUpFirstSalesman.as_view(),
        name = 'Signup_Salesman_first_step,_email_authentication'),
    url('signup/confirm-email/', SignUpSecondSalesman.as_view(),
        name = 'Signup_Salesman_second_step,_Code_authentication'),
    url('signup/complete-info/', SignUpFinalSalesman.as_view(),
        name = 'Signup_Salesman_final_step,_Complete_information'),
    url('signup/resend-code/', ResendCodeSalesman.as_view(),
        name = 'Signup_Salesman,_Resend_code_to_salesman_email'),
    url('login/', LoginSalesman.as_view(), name = 'Login_salesman'),
    url('edit-profile/', EditSalesmanProfileView.as_view(), name = 'Edit_profile_of_salesman'),
    url('logout/', LogoutViewSalesman.as_view(), name = 'Logout_salesman'),
    url('add-shop/', AddShop.as_view(), name = 'Add_new_shop_by_salesman'),
    url('edit-shop/', EditShop.as_view(), name = 'Edit_shop_by_salesman'),
    url('get-shop/', GetShopById.as_view(), name = 'Get_shop_information_by_id'),
    url('add-discount/', AddDiscount.as_view(), name = 'Add_new_discount_for_shop_by_salesman'),
    url('add-poll/', AddPoll.as_view(), name = 'Add_new_poll_for_shop_by_salesman'),
    url('poll-to-customer/', PollToCustomer.as_view(), name = 'Assign_poll_to_customer_by_salesman'),
    url('add-advertisement/', AddAdvertise.as_view(), name = 'Add_new_advertise_for_shop'),
    url('apply-discount/', ApplyDiscount.as_view(), name = 'apply_discount_for_customer'),
    url('statistics/', Statistics.as_view(), name = 'show_statistics_for_shop'),
    url('shops/', SalesmanShops.as_view(), name = 'show_all_shops'),
    url('polls/', SalesmanPolls.as_view(), name = 'show_all_polls')
]

urlpatterns = [
    url(r'^', include('drf_autodocs.urls')),
    url(r'^silk/', include('silk.urls', namespace = 'silk')),
    url('admin/', admin.site.urls),
    url('cities/', GetCities.as_view(), name = 'Get_all_cities'),
    url('shop-kinds/', GetShopKinds.as_view(), name = 'get_all_shop_kinds'),
    url('customer/', include((urlpatterns_customer, 'Tick_server'), namespace = 'Customer requests')),
    url('salesman/', include((urlpatterns_salesman, 'Tick_server'), namespace = 'Salesman requests')),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
