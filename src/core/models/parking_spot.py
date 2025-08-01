# models/parking_spot.py
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float, Text, Boolean
from core.sqlalchemy_engine import BaseModel
from core.sqlalchemy_engine import session, BaseModel
import json

class ParkingSpot(BaseModel):
    __tablename__ = 'parking_spots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))                      # 🏷️ Spot title
    description = Column(Text)                       # 📝 Detailed description
    location = Column(String(255))                   # 📍 Location description  
    latitude = Column(Float)                         # 🧭 Latitude
    longitude = Column(Float)                        # 🧭 Longitude
    price_per_hour = Column(Float)                   # 💰 Price per hour
    parking_type = Column(String(50))                # 🚗 Type: covered, open, garage, driveway
    is_available = Column(String(10), default='yes') # ✅ 'yes' or 'no'
    owner_id = Column(Integer)                       # 👤 Owner ID (references users)
    
    # Additional fields
    max_vehicle_size = Column(String(20), default='car')  # 🚙 car, bike, truck, etc.
    amenities = Column(Text)                         # 🏢 JSON string of amenities
    images = Column(Text)                            # 🖼️ JSON array of image URLs
    contact_phone = Column(String(20))               # 📞 Contact number
    availability_hours = Column(String(100))         # ⏰ "24/7" or "9AM-6PM"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer)
    
    is_active = Column(Boolean, nullable=False, default=True)

    @classmethod
    def add(cls, data):
        """Create a new parking spot"""
        parking_spot = ParkingSpot()
        
        # Convert string numbers to proper types
        if 'latitude' in data:
            data['latitude'] = float(data['latitude'])
        if 'longitude' in data:
            data['longitude'] = float(data['longitude'])
        if 'price_per_hour' in data or 'hourly_rate' in data:
            rate = data.pop('hourly_rate', data.get('price_per_hour', 0))
            data['price_per_hour'] = float(rate)
        if 'owner_id' in data:
            data['owner_id'] = int(data['owner_id'])
            
        # Handle address field mapping
        if 'address' in data and not data.get('location'):
            data['location'] = data.pop('address')
            
        # Set default values
        if not data.get('title'):
            location_short = data.get('location', 'Parking Spot')[:50]
            data['title'] = f"Parking - {location_short}"
            
        if not data.get('availability_hours'):
            data['availability_hours'] = '24/7'
            
        if not data.get('max_vehicle_size'):
            data['max_vehicle_size'] = 'car'
            
        # Handle amenities as JSON
        if 'amenities' in data and isinstance(data['amenities'], list):
            data['amenities'] = json.dumps(data['amenities'])
            
        # Handle images as JSON  
        if 'images' in data and isinstance(data['images'], list):
            data['images'] = json.dumps(data['images'])

        parking_spot.fill(**data)
        parking_spot.save()
        
        return parking_spot

    @staticmethod
    def get_by_id(spot_id):
        """Get parking spot by ID"""
        return session.query(ParkingSpot).filter_by(id=spot_id, is_active=True).first()

    @staticmethod  
    def get_by_owner(owner_id):
        """Get all parking spots by owner"""
        return session.query(ParkingSpot).filter_by(
            owner_id=owner_id, 
            is_active=True
        ).all()

    @staticmethod
    def get_available_spots(limit=50):
        """Get all available parking spots"""
        return session.query(ParkingSpot).filter_by(
            is_available='yes',
            is_active=True
        ).limit(limit).all()

    @staticmethod
    def search_nearby(latitude, longitude, radius_km=5, limit=20):
        """Search parking spots within radius"""
        # Haversine formula approximation
        lat_diff = 0.009 * radius_km  # Rough conversion: 1 degree ≈ 111km
        lng_diff = 0.009 * radius_km
        
        return session.query(ParkingSpot).filter(
            ParkingSpot.latitude.between(latitude - lat_diff, latitude + lat_diff),
            ParkingSpot.longitude.between(longitude - lng_diff, longitude + lng_diff),
            ParkingSpot.is_available == 'yes',
            ParkingSpot.is_active == True
        ).limit(limit).all()

    @staticmethod
    def update_availability(spot_id, is_available):
        """Update spot availability"""
        spot = session.query(ParkingSpot).filter_by(id=spot_id).first()
        if spot:
            spot.is_available = is_available
            spot.updated_at = datetime.utcnow()
            spot.save()
            return spot
        return None

    @staticmethod
    def get_stats_by_owner(owner_id):
        """Get parking spots statistics for owner"""
        total_spots = session.query(ParkingSpot).filter_by(
            owner_id=owner_id,
            is_active=True
        ).count()
        
        available_spots = session.query(ParkingSpot).filter_by(
            owner_id=owner_id,
            is_available='yes',
            is_active=True
        ).count()
        
        return {
            'total_spots': total_spots,
            'available_spots': available_spots,
            'occupied_spots': total_spots - available_spots
        }

    def update_spot(self, data):
        """Update parking spot details"""
        # Convert data types if needed
        if 'latitude' in data:
            data['latitude'] = float(data['latitude'])
        if 'longitude' in data:
            data['longitude'] = float(data['longitude'])
        if 'price_per_hour' in data:
            data['price_per_hour'] = float(data['price_per_hour'])
            
        # Handle amenities/images as JSON
        if 'amenities' in data and isinstance(data['amenities'], list):
            data['amenities'] = json.dumps(data['amenities'])
        if 'images' in data and isinstance(data['images'], list):
            data['images'] = json.dumps(data['images'])
            
        data['updated_at'] = datetime.utcnow()
        self.fill(**data)
        self.save()
        return self

    def soft_delete(self):
        """Soft delete - mark as inactive"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        self.save()
        return True

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'price_per_hour': self.price_per_hour,
            'parking_type': self.parking_type,
            'is_available': self.is_available,
            'is_active': self.is_active,
            'owner_id': self.owner_id,
            'max_vehicle_size': self.max_vehicle_size,
            'amenities': json.loads(self.amenities) if self.amenities else [],
            'images': json.loads(self.images) if self.images else [],
            'contact_phone': self.contact_phone,
            'availability_hours': self.availability_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<ParkingSpot(id={self.id}, title='{self.title}', owner_id={self.owner_id})>"


# # Usage Examples following your pattern:

# def create_parking_spot_example():
#     """Example: Create parking spot from signup form data"""
#     # Data from frontend signup form
#     form_data = {
#         'title': 'Secure Covered Parking - Park Street',
#         'description': 'Safe covered parking with 24/7 security', 
#         'address': 'Park Street, Kolkata, West Bengal, India',  # Will map to 'location'
#         'latitude': '22.5726',                                  # String from form
#         'longitude': '88.3639',                                 # String from form
#         'hourly_rate': '50.0',                                  # Will map to 'price_per_hour'
#         'parking_type': 'covered',
#         'owner_id': '123',                                      # String from form
#         'contact_phone': '+91 9876543210'
#     }
    
#     # Create parking spot
#     spot = ParkingSpot.add(form_data)
#     print(f"Created parking spot: {spot.id}")
#     return spot

# def get_owner_spots_example():
#     """Example: Get all spots for an owner"""
#     owner_id = 123
#     spots = ParkingSpot.get_by_owner(owner_id)
    
#     print(f"Owner {owner_id} has {len(spots)} parking spots:")
#     for spot in spots:
#         print(f"- {spot.title} (₹{spot.price_per_hour}/hr) - {spot.is_available}")

# def search_nearby_example():
#     """Example: Search nearby spots"""
#     spots = ParkingSpot.search_nearby(22.5726, 88.3639, radius_km=2)
#     print(f"Found {len(spots)} nearby spots")

# def owner_dashboard_example():
#     """Example: Owner dashboard stats"""
#     stats = ParkingSpot.get_stats_by_owner(123)
#     print(f"Stats: {stats}")