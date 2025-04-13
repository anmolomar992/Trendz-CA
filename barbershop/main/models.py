from django.db import models

# Since we're using Supabase, we don't need Django ORM models for database access.
# However, we'll create model classes to represent our tables for type hints and validation.

class User:
    """Represents a user from the users table."""
    def __init__(self, id=None, username=None, password=None, email=None, phone_number=None, 
                 role='user', created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.phone_number = phone_number
        self.role = role
        self.created_at = created_at

class ServiceCategory:
    """Represents a service category from the service_categories table."""
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

class Service:
    """Represents a service from the services table."""
    def __init__(self, id=None, name=None, description=None, category_id=None, 
                 price=None, duration=None, is_active=True):
        self.id = id
        self.name = name
        self.description = description
        self.category_id = category_id
        self.price = price
        self.duration = duration
        self.is_active = is_active

class Stylist:
    """Represents a stylist from the stylists table."""
    def __init__(self, id=None, name=None, bio=None, profile_image=None, 
                 experience_years=None, is_active=True, user_id=None):
        self.id = id
        self.name = name
        self.bio = bio
        self.profile_image = profile_image
        self.experience_years = experience_years
        self.is_active = is_active
        self.user_id = user_id

class StylistService:
    """Represents a stylist service from the stylist_services table."""
    def __init__(self, id=None, stylist_id=None, service_id=None):
        self.id = id
        self.stylist_id = stylist_id
        self.service_id = service_id

class BusinessHours:
    """Represents business hours from the business_hours table."""
    def __init__(self, id=None, day_of_week=None, opening_time=None, 
                 closing_time=None, is_closed=False):
        self.id = id
        self.day_of_week = day_of_week
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.is_closed = is_closed

class Appointment:
    """Represents an appointment from the appointments table."""
    def __init__(self, id=None, user_id=None, customer_name=None, customer_phone=None,
                 service_id=None, stylist_id=None, date=None, time=None, 
                 status='scheduled', special_requests=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.service_id = service_id
        self.stylist_id = stylist_id
        self.date = date
        self.time = time
        self.status = status
        self.special_requests = special_requests
        self.created_at = created_at

class Review:
    """Represents a review from the reviews table."""
    def __init__(self, id=None, user_id=None, service_id=None, stylist_id=None,
                 appointment_id=None, rating=None, comment=None, 
                 is_approved=False, created_at=None):
        self.id = id
        self.user_id = user_id
        self.service_id = service_id
        self.stylist_id = stylist_id
        self.appointment_id = appointment_id
        self.rating = rating
        self.comment = comment
        self.is_approved = is_approved
        self.created_at = created_at
