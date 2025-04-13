from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    
    def ready(self):
        """Initialize the app - run the database setup functions."""
        # Import here to avoid circular imports
        try:
            from .db_init import initialize_database
            initialize_database()
            
            # Create a test user if one doesn't exist
            from .utils import hash_password
            from .supabase import supabase
            
            print("Checking for test user...")
            # Check if the test user already exists
            test_users = supabase.select('users', filter_column='username', filter_value='testuser')
            
            if not test_users or len(test_users) == 0:
                print("Creating test user account...")
                
                # Create a test user
                test_user_data = {
                    "username": "testuser",
                    "password": hash_password("password123"),
                    "email": "testuser@example.com",
                    "phone_number": "+911234567890",
                    "role": "user"
                }
                
                result = supabase.insert("users", test_user_data)
                if 'error' in result:
                    print(f"Error creating test user: {result['error']}")
                else:
                    print("Test user created successfully!")
            else:
                print("Test user already exists.")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
