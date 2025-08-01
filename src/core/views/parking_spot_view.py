from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import math, traceback

from core.models.parking_spot import ParkingSpot
from core.models.users import User

def parking_spot_view(request):
    return render(request, 'users/parking_spot.html')

@method_decorator(csrf_exempt, name='dispatch')
class ParkingSpotAPIView(View):
    
    def get(self, request, *args, **kwargs):
        try:
            lat = float(request.GET.get('lat', 0))
            lng = float(request.GET.get('lng', 0))
            radius = float(request.GET.get('radius', 200))
            if lat == 0 or lng == 0:
                return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)

            all_spots = ParkingSpot.get_available_spots()
            nearby_spots = []

            for spot in all_spots:
                distance = self.calculate_distance(lat, lng, spot.latitude, spot.longitude)
                if distance <= radius:
                    owner = User.get_by_id(spot.owner_id) if spot.owner_id else None
                    spot_data = {
                        "id": spot.id,
                        "title": spot.title or f"Parking Spot {spot.id}",
                        "latitude": float(spot.latitude),
                        "longitude": float(spot.longitude),
                        "location": spot.location,
                        "parking_type": spot.parking_type,
                        "price_per_hour": float(spot.price_per_hour) if spot.price_per_hour else 0,
                        "max_vehicle_size": spot.max_vehicle_size,
                        "availability_hours": spot.availability_hours or "24/7",
                        "is_available": spot.is_available,
                        "contact_phone": spot.contact_phone,
                        "description": getattr(spot, 'description', ''),
                        "distance_km": round(distance, 2),
                        "owner": {
                            "first_name": owner.first_name if owner else "Unknown",
                            "last_name": owner.last_name if owner else "Owner",
                            "email": owner.email if owner else ""
                        }
                    }
                    nearby_spots.append(spot_data)

            nearby_spots.sort(key=lambda x: x['distance_km'])
            return JsonResponse(nearby_spots, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    @staticmethod
    def calculate_distance(lat1, lng1, lat2, lng2):
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return c * 6371
