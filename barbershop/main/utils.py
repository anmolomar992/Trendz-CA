from datetime import datetime, timedelta, time
import hashlib
import json
from .supabase import supabase

def hash_password(password):
    """Hash a password for storage."""
    # In production, use a proper password hashing library
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    """Check if a password matches the hashed version."""
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()

def get_available_time_slots(date_str, stylist_id, service_id):
    """Get available time slots for a given date, stylist, and service."""
    # Convert to datetime object
    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return []
    
    # By default, use standard hours from 9 AM to 8 PM for all days
    default_opening_time = time(9, 0)  # 9:00 AM
    default_closing_time = time(20, 0) # 8:00 PM
    
    # Get day of week (0 = Monday, 6 = Sunday)
    day_of_week = booking_date.weekday()
    
    # Check for custom hours in the database
    business_hours = supabase.select(
        'business_hours',
        filter_column='day_of_week',
        filter_value=day_of_week
    )
    
    # If there are custom hours, use them
    if business_hours and 'error' not in business_hours and len(business_hours) > 0:
        if business_hours[0].get('is_closed', False):
            return []  # Closed on this day
        
        try:
            opening_time = datetime.strptime(business_hours[0]['opening_time'], '%H:%M:%S').time()
            closing_time = datetime.strptime(business_hours[0]['closing_time'], '%H:%M:%S').time()
        except (KeyError, ValueError, IndexError):
            # Fall back to defaults if there's an error
            opening_time = default_opening_time
            closing_time = default_closing_time
    else:
        # If no business hours entry, use default hours
        opening_time = default_opening_time
        closing_time = default_closing_time
    
    # Get service duration
    service = supabase.select('services', columns='duration', filter_column='id', filter_value=service_id)
    if not service or 'error' in service:
        return []
    
    try:
        duration_minutes = int(service[0]['duration'])
    except (KeyError, ValueError, IndexError):
        return []
    
    # Generate time slots at 30-minute intervals
    time_slots = []
    current_time = datetime.combine(booking_date, opening_time)
    end_time = datetime.combine(booking_date, closing_time)
    
    while current_time + timedelta(minutes=duration_minutes) <= end_time:
        time_slot = current_time.time().strftime('%H:%M')
        time_slots.append(time_slot)
        current_time += timedelta(minutes=30)
    
    # Get existing appointments for the day and stylist
    appointments = supabase.select(
        'appointments',
        columns='time',
        filter_column='date',
        filter_value=date_str
    )
    
    if appointments and 'error' not in appointments:
        for appointment in appointments:
            try:
                # Filter by stylist if stylist_id is provided
                if 'stylist_id' in appointment and int(appointment['stylist_id']) == int(stylist_id):
                    appt_time = appointment['time']
                    if appt_time in time_slots:
                        time_slots.remove(appt_time)
            except (KeyError, ValueError):
                continue
    
    return time_slots

def is_admin(user_data):
    """Check if the user has admin privileges."""
    return user_data and user_data.get('role') == 'admin'

def format_price(price):
    """Format price with currency symbol."""
    try:
        return f"₹{float(price):.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

def get_upcoming_appointments(user_id=None):
    """Get upcoming appointments for a user or all upcoming appointments if user_id is None."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user_id:
        appointments = supabase.select(
            'appointments',
            filter_column='user_id',
            filter_value=user_id,
            order='date.asc,time.asc'
        )
    else:
        appointments = supabase.select(
            'appointments',
            order='date.asc,time.asc'
        )
    
    # Filter out past appointments
    upcoming = []
    if appointments and 'error' not in appointments:
        for appointment in appointments:
            try:
                appt_date = appointment['date']
                if appt_date >= today:
                    upcoming.append(appointment)
            except (KeyError, ValueError):
                continue
    
    return upcoming

def get_stylist_details(stylist_id):
    """Get details of a stylist including services offered."""
    stylist = supabase.select('stylists', filter_column='id', filter_value=stylist_id)
    
    if not stylist or 'error' in stylist:
        return None
    
    stylist_data = stylist[0]
    
    # Get services offered by the stylist
    stylist_services = supabase.select(
        'stylist_services',
        filter_column='stylist_id',
        filter_value=stylist_id
    )
    
    service_ids = []
    if stylist_services and 'error' not in stylist_services:
        service_ids = [ss['service_id'] for ss in stylist_services]
    
    services = []
    if service_ids:
        for service_id in service_ids:
            service = supabase.select('services', filter_column='id', filter_value=service_id)
            if service and 'error' not in service:
                services.append(service[0])
    
    stylist_data['services'] = services
    
    return stylist_data

def get_service_with_category(service_id):
    """Get service details including its category."""
    service = supabase.select('services', filter_column='id', filter_value=service_id)
    
    if not service or 'error' in service:
        return None
    
    service_data = service[0]
    
    # Get category
    category = supabase.select(
        'service_categories',
        filter_column='id',
        filter_value=service_data['category_id']
    )
    
    if category and 'error' not in category:
        service_data['category'] = category[0]
    
    return service_data
