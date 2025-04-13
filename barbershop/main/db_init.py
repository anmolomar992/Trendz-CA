from .supabase import supabase
import time

def initialize_database():
    """
    Initialize the database with default data if needed.
    
    This function checks if the required tables exist in Supabase and 
    adds default data if tables are empty. Note: In Supabase, tables need 
    to be created manually through the Dashboard. This function will only
    populate them with default data.
    """
    print("Initializing database...")
    
    try:
        # 1. Check and create default service categories
        print("Checking service categories...")
        try:
            categories = supabase.select('service_categories')
            
            # Add default service categories if none exist
            if not categories or len(categories) == 0:
                print("Adding default service categories...")
                categories = [
                    {
                        "name": "Haircuts",
                        "description": "Premium haircut services for men"
                    },
                    {
                        "name": "Beard & Shave",
                        "description": "Expert beard grooming and shaving services"
                    },
                    {
                        "name": "Hair Treatments",
                        "description": "Specialized hair treatments and therapies"
                    },
                    {
                        "name": "Facials",
                        "description": "Refreshing facials and skincare treatments"
                    },
                    {
                        "name": "Packages",
                        "description": "Combination packages for complete grooming"
                    }
                ]
                
                for category in categories:
                    result = supabase.insert("service_categories", category)
                    if 'error' in result:
                        print(f"Error adding category {category['name']}: {result['error']}")
        except Exception as e:
            print(f"Error checking service categories: {str(e)}")
        
        # 2. Check and create default business hours
        print("Checking business hours...")
        try:
            hours = supabase.select('business_hours')
            
            # Add default business hours if none exist
            if not hours or len(hours) == 0:
                print("Adding default business hours...")
                for day in range(7):  # 0 = Monday, 6 = Sunday
                    # All days have same hours: 9 AM to 8 PM (per user request)
                    opening_time = "09:00:00"
                    closing_time = "20:00:00"
                    
                    # No days are closed (all days available)
                    is_closed = False
                    
                    # Insert business hours
                    hours_data = {
                        "day_of_week": day,
                        "opening_time": opening_time,
                        "closing_time": closing_time,
                        "is_closed": is_closed
                    }
                    result = supabase.insert("business_hours", hours_data)
                    if 'error' in result:
                        print(f"Error adding business hours for day {day}: {result['error']}")
        except Exception as e:
            print(f"Error checking business hours: {str(e)}")
        
        # 3. Check and create default admin user
        print("Checking for admin users...")
        try:
            # Try to get users with role='admin'
            users = supabase.select('users', filter_column='role', filter_value='admin')
            
            # Add default admin user if none exist
            if not users or len(users) == 0:
                print("Adding default admin user...")
                from .utils import hash_password
                
                admin_data = {
                    "username": "admin",
                    "password": hash_password("admin123"),  # Hashed password
                    "email": "admin@royalcuts.com",
                    "phone_number": "+919876543210",
                    "role": "admin"
                }
                result = supabase.insert("users", admin_data)
                if 'error' in result:
                    print(f"Error adding admin user: {result['error']}")
                
                # Add a regular test user as well
                test_user_data = {
                    "username": "testuser",
                    "password": hash_password("password123"),  # Hashed password
                    "email": "testuser@example.com",
                    "phone_number": "+911234567890",
                    "role": "user"
                }
                
                print("Adding test user for demonstration...")
                test_result = supabase.insert("users", test_user_data)
                if 'error' in test_result:
                    print(f"Error adding test user: {test_result['error']}")
                else:
                    print("Test user created successfully.")
        except Exception as e:
            print(f"Error checking admin users: {str(e)}")
            
        # 4. Check and create default services
        print("Checking services...")
        try:
            services = supabase.select('services')
            
            # Add default services if none exist
            if not services or len(services) == 0:
                print("Adding default services...")
                # First get category IDs
                categories = supabase.select('service_categories')
                
                if categories and len(categories) > 0:
                    # Map category names to IDs
                    category_map = {}
                    for cat in categories:
                        category_map[cat['name']] = cat['id']
                    
                    # Default services
                    services = [
                        {
                            "name": "Royal Haircut",
                            "description": "Our signature premium haircut with personalized styling",
                            "category_id": category_map.get("Haircuts"),
                            "price": 699,
                            "duration": 45,
                            "is_active": True
                        },
                        {
                            "name": "Beard Trim & Shape",
                            "description": "Expert beard grooming service",
                            "category_id": category_map.get("Beard & Shave"),
                            "price": 349,
                            "duration": 30,
                            "is_active": True
                        },
                        {
                            "name": "Hair Color",
                            "description": "Professional coloring with premium products",
                            "category_id": category_map.get("Hair Treatments"),
                            "price": 1299,
                            "duration": 90,
                            "is_active": True
                        },
                        {
                            "name": "Royal Facial",
                            "description": "Luxurious facial treatment for men",
                            "category_id": category_map.get("Facials"),
                            "price": 899,
                            "duration": 60,
                            "is_active": True
                        },
                        {
                            "name": "Complete Package",
                            "description": "Haircut, beard trim, facial, and hair treatment",
                            "category_id": category_map.get("Packages"),
                            "price": 2499,
                            "duration": 120,
                            "is_active": True
                        }
                    ]
                    
                    for service in services:
                        if service["category_id"]:  # Only add if category exists
                            result = supabase.insert("services", service)
                            if 'error' in result:
                                print(f"Error adding service {service['name']}: {result['error']}")
        except Exception as e:
            print(f"Error checking services: {str(e)}")
        
        # 5. Check and create default stylists
        print("Checking stylists...")
        try:
            stylists = supabase.select('stylists')
            
            # Add default stylists if none exist
            if not stylists or len(stylists) == 0:
                print("Adding default stylists...")
                # Default stylists
                stylists = [
                    {
                        "name": "Rajesh Kumar",
                        "bio": "Master stylist with 15 years of experience in premium salons",
                        "profile_image": "https://images.unsplash.com/photo-1580518324671-c2f0833a3af3",
                        "experience_years": 15,
                        "is_active": True
                    },
                    {
                        "name": "Vikram Singh",
                        "bio": "Beard grooming specialist with a passion for traditional techniques",
                        "profile_image": "https://images.unsplash.com/photo-1621605815971-fbc98d665033",
                        "experience_years": 8,
                        "is_active": True
                    },
                    {
                        "name": "Anil Sharma",
                        "bio": "Expert in modern haircuts and trending styles",
                        "profile_image": "https://images.unsplash.com/photo-1618077360395-f3068be8e001",
                        "experience_years": 5,
                        "is_active": True
                    }
                ]
                
                for stylist in stylists:
                    result = supabase.insert("stylists", stylist)
                    if 'error' in result:
                        print(f"Error adding stylist {stylist['name']}: {result['error']}")
                
                # After adding stylists, associate them with services
                # First get all stylists and services
                time.sleep(1)  # Wait a moment for previous operations to complete
                stylists = supabase.select('stylists')
                services = supabase.select('services')
                
                if stylists and services and len(stylists) > 0 and len(services) > 0:
                    # Associate each stylist with certain services
                    for stylist in stylists:
                        for service in services:
                            # Skip some combinations to make it realistic
                            if (stylist['name'] == 'Vikram Singh' and service['name'] in ['Hair Color', 'Royal Facial']):
                                continue
                            if (stylist['name'] == 'Anil Sharma' and service['name'] in ['Complete Package']):
                                continue
                                
                            stylist_service = {
                                "stylist_id": stylist['id'],
                                "service_id": service['id']
                            }
                            
                            result = supabase.insert("stylist_services", stylist_service)
                            if 'error' in result:
                                print(f"Error associating stylist {stylist['name']} with service {service['name']}: {result['error']}")
        except Exception as e:
            print(f"Error checking stylists: {str(e)}")
            
        print("Database initialization completed")
        return True
    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        return False