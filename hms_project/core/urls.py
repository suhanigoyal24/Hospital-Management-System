from django.urls import path  
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('redirect-after-login/', views.after_login_redirect, name='after_login_redirect'),
    
    # Patient URLs
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/doctor/<int:doctor_id>/slots/', views.doctor_slots, name='doctor_slots'),

    # Booking URLs
    path('book/<int:slot_id>/', views.book_and_notify, name='book_slot'),

    # Doctor URLs
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/add-slot/', views.add_slot, name='add_slot'),
    path('doctor/delete-slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),
]
