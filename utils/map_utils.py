import openrouteservice
import requests
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime

# CHANGE REQUIRED: Add your OpenRouteService API key here
# You can get a free API key from https://openrouteservice.org/
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImVkYjc1ZGU4MzgxNDQxMmE5MDc2NDRmZDE1N2ZhYzhjIiwiaCI6Im11cm11cjY0In0="

# Initialize OpenRouteService client
client = openrouteservice.Client(key=ORS_API_KEY)

def geocode_location(location_name):
    """Convert location name to coordinates"""
    geolocator = Nominatim(user_agent="smart_transit_ai")
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.longitude, location.latitude)
        else:
            return None
    except:
        # Fallback: return coordinates for a well-known location
        if "mumbai" in location_name.lower():
            return (72.8777, 19.0760)  # Mumbai coordinates
        elif "delhi" in location_name.lower():
            return (77.1025, 28.7041)  # Delhi coordinates
        elif "bangalore" in location_name.lower():
            return (77.5946, 12.9716)  # Bangalore coordinates
        else:
            return (77.2090, 28.6139)  # Default to New Delhi

def get_route(start, end, profile='driving-car'):
    """Get route between two points"""
    try:
        # Geocode start and end points
        start_coords = geocode_location(start)
        end_coords = geocode_location(end)
        
        if not start_coords or not end_coords:
            return None
        
        # Get route
        route = client.directions(
            coordinates=[start_coords, end_coords],
            profile=profile,
            format='geojson'
        )
        
        return route
    except Exception as e:
        print(f"Error getting route: {e}")
        # Return a mock route for demonstration
        return create_mock_route(start, end)

def get_route_with_waypoints(coordinates, profile='driving-car'):
    """Get route with multiple waypoints"""
    try:
        route = client.directions(
            coordinates=coordinates,
            profile=profile,
            format='geojson'
        )
        
        return route
    except Exception as e:
        print(f"Error getting route with waypoints: {e}")
        return None

def get_crowd_data(location, radius=500):
    """Get crowd data for a location (simulated)"""
    # In a real implementation, this would use actual data sources
    # For now, we'll simulate based on time of day and location type
    
    hour = datetime.now().hour
    
    # Simulate crowd levels based on time and location type
    if 'station' in location.lower() or 'central' in location.lower():
        # Transportation hubs are busy during rush hours
        if 7 <= hour <= 10 or 17 <= hour <= 19:
            crowd_level = np.random.randint(7, 10)
        else:
            crowd_level = np.random.randint(4, 7)
    else:
        # Other locations have more variation
        crowd_level = np.random.randint(3, 8)
    
    return crowd_level

def create_mock_route(start, end):
    """Create a mock route for demonstration when API is not available"""
    # Generate some coordinates between start and end
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)
    
    # Create a simple straight line with a few points
    num_points = 10
    coordinates = []
    
    for i in range(num_points):
        lat = start_coords[1] + (end_coords[1] - start_coords[1]) * (i / (num_points - 1))
        lng = start_coords[0] + (end_coords[0] - start_coords[0]) * (i / (num_points - 1))
        coordinates.append([lng, lat])
    
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {
                    'segments': [
                        {
                            'distance': 5000,  # 5km
                            'duration': 1200   # 20 minutes
                        }
                    ]
                },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': coordinates
                }
            }
        ]
    }