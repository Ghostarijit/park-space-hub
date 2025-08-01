import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings
from functools import wraps
from core.models.users import User

# Secret key for JWT
SECRET_KEY = 'park-space-hub'
JWT_EXPIRY_MINUTES = 60

# Generate JWT Token
def generate_jwt(user_id, role_name):
    payload = {
        'user_id': user_id,
        'role': role_name,
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Decode JWT Token
def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Decorator for JWT-protected views
def jwt_required(allowed_roles=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authorization token missing'}, status=401)
            token = auth_header.split(' ')[1]
            payload = decode_jwt(token)
            if not payload:
                return JsonResponse({'error': 'Invalid or expired token'}, status=401)

            user = User.get_by_id(payload['user_id'])
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Role Check
            if allowed_roles and user.role.name not in allowed_roles:
                return JsonResponse({'error': 'Access denied'}, status=403)

            request.user = user  # attach user to request
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
