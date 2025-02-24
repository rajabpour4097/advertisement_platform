from django.urls import path
from account.views import CustomLogoutView
from advplatform.views import (
                                AboutUs,
                                ContactUs,
                                CustomLoginView,
                                campaigns_list,
                                custom_404_view,
                                home_view, mentors_list,
                                portfolios_list, 
                              )


app_name = 'adv'

handler404 = custom_404_view



urlpatterns = [
    path('', home_view, name='home'),
    path('mentors/', mentors_list, name='mentors'),
    path('portfolios/', portfolios_list, name='portfolios'),
    path('campaigns/', campaigns_list, name='campaigns'),
    path('aboutus/', AboutUs.as_view(), name='aboutus'),
    path('contactus/', ContactUs.as_view(), name='contactus'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]