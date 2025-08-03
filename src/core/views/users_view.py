import traceback
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.auth_utils import generate_jwt, jwt_required
from core.models.parking_spot import ParkingSpot
from core.models.users import User
from core.models.user_role import UserRole


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):

    def dispatch(self, request, *args, **kwargs):
        # Handle /signup URL manually
        if request.path.endswith('/signup') or request.path.endswith('/signup/'):
            return self.signup(request, *args, **kwargs)
        
        # Handle / (home page)
        if request.path == '/':
            return self.home(request, *args, **kwargs)

        # Let GET, PUT fall back to normal method dispatch
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(jwt_required(allowed_roles=['admin']))
    def get(self, request, *args, **kwargs):
        # GET /user → get all users
        users = User.get_all()
        data = [{
            "id": u.id,
            "email": u.email,
            "name": f"{u.first_name} {u.last_name}",
            "role": u.role.name if u.role else None
        } for u in users]
        return JsonResponse(data, safe=False)

    def put(self, request, *args, **kwargs):
        # PUT /user → login
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            user = User.authenticate(email, password)
            if not user:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

            user_role = UserRole.get_by_user_id(user.id)
            role_name = user_role.name if user_role else 'seeker'

            token = generate_jwt(user.id, role_name)

            return JsonResponse({
                'message': 'Login successful',
                'user_id': user.id,
                'email': user.email,
                'role': role_name,
                'token': token
            })
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)

    def signup(self, request, *args, **kwargs):
        # GET or POST /user/signup
        if request.method == 'GET':
            return render(request, 'users/signup.html')

        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                print("Received signup data:", data)
                role_name = data.pop('role', 'seeker')
                
                # Extract location data for providers
                parking_data = {}
                if role_name == 'provider':
                    parking_data = {
                        'latitude': data.pop('latitude', None),
                        'longitude': data.pop('longitude', None),
                        'address': data.pop('address', None),  # Will map to 'location' in ParkingSpot
                        'parking_type': data.pop('parking_type', None),
                        'hourly_rate': data.pop('hourly_rate', None),  # Will map to 'price_per_hour'
                        'description': data.pop('description', None),
                        # Additional parking fields that might come from frontend
                        'title': data.pop('title', None),
                        'max_vehicle_size': data.pop('max_vehicle_size', 'car'),
                        'amenities': data.pop('amenities', []),
                        'images': data.pop('images', []),
                        'contact_phone': data.pop('contact_phone', None),
                        'availability_hours': data.pop('availability_hours', '24/7')
                    }
                    data.pop('user_address', None)  # Remove role from user data if present

                # Create user with remaining data
                user, raw_password = User.add(data)
                
                # Add user role
                UserRole.add({
                    'user_id': user.id,
                    'name': role_name
                })
                
                parking_spot = None
                # If provider, create parking spot
                if role_name == 'provider' and parking_data.get('latitude') and parking_data.get('longitude'):
                    try:
                        # Add owner_id to parking data
                        parking_data['owner_id'] = user.id
                        parking_data['created_by'] = user.id
                        
                        # Set contact_phone from user if not provided
                        if not parking_data.get('contact_phone') and hasattr(user, 'phone'):
                            parking_data['contact_phone'] = user.mobile_number
                        
                        # Create parking spot using your model
                        parking_spot = ParkingSpot.add(parking_data)
                        print(f"Created parking spot: {parking_spot.id} for user: {user.id}")
                        
                    except Exception as parking_error:
                        print(f"Error creating parking spot: {parking_error}")
                        print(traceback.format_exc())
                        # Continue with user creation even if parking spot fails
                        pass

                response_data = {
                    'message': 'User created successfully',
                    'id': user.id,
                    'email': user.email,
                    'role': role_name,
                    'generated_password': raw_password if raw_password else 'Provided by user'
                }
                
                # Add parking spot data to response if provider and spot was created
                if role_name == 'provider' and parking_spot:
                    response_data['parking_spot'] = {
                        'id': parking_spot.id,
                        'title': parking_spot.title,
                        'location': parking_spot.location,
                        'latitude': parking_spot.latitude,
                        'longitude': parking_spot.longitude,
                        'price_per_hour': parking_spot.price_per_hour,
                        'parking_type': parking_spot.parking_type,
                        'is_available': parking_spot.is_available,
                        'max_vehicle_size': parking_spot.max_vehicle_size,
                        'availability_hours': parking_spot.availability_hours
                    }
                elif role_name == 'provider' and parking_data.get('latitude'):
                    # If parking spot creation failed but we had data
                    response_data['location'] = {
                        'latitude': parking_data['latitude'],
                        'longitude': parking_data['longitude'],
                        'address': parking_data['address'],
                        'parking_type': parking_data['parking_type'],
                        'hourly_rate': parking_data['hourly_rate'],
                        'description': parking_data['description']
                    }

                return JsonResponse(response_data)
                
            except Exception as e:
                print(traceback.format_exc())
                return JsonResponse({'error': str(e)}, status=500)

    def home(self, request, *args, **kwargs):
        return render(request, 'home.html') 
