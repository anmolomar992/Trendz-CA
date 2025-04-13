from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .utils import is_admin

class AdminMiddleware:
    """
    Middleware to handle admin-specific behavior:
    1. Redirect admins to dashboard if they try to access other pages
    2. Redirect non-admins to home if they try to access admin pages
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view to check user permissions."""
        user_data = request.session.get('user')
        
        # Skip for login, logout, static and media files
        if (
            request.path.startswith('/login') or 
            request.path.startswith('/logout') or
            request.path.startswith('/static') or
            request.path.startswith('/media')
        ):
            return None
            
        # Admin pages/dashboard
        if request.path.startswith('/dashboard'):
            if not user_data or not is_admin(user_data):
                messages.error(request, "You don't have permission to access the admin dashboard.")
                return redirect('home')
            return None
        
        # For admin users, redirect to dashboard if they try to access non-admin pages
        if user_data and is_admin(user_data) and not request.path.startswith('/dashboard'):
            return redirect('dashboard')
            
        return None