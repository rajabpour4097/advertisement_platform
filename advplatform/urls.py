from django.urls import path
from django.contrib.auth import views as auth_views
from advplatform.views import CustomLoginView, about_us, contact_us, home_view, mentors_list, portfolios_list, signup_page


urlpatterns = [
    path('', home_view, name='home'),
    path('mentors/', mentors_list, name='mentors'),
    path('portfolios/', portfolios_list, name='portfolios'),
    path('aboutus/', about_us, name='aboutus'),
    path('contactus/', contact_us, name='contactus'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup_page, name='signuppage'),
    
]