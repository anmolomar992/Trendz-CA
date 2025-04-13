from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.html import escape
import json
from datetime import datetime, timedelta, date

from .supabase import supabase
from .forms import (
    LoginForm, SignupForm, BookingForm, ReviewForm, 
    ServiceForm, StylistForm
)
from .utils import (
    hash_password, check_password, get_available_time_slots,
    is_admin, format_price, get_upcoming_appointments,
    get_stylist_details, get_service_with_category
)

def home(request):
    """View for the home page."""
    # Get services for showcase
    services = supabase.select(
        'services', 
        columns='id,name,description,price',
        filter_column='is_active',
        filter_value='true',
        order='price.asc',
        range_from=0,
        range_to=3
    )
    
    # Get top stylists
    stylists = supabase.select(
        'stylists',
        columns='id,name,bio,profile_image,experience_years',
        filter_column='is_active',
        filter_value='true',
        range_from=0,
        range_to=4
    )
    
    # Get recent reviews
    reviews = supabase.select(
        'reviews',
        columns='id,rating,comment,created_at',
        filter_column='is_approved',
        filter_value='true',
        order='created_at.desc',
        range_from=0,
        range_to=3
    )
    
    # Format prices
    if services and 'error' not in services:
        for service in services:
            service['formatted_price'] = format_price(service.get('price', 0))
    
    # Check if user is logged in
    user_data = request.session.get('user')
    
    context = {
        'services': services if services and 'error' not in services else [],
        'stylists': stylists if stylists and 'error' not in stylists else [],
        'reviews': reviews if reviews and 'error' not in reviews else [],
        'user': user_data,
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/index.html', context)

def login_view(request):
    """View for user login."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Additional debugging for admin login
            print(f"Attempting login for user: {username} with password: {'*' * len(password)}")
            
            # Find user by username
            users = supabase.select(
                'users',
                filter_column='username',
                filter_value=username
            )
            
            print(f"Database response: {users}")
            
            if users and 'error' not in users and len(users) > 0:
                user = users[0]
                hashed_password = user.get('password', '')
                
                # Special handling for admin user (directly compare with admin credentials)
                if username == 'admin' and password == 'admin123':
                    print("Admin login successful via direct verification")
                    # Store admin user data in session
                    user_data = {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user.get('email', ''),
                        'phone_number': user.get('phone_number', ''),
                        'role': 'admin'  # Ensure role is set to admin
                    }
                    request.session['user'] = user_data
                    messages.success(request, f"Welcome back, Administrator!")
                    return redirect('dashboard')
                # Normal password check for other users
                elif check_password(hashed_password, password):
                    # Store user data in session
                    user_data = {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user.get('email', ''),
                        'phone_number': user.get('phone_number', ''),
                        'role': user.get('role', 'user')
                    }
                    request.session['user'] = user_data
                    messages.success(request, f"Welcome back, {username}!")
                    
                    # Redirect to dashboard if admin, otherwise to home
                    if user.get('role') == 'admin':
                        return redirect('dashboard')
                    return redirect('home')
                else:
                    print(f"Password verification failed. Provided: {password}, Expected hash: {hashed_password}")
                    messages.error(request, "Invalid password.")
            else:
                messages.error(request, "User not found.")
    else:
        form = LoginForm()
    
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """Log out a user by clearing the session."""
    if 'user' in request.session:
        del request.session['user']
        messages.success(request, "You have been logged out successfully.")
    
    return redirect('home')

def signup_view(request):
    """View for user registration."""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            # Check if username already exists
            existing_users = supabase.select(
                'users',
                filter_column='username',
                filter_value=username
            )
            
            if existing_users and 'error' not in existing_users and len(existing_users) > 0:
                messages.error(request, "Username already taken.")
                return render(request, 'main/signup.html', {'form': form})
            
            # Create new user
            hashed_password = hash_password(password)
            new_user = {
                'username': username,
                'password': hashed_password,
                'email': email,
                'phone_number': phone_number,
                'role': 'user'
            }
            
            result = supabase.insert('users', new_user)
            
            if 'error' in result:
                messages.error(request, f"Registration failed: {result['error']}")
            else:
                messages.success(request, "Registration successful! Please log in.")
                return redirect('login')
    else:
        form = SignupForm()
    
    return render(request, 'main/signup.html', {'form': form})

def services_view(request):
    """View for displaying all services."""
    # Get all service categories
    categories = supabase.select('service_categories', order='name.asc')
    
    # Get services organized by category
    categorized_services = {}
    
    if categories and 'error' not in categories:
        for category in categories:
            services = supabase.select(
                'services',
                filter_column='category_id',
                filter_value=category['id'],
                order='price.asc'
            )
            
            if services and 'error' not in services:
                # Format prices
                for service in services:
                    service['formatted_price'] = format_price(service.get('price', 0))
                
                categorized_services[category['name']] = services
    
    # Check if user is logged in
    user_data = request.session.get('user')
    
    context = {
        'categories': categories if categories and 'error' not in categories else [],
        'categorized_services': categorized_services,
        'user': user_data,
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/services.html', context)

def stylists_view(request):
    """View for displaying all stylists."""
    # Get all stylists
    stylists = supabase.select(
        'stylists',
        columns='id,name,bio,profile_image,experience_years',
        filter_column='is_active',
        filter_value='true',
        order='name.asc'
    )
    
    # Check if user is logged in
    user_data = request.session.get('user')
    
    context = {
        'stylists': stylists if stylists and 'error' not in stylists else [],
        'user': user_data,
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/stylists.html', context)

def stylist_detail_view(request, stylist_id):
    """View for displaying details of a specific stylist and handling review submissions."""
    stylist_data = get_stylist_details(stylist_id)
    
    if not stylist_data:
        messages.error(request, "Stylist not found.")
        return redirect('stylists')
    
    # Get reviews for this stylist
    reviews = supabase.select(
        'reviews',
        filter_column='stylist_id',
        filter_value=stylist_id,
        order='created_at.desc'
    )
    
    # Format service prices
    for service in stylist_data.get('services', []):
        service['formatted_price'] = format_price(service.get('price', 0))
    
    # Check if user is logged in
    user_data = request.session.get('user')
    
    # Initialize review form
    form = None
    
    # If user is logged in, show form for submitting a review
    if user_data:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                rating = form.cleaned_data['rating']
                comment = form.cleaned_data['comment']
                
                # Create review data - just for the stylist (no service or appointment associated)
                review_data = {
                    'user_id': user_data['id'],
                    'stylist_id': stylist_id,
                    'rating': rating,
                    'comment': comment,
                    'is_approved': False  # Require admin approval
                }
                
                # Insert review
                result = supabase.insert('reviews', review_data)
                
                if 'error' in result:
                    messages.error(request, f"Review submission failed: {result['error']}")
                else:
                    messages.success(request, "Thank you for your review! It will be visible after approval.")
                    return redirect('stylist_detail', stylist_id=stylist_id)
        else:
            form = ReviewForm()
    
    context = {
        'stylist': stylist_data,
        'reviews': reviews if reviews and 'error' not in reviews else [],
        'user': user_data,
        'is_admin': is_admin(user_data),
        'form': form
    }
    
    return render(request, 'main/stylist_detail.html', context)

def service_detail_view(request, service_id):
    """View for displaying details of a specific service."""
    service_data = get_service_with_category(service_id)
    
    if not service_data:
        messages.error(request, "Service not found.")
        return redirect('services')
    
    # Format price
    service_data['formatted_price'] = format_price(service_data.get('price', 0))
    
    # Get all active stylists since all stylists provide all services
    stylists = supabase.select(
        'stylists',
        filter_column='is_active', 
        filter_value='true',
        order='name.asc'
    )
    
    # Get reviews for this service
    reviews = supabase.select(
        'reviews',
        filter_column='service_id',
        filter_value=service_id,
        order='created_at.desc'
    )
    
    # Check if user is logged in
    user_data = request.session.get('user')
    
    context = {
        'service': service_data,
        'stylists': stylists,
        'reviews': reviews if reviews and 'error' not in reviews else [],
        'user': user_data,
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/service_detail.html', context)

def booking_view(request):
    """View for booking appointments."""
    # Check if user is logged in
    user_data = request.session.get('user')
    
    # Get active services
    services = supabase.select(
        'services',
        filter_column='is_active',
        filter_value='true',
        order='name.asc'
    )
    
    # Get active stylists
    stylists = supabase.select(
        'stylists',
        filter_column='is_active',
        filter_value='true',
        order='name.asc'
    )
    
    # Default to empty time slots list
    time_slots = []
    
    # Get time slots from form data if available
    selected_date = None
    selected_stylist = None
    selected_service = None
    
    if request.method == 'POST':
        # Get selected values from form data
        selected_date = request.POST.get('date')
        selected_stylist = request.POST.get('stylist')
        selected_service = request.POST.get('service')
        
        # Get time slots if all required values are present
        if selected_date and selected_stylist and selected_service:
            time_slots = get_available_time_slots(selected_date, selected_stylist, selected_service)
            print(f"Available time slots: {time_slots}")
            
        form = BookingForm(request.POST, services=services, stylists=stylists, time_slots=time_slots)
        
        if form.is_valid():
            customer_name = form.cleaned_data['customer_name']
            customer_phone = form.cleaned_data['customer_phone']
            service_id = form.cleaned_data['service']
            stylist_id = form.cleaned_data['stylist']
            date_str = form.cleaned_data['date'].strftime('%Y-%m-%d')
            time_str = form.cleaned_data['time']
            special_requests = form.cleaned_data['special_requests']
            
            # Create appointment data
            appointment_data = {
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'service_id': service_id,
                'stylist_id': stylist_id,
                'date': date_str,
                'time': time_str,
                'special_requests': special_requests,
                'status': 'scheduled'
            }
            
            # Add user_id if logged in
            if user_data:
                appointment_data['user_id'] = user_data['id']
            
            # Check if the time slot is still available
            available_slots = get_available_time_slots(date_str, stylist_id, service_id)
            if time_str not in available_slots:
                messages.error(request, "Sorry, this time slot is no longer available. Please choose another time.")
            else:
                # Insert appointment
                result = supabase.insert('appointments', appointment_data)
                
                if 'error' in result:
                    messages.error(request, f"Booking failed: {result['error']}")
                else:
                    messages.success(request, "Appointment booked successfully!")
                    return redirect('booking_success')
    else:
        # For GET request, create an empty form
        initial_data = {}
        if user_data:
            # Pre-fill customer name with username if logged in
            initial_data['customer_name'] = user_data.get('username', '')
            initial_data['customer_phone'] = user_data.get('phone_number', '')
        
        form = BookingForm(initial=initial_data, services=services, stylists=stylists, time_slots=time_slots)
    
    context = {
        'form': form,
        'services': services if services and 'error' not in services else [],
        'stylists': stylists if stylists and 'error' not in stylists else [],
        'user': user_data,
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/booking.html', context)

@csrf_exempt
def get_time_slots(request):
    """AJAX endpoint to get available time slots for a given date, stylist, and service."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            stylist_id = data.get('stylist_id')
            service_id = data.get('service_id')
            
            if not date_str or not stylist_id or not service_id:
                return JsonResponse({'error': 'Missing required parameters'}, status=400)
            
            # Get time slots
            time_slots = get_available_time_slots(date_str, stylist_id, service_id)
            
            # Log for debugging
            print(f"Available time slots for date={date_str}, stylist={stylist_id}, service={service_id}: {time_slots}")
            
            return JsonResponse({'time_slots': time_slots})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error getting time slots: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def booking_success_view(request):
    """View for successful booking confirmation."""
    # Check if user is logged in
    user_data = request.session.get('user')
    
    context = {
        'user': user_data,
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/booking_success.html', context)

def reviews_view(request):
    """View for displaying and submitting reviews."""
    # Check if user is logged in
    user_data = request.session.get('user')
    
    # Get all approved reviews
    reviews = supabase.select(
        'reviews',
        filter_column='is_approved',
        filter_value='true',
        order='created_at.desc'
    )
    
    # Enhance review data with service and stylist names
    if reviews and 'error' not in reviews:
        for review in reviews:
            # Get service name
            service_id = review.get('service_id')
            if service_id:
                service = supabase.select(
                    'services',
                    columns='name',
                    filter_column='id',
                    filter_value=service_id
                )
                if service and 'error' not in service and len(service) > 0:
                    review['service_name'] = service[0]['name']
            
            # Get stylist name
            stylist_id = review.get('stylist_id')
            if stylist_id:
                stylist = supabase.select(
                    'stylists',
                    columns='name',
                    filter_column='id',
                    filter_value=stylist_id
                )
                if stylist and 'error' not in stylist and len(stylist) > 0:
                    review['stylist_name'] = stylist[0]['name']
    
    # Initialize form for submitting new review
    form = None
    
    # If user is logged in, show form and get their appointments for review
    if user_data:
        # Get user's completed appointments that haven't been reviewed
        appointments = supabase.select(
            'appointments',
            filter_column='user_id',
            filter_value=user_data['id']
        )
        
        completed_appointments = []
        if appointments and 'error' not in appointments:
            for appointment in appointments:
                # Check if appointment is in the past
                try:
                    appt_date = datetime.strptime(appointment['date'], '%Y-%m-%d').date()
                    if appt_date <= datetime.now().date() and appointment['status'] != 'canceled':
                        # Check if already reviewed
                        review_exists = supabase.select(
                            'reviews',
                            filter_column='appointment_id',
                            filter_value=appointment['id']
                        )
                        
                        if not review_exists or 'error' in review_exists or len(review_exists) == 0:
                            # Get service name
                            service = supabase.select(
                                'services',
                                columns='name',
                                filter_column='id',
                                filter_value=appointment['service_id']
                            )
                            
                            # Get stylist name
                            stylist = supabase.select(
                                'stylists',
                                columns='name',
                                filter_column='id',
                                filter_value=appointment['stylist_id']
                            )
                            
                            if service and 'error' not in service and len(service) > 0:
                                appointment['service_name'] = service[0]['name']
                            
                            if stylist and 'error' not in stylist and len(stylist) > 0:
                                appointment['stylist_name'] = stylist[0]['name']
                            
                            completed_appointments.append(appointment)
                except (ValueError, KeyError):
                    continue
        
        # Process review form submission
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                appointment_id = request.POST.get('appointment_id')
                
                # Validate appointment
                appointment = None
                for appt in completed_appointments:
                    if appt['id'] == appointment_id:
                        appointment = appt
                        break
                
                if appointment:
                    rating = form.cleaned_data['rating']
                    comment = form.cleaned_data['comment']
                    
                    # Create review data
                    review_data = {
                        'user_id': user_data['id'],
                        'service_id': appointment['service_id'],
                        'stylist_id': appointment['stylist_id'],
                        'appointment_id': appointment_id,
                        'rating': rating,
                        'comment': comment,
                        'is_approved': False  # Require admin approval
                    }
                    
                    # Insert review
                    result = supabase.insert('reviews', review_data)
                    
                    if 'error' in result:
                        messages.error(request, f"Review submission failed: {result['error']}")
                    else:
                        messages.success(request, "Thank you for your review! It will be visible after approval.")
                        return redirect('reviews')
                else:
                    messages.error(request, "Invalid appointment selected.")
        else:
            form = ReviewForm()
            
        context = {
            'reviews': reviews if reviews and 'error' not in reviews else [],
            'form': form,
            'appointments': completed_appointments,
            'user': user_data,
            'is_admin': is_admin(user_data)
        }
    else:
        context = {
            'reviews': reviews if reviews and 'error' not in reviews else [],
            'user': None,
            'is_admin': False
        }
    
    return render(request, 'main/reviews.html', context)

def profile_view(request):
    """View for user profile and appointment history."""
    # Check if user is logged in
    user_data = request.session.get('user')
    
    if not user_data:
        messages.error(request, "Please log in to view your profile.")
        return redirect('login')
    
    # Get user's appointments
    appointments = supabase.select(
        'appointments',
        filter_column='user_id',
        filter_value=user_data['id'],
        order='date.desc,time.desc'
    )
    
    # Enhance appointment data with service and stylist names
    if appointments and 'error' not in appointments:
        for appointment in appointments:
            # Get service name
            service_id = appointment.get('service_id')
            if service_id:
                service = supabase.select(
                    'services',
                    columns='name,price',
                    filter_column='id',
                    filter_value=service_id
                )
                if service and 'error' not in service and len(service) > 0:
                    appointment['service_name'] = service[0]['name']
                    appointment['service_price'] = format_price(service[0]['price'])
            
            # Get stylist name
            stylist_id = appointment.get('stylist_id')
            if stylist_id:
                stylist = supabase.select(
                    'stylists',
                    columns='name',
                    filter_column='id',
                    filter_value=stylist_id
                )
                if stylist and 'error' not in stylist and len(stylist) > 0:
                    appointment['stylist_name'] = stylist[0]['name']
    
    context = {
        'user': user_data,
        'appointments': appointments if appointments and 'error' not in appointments else [],
        'is_admin': is_admin(user_data)
    }
    
    return render(request, 'main/profile.html', context)

# Function to clean up old appointments
def cleanup_old_appointments():
    """Delete appointments that are more than one day old."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    # Get old appointments (scheduled date before yesterday)
    old_appointments = supabase.select(
        'appointments',
        filter_column='date',
        filter_value=f'lt.{yesterday}'
    )
    
    if old_appointments and 'error' not in old_appointments:
        for appointment in old_appointments:
            # Delete the appointment
            supabase.delete('appointments', appointment['id'])
            
    return len(old_appointments) if old_appointments and 'error' not in old_appointments else 0

def dashboard_view(request):
    """Main admin dashboard view."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
        
    # Cleanup old appointments
    deleted_appointments = cleanup_old_appointments()
    if deleted_appointments > 0:
        messages.info(request, f"System automatically removed {deleted_appointments} old appointments.")
    
    # Get counts for dashboard
    appointment_count = 0
    service_count = 0
    stylist_count = 0
    user_count = 0
    
    # Count appointments
    appointments = supabase.select('appointments')
    if appointments and 'error' not in appointments:
        appointment_count = len(appointments)
    
    # Count services
    services = supabase.select('services')
    if services and 'error' not in services:
        service_count = len(services)
    
    # Count stylists
    stylists = supabase.select('stylists')
    if stylists and 'error' not in stylists:
        stylist_count = len(stylists)
    
    # Count users
    users = supabase.select('users')
    if users and 'error' not in users:
        user_count = len(users)
    
    # Get recent appointments
    recent_appointments = supabase.select(
        'appointments',
        order='created_at.desc',
        range_from=0,
        range_to=5
    )
    
    # Enhance appointment data
    if recent_appointments and 'error' not in recent_appointments:
        for appointment in recent_appointments:
            # Get service name
            service_id = appointment.get('service_id')
            if service_id:
                service = supabase.select(
                    'services',
                    columns='name',
                    filter_column='id',
                    filter_value=service_id
                )
                if service and 'error' not in service and len(service) > 0:
                    appointment['service_name'] = service[0]['name']
            
            # Get stylist name
            stylist_id = appointment.get('stylist_id')
            if stylist_id:
                stylist = supabase.select(
                    'stylists',
                    columns='name',
                    filter_column='id',
                    filter_value=stylist_id
                )
                if stylist and 'error' not in stylist and len(stylist) > 0:
                    appointment['stylist_name'] = stylist[0]['name']
    
    context = {
        'user': user_data,
        'is_admin': True,
        'appointment_count': appointment_count,
        'service_count': service_count,
        'stylist_count': stylist_count,
        'user_count': user_count,
        'recent_appointments': recent_appointments if recent_appointments and 'error' not in recent_appointments else []
    }
    
    return render(request, 'main/dashboard.html', context)

def dashboard_appointments_view(request):
    """Admin view for managing appointments."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Get all appointments
    appointments = supabase.select(
        'appointments',
        order='date.asc,time.asc'
    )
    
    # Enhance appointment data
    if appointments and 'error' not in appointments:
        for appointment in appointments:
            # Get service name
            service_id = appointment.get('service_id')
            if service_id:
                service = supabase.select(
                    'services',
                    columns='name',
                    filter_column='id',
                    filter_value=service_id
                )
                if service and 'error' not in service and len(service) > 0:
                    appointment['service_name'] = service[0]['name']
            
            # Get stylist name
            stylist_id = appointment.get('stylist_id')
            if stylist_id:
                stylist = supabase.select(
                    'stylists',
                    columns='name',
                    filter_column='id',
                    filter_value=stylist_id
                )
                if stylist and 'error' not in stylist and len(stylist) > 0:
                    appointment['stylist_name'] = stylist[0]['name']
    
    # Handle status updates
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')
        
        if appointment_id and new_status:
            # Update appointment status
            result = supabase.update(
                'appointments',
                appointment_id,
                {'status': new_status}
            )
            
            if 'error' in result:
                messages.error(request, f"Failed to update status: {result['error']}")
            else:
                messages.success(request, "Appointment status updated successfully.")
                return redirect('dashboard_appointments')
    
    context = {
        'user': user_data,
        'is_admin': True,
        'appointments': appointments if appointments and 'error' not in appointments else []
    }
    
    return render(request, 'main/dashboard_appointments.html', context)

def dashboard_services_view(request):
    """Admin view for managing services."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Get all service categories
    categories = supabase.select('service_categories', order='name.asc')
    
    # Get all services
    services = supabase.select('services', order='name.asc')
    
    # Enhance service data with category name
    if services and 'error' not in services:
        for service in services:
            # Format price
            service['formatted_price'] = format_price(service.get('price', 0))
            
            # Get category name
            category_id = service.get('category_id')
            if category_id:
                category = supabase.select(
                    'service_categories',
                    columns='name',
                    filter_column='id',
                    filter_value=category_id
                )
                if category and 'error' not in category and len(category) > 0:
                    service['category_name'] = category[0]['name']
    
    # Handle form submission
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'service':
            form = ServiceForm(request.POST, categories=categories)
            
            if form.is_valid():
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                category_id = form.cleaned_data['category']
                price = form.cleaned_data['price']
                duration = form.cleaned_data['duration']
                is_active = form.cleaned_data['is_active']
                
                # Create service data
                service_data = {
                    'name': name,
                    'description': description,
                    'category_id': category_id,
                    'price': str(price),
                    'duration': duration,
                    'is_active': is_active
                }
                
                # Check if editing or adding
                service_id = request.POST.get('service_id')
                
                if service_id:
                    # Update existing service
                    result = supabase.update('services', service_id, service_data)
                    success_message = "Service updated successfully."
                else:
                    # Add new service
                    result = supabase.insert('services', service_data)
                    success_message = "Service added successfully."
                
                if 'error' in result:
                    messages.error(request, f"Failed to save service: {result['error']}")
                else:
                    messages.success(request, success_message)
                    return redirect('dashboard_services')
        
        elif form_type == 'category':
            name = request.POST.get('category_name')
            description = request.POST.get('category_description')
            
            if name:
                # Create category data
                category_data = {
                    'name': name,
                    'description': description
                }
                
                # Add new category
                result = supabase.insert('service_categories', category_data)
                
                if 'error' in result:
                    messages.error(request, f"Failed to add category: {result['error']}")
                else:
                    messages.success(request, "Category added successfully.")
                    return redirect('dashboard_services')
    else:
        form = ServiceForm(categories=categories)
    
    context = {
        'user': user_data,
        'is_admin': True,
        'services': services if services and 'error' not in services else [],
        'categories': categories if categories and 'error' not in categories else [],
        'form': form
    }
    
    return render(request, 'main/dashboard_services.html', context)

def dashboard_stylists_view(request):
    """Admin view for managing stylists."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Get all services for the form
    services = supabase.select('services', order='name.asc')
    
    # Get all stylists
    stylists = supabase.select('stylists', order='name.asc')
    
    # Get stylist services for each stylist
    if stylists and 'error' not in stylists:
        for stylist in stylists:
            stylist_services = supabase.select(
                'stylist_services',
                filter_column='stylist_id',
                filter_value=stylist['id']
            )
            
            service_ids = []
            if stylist_services and 'error' not in stylist_services:
                service_ids = [ss['service_id'] for ss in stylist_services]
            
            stylist['service_ids'] = service_ids
    
    # Handle form submission
    if request.method == 'POST':
        form = StylistForm(request.POST, services=services)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            bio = form.cleaned_data['bio']
            profile_image = form.cleaned_data['profile_image']
            experience_years = form.cleaned_data['experience_years']
            is_active = form.cleaned_data['is_active']
            selected_services = form.cleaned_data['services']
            
            # Create stylist data
            stylist_data = {
                'name': name,
                'bio': bio,
                'profile_image': profile_image,
                'experience_years': experience_years,
                'is_active': is_active
            }
            
            # Check if editing or adding
            stylist_id = request.POST.get('stylist_id')
            
            if stylist_id:
                # Update existing stylist
                result = supabase.update('stylists', stylist_id, stylist_data)
                success_message = "Stylist updated successfully."
            else:
                # Add new stylist
                result = supabase.insert('stylists', stylist_data)
                if 'error' not in result:
                    stylist_id = result[0]['id']
                success_message = "Stylist added successfully."
            
            if 'error' in result:
                messages.error(request, f"Failed to save stylist: {result['error']}")
            else:
                # Update stylist services
                
                # First, remove existing associations
                if stylist_id:
                    # Delete existing stylist_services
                    existing_services = supabase.select(
                        'stylist_services',
                        filter_column='stylist_id',
                        filter_value=stylist_id
                    )
                    
                    if existing_services and 'error' not in existing_services:
                        for es in existing_services:
                            supabase.delete('stylist_services', es['id'])
                
                # Then add new associations
                for service_id in selected_services:
                    stylist_service_data = {
                        'stylist_id': stylist_id,
                        'service_id': service_id
                    }
                    supabase.insert('stylist_services', stylist_service_data)
                
                messages.success(request, success_message)
                return redirect('dashboard_stylists')
    else:
        form = StylistForm(services=services)
    
    context = {
        'user': user_data,
        'is_admin': True,
        'stylists': stylists if stylists and 'error' not in stylists else [],
        'services': services if services and 'error' not in services else [],
        'form': form
    }
    
    return render(request, 'main/dashboard_stylists.html', context)

def delete_service_view(request, service_id):
    """Admin view for deleting a service."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Delete the service
    result = supabase.delete('services', service_id)
    
    if 'error' in result:
        messages.error(request, f"Failed to delete service: {result['error']}")
    else:
        messages.success(request, "Service deleted successfully.")
    
    return redirect('dashboard_services')

def delete_stylist_view(request, stylist_id):
    """Admin view for deleting a stylist."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # First, delete any stylist_services entries for this stylist
    stylist_services = supabase.select(
        'stylist_services',
        filter_column='stylist_id',
        filter_value=stylist_id
    )
    
    if stylist_services and 'error' not in stylist_services:
        for ss in stylist_services:
            supabase.delete('stylist_services', ss['id'])
    
    # Now delete the stylist
    result = supabase.delete('stylists', stylist_id)
    
    if 'error' in result:
        messages.error(request, f"Failed to delete stylist: {result['error']}")
    else:
        messages.success(request, "Stylist deleted successfully.")
    
    return redirect('dashboard_stylists')

def dashboard_reviews_view(request):
    """Admin view for managing reviews."""
    # Check if user is logged in and is admin
    user_data = request.session.get('user')
    
    if not user_data or not is_admin(user_data):
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Get all reviews
    reviews = supabase.select('reviews', order='created_at.desc')
    
    # Enhance review data
    if reviews and 'error' not in reviews:
        for review in reviews:
            # Get username
            user_id = review.get('user_id')
            if user_id:
                user = supabase.select(
                    'users',
                    columns='username',
                    filter_column='id',
                    filter_value=user_id
                )
                if user and 'error' not in user and len(user) > 0:
                    review['username'] = user[0]['username']
            
            # Get service name
            service_id = review.get('service_id')
            if service_id:
                service = supabase.select(
                    'services',
                    columns='name',
                    filter_column='id',
                    filter_value=service_id
                )
                if service and 'error' not in service and len(service) > 0:
                    review['service_name'] = service[0]['name']
            
            # Get stylist name
            stylist_id = review.get('stylist_id')
            if stylist_id:
                stylist = supabase.select(
                    'stylists',
                    columns='name',
                    filter_column='id',
                    filter_value=stylist_id
                )
                if stylist and 'error' not in stylist and len(stylist) > 0:
                    review['stylist_name'] = stylist[0]['name']
    
    # Handle review approval/rejection
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')
        
        if review_id and action:
            if action == 'approve':
                # Approve review
                result = supabase.update('reviews', review_id, {'is_approved': True})
                success_message = "Review approved successfully."
            elif action == 'reject':
                # Delete review
                result = supabase.delete('reviews', review_id)
                success_message = "Review rejected and removed."
            
            if 'error' in result:
                messages.error(request, f"Failed to process review: {result['error']}")
            else:
                messages.success(request, success_message)
                return redirect('dashboard_reviews')
    
    context = {
        'user': user_data,
        'is_admin': True,
        'reviews': reviews if reviews and 'error' not in reviews else []
    }
    
    return render(request, 'main/dashboard_reviews.html', context)
