from django.urls import path
from account.views import CustomLogoutView
from advplatform.views import CustomLoginView, about_us, contact_us, home_view, mentors_list, portfolios_list, signup_page


app_name = 'adv'

urlpatterns = [
    path('', home_view, name='home'),
    path('mentors/', mentors_list, name='mentors'),
    path('portfolios/', portfolios_list, name='portfolios'),
    path('aboutus/', about_us, name='aboutus'),
    path('contactus/', contact_us, name='contactus'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', signup_page, name='signuppage'),
    
]