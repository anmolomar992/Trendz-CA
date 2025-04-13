from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('services/', views.services_view, name='services'),
    path('services/<int:service_id>/', views.service_detail_view, name='service_detail'),
    path('stylists/', views.stylists_view, name='stylists'),
    path('stylists/<int:stylist_id>/', views.stylist_detail_view, name='stylist_detail'),
    path('booking/', views.booking_view, name='booking'),
    path('booking/success/', views.booking_success_view, name='booking_success'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('profile/', views.profile_view, name='profile'),
    
    # AJAX endpoints
    path('api/time-slots/', views.get_time_slots, name='get_time_slots'),
    
    # Admin dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/appointments/', views.dashboard_appointments_view, name='dashboard_appointments'),
    path('dashboard/services/', views.dashboard_services_view, name='dashboard_services'),
    path('dashboard/stylists/', views.dashboard_stylists_view, name='dashboard_stylists'),
    path('dashboard/reviews/', views.dashboard_reviews_view, name='dashboard_reviews'),
    
    # Admin delete operations
    path('dashboard/services/delete/<int:service_id>/', views.delete_service_view, name='delete_service'),
    path('dashboard/stylists/delete/<int:stylist_id>/', views.delete_stylist_view, name='delete_stylist'),
]
