import os
import json
import requests
from django.conf import settings

class SupabaseClient:
    """A client for interacting with Supabase API."""
    
    def __init__(self, url=None, key=None, secret_key=None):
        """Initialize the Supabase client with API credentials."""
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY
        self.secret_key = secret_key or settings.SUPABASE_SECRET_KEY
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
        self.admin_headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }

    def _build_url(self, table, id=None):
        """Build the URL for the REST API request."""
        url = f"{self.url}/rest/v1/{table}"
        if id:
            url += f"/{id}"
        return url

    def select(self, table, columns="*", filter_column=None, filter_value=None, order=None, range_from=None, range_to=None):
        """Query data from a table."""
        url = self._build_url(table)
        params = {'select': columns}
        
        if filter_column and filter_value:
            params[filter_column] = f'eq.{filter_value}'
        
        if order:
            params['order'] = order
            
        headers = self.headers.copy()
        if range_from is not None and range_to is not None:
            headers['Range'] = f'{range_from}-{range_to}'
        
        print(f"Selecting data from {table} at URL: {url}")
        print(f"Select params: {params}")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"Select response status: {response.status_code}")
        print(f"Select response content: {response.text}")
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        if response.text.strip():
            return response.json()
        else:
            return []

    def insert(self, table, data):
        """Insert data into a table."""
        url = self._build_url(table)
        print(f"Inserting data into {table} at URL: {url}")
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        print(f"Insert response status: {response.status_code}")
        print(f"Insert response content: {response.text}")
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        if response.text.strip():
            return response.json()
        else:
            return {'success': True, 'data': data}

    def update(self, table, id, data):
        """Update data in a table."""
        url = self._build_url(table)
        params = {'id': f'eq.{id}'}
        response = requests.patch(url, headers=self.headers, params=params, data=json.dumps(data))
        
        print(f"Update response status: {response.status_code}")
        print(f"Update response content: {response.text}")
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        if response.text.strip():
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'success': True, 'data': data}
        else:
            return {'success': True, 'data': data}

    def delete(self, table, id):
        """Delete data from a table."""
        url = self._build_url(table)
        params = {'id': f'eq.{id}'}
        response = requests.delete(url, headers=self.headers, params=params)
        
        print(f"Delete response status: {response.status_code}")
        print(f"Delete response content: {response.text}")
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        return {'success': True}

    def custom_query(self, query):
        """Execute a custom SQL query using the admin key."""
        # For simplicity and security reasons, we don't execute raw SQL via Supabase REST API
        # Instead, we use the appropriate REST API methods for different operations
        print(f"Custom query requested: {query}")
        
        # Split the query into individual statements
        statements = [stmt.strip() for stmt in query.split(';') if stmt.strip()]
        results = []
        
        for statement in statements:
            # Skip empty statements
            if not statement:
                continue
                
            # Determine the type of statement
            statement_lower = statement.lower()
            
            try:
                if statement_lower.startswith('select'):
                    # Handle SELECT statements
                    # Extract the table name (simplified approach)
                    from_parts = statement_lower.split('from')
                    if len(from_parts) > 1:
                        table_parts = from_parts[1].strip().split()
                        if table_parts:
                            table_name = table_parts[0].strip()
                            # Use the select method instead of raw SQL
                            result = self.select(table_name)
                            results.append(result)
                        else:
                            results.append({'error': 'Could not parse table name from SELECT statement'})
                    else:
                        results.append({'error': 'Invalid SELECT statement format'})
                        
                elif statement_lower.startswith('insert'):
                    # Handle INSERT statements
                    results.append({'message': 'INSERT operations should use the insert() method'})
                    
                elif statement_lower.startswith('update'):
                    # Handle UPDATE statements
                    results.append({'message': 'UPDATE operations should use the update() method'})
                    
                elif statement_lower.startswith('delete'):
                    # Handle DELETE statements
                    results.append({'message': 'DELETE operations should use the delete() method'})
                    
                elif statement_lower.startswith('create'):
                    # Handle CREATE statements
                    results.append({'message': 'CREATE operations should be performed through Supabase UI'})
                    
                else:
                    # Handle other types of statements
                    results.append({'message': f'Unsupported operation: {statement}'})
                    
            except Exception as e:
                results.append({'error': str(e), 'statement': statement})
                
        return results

    def auth_signup(self, email, password, user_data=None):
        """Register a new user using Supabase Auth."""
        url = f"{self.url}/auth/v1/signup"
        data = {
            'email': email,
            'password': password
        }
        if user_data:
            data['data'] = user_data
            
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        return response.json()

    def auth_login(self, email, password):
        """Log in a user using Supabase Auth."""
        url = f"{self.url}/auth/v1/token?grant_type=password"
        data = {
            'email': email,
            'password': password
        }
        
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        return response.json()

    def auth_user(self, jwt):
        """Get user data using the JWT token."""
        headers = self.headers.copy()
        headers['Authorization'] = f'Bearer {jwt}'
        
        url = f"{self.url}/auth/v1/user"
        response = requests.get(url, headers=headers)
        
        if response.status_code >= 400:
            return {'error': response.text}
        
        return response.json()


# Create a global instance for use throughout the app
supabase = SupabaseClient()
