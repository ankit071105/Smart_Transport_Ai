import numpy as np
from datetime import datetime
from utils.map_utils import get_route, get_crowd_data
import copy

class RouteAgent:
    def __init__(self):
        self.history = []
    
    def get_route_recommendations(self, origin, destination, transport_mode, priority):
        """Get AI-powered route recommendations"""
        # Get base route
        profile = self._get_profile(transport_mode)
        base_route = get_route(origin, destination, profile)
        
        if not base_route:
            return None
        
        # Generate alternative routes (simulated)
        routes = []
        
        # Primary route (fastest)
        primary_route = self._enhance_route_data(base_route, origin, destination, 0)
        routes.append(primary_route)
        
        # Alternative routes (simulated)
        for i in range(1, 3):
            alt_route = self._create_alternative_route(base_route, origin, destination, i)
            routes.append(alt_route)
        
        # Sort based on priority
        if priority == "Least Crowded":
            routes.sort(key=lambda x: x['crowd_level'])
        elif priority == "Safest":
            routes.sort(key=lambda x: x['safety_score'])
        else:  # Fastest or Balanced
            routes.sort(key=lambda x: x['duration'])
        
        return routes
    
    def _get_profile(self, transport_mode):
        """Get routing profile based on transport mode"""
        if transport_mode == "Bus":
            return "driving-car"  # Using car routing as proxy for bus
        elif transport_mode == "Train":
            return "driving-car"  # Would need specialized transit routing
        elif transport_mode == "Walking":
            return "foot-walking"
        else:  # Multi-modal
            return "driving-car"
    
    def _enhance_route_data(self, route, origin, destination, variant):
        """Enhance route data with AI predictions"""
        # Calculate distance and duration
        if 'features' in route and len(route['features']) > 0:
            distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert to km
            duration = route['features'][0]['properties']['segments'][0]['duration'] / 60  # Convert to minutes
        else:
            # Fallback values if route structure is different
            distance = 10.0
            duration = 30.0
        
        # Apply variant modifications
        if variant == 1:
            # Slightly longer but less crowded
            duration *= 1.1
            distance *= 1.05
        elif variant == 2:
            # Safer but longer
            duration *= 1.2
            distance *= 1.1
        
        # Get crowd data (simulated)
        crowd_level = get_crowd_data(origin)  # Would be more sophisticated in real implementation
        
        # Calculate safety score (simulated)
        hour = datetime.now().hour
        if 6 <= hour <= 20:
            safety_score = np.random.randint(7, 10)
        else:
            safety_score = np.random.randint(4, 7)
        
        # Add steps for directions (simulated)
        steps = [
            f"Walk to {origin} station",
            f"Take bus line {np.random.randint(1, 15)} towards city center",
            f"Transfer at Central Station to bus line {np.random.randint(20, 35)}",
            f"Get off at {destination} station",
            "Walk to your destination"
        ]
        
        # Ensure geometry exists
        if 'features' in route and len(route['features']) > 0:
            geometry = route['features'][0]['geometry']
        else:
            # Create a simple geometry as fallback
            start_coords = [72.8777, 19.0760]  # Default coordinates
            end_coords = [77.1025, 28.7041]    # Default coordinates
            geometry = {
                'type': 'LineString',
                'coordinates': [start_coords, end_coords]
            }
        
        return {
            'origin': origin,
            'destination': destination,
            'distance': round(distance, 1),
            'duration': round(duration, 1),
            'crowd_level': crowd_level,
            'safety_score': safety_score,
            'geometry': geometry,
            'steps': steps,
            'variant': variant
        }
    
    def _create_alternative_route(self, base_route, origin, destination, variant):
        """Create an alternative route (simulated)"""
        # In a real implementation, this would find actual alternative routes
        # For now, we'll just modify the base route slightly
        
        # Make a deep copy of the route
        alt_route = copy.deepcopy(base_route)
        
        # Modify some coordinates slightly to simulate different route
        if 'features' in alt_route and len(alt_route['features']) > 0:
            coords = alt_route['features'][0]['geometry']['coordinates']
            for i in range(1, len(coords)-1):
                if i % 5 == 0:  # Modify every 5th point
                    coords[i][0] += 0.001 * variant
                    coords[i][1] += 0.001 * variant
        
        return self._enhance_route_data(alt_route, origin, destination, variant)
    
    def monitor_route(self, route):
        """Monitor a route for changes and provide alerts"""
        # Check for congestion
        congestion = self._check_congestion(route)
        
        # Check for safety issues
        safety_issues = self._check_safety(route)
        
        # Check for delays
        delays = self._check_delays(route)
        
        alerts = []
        if congestion:
            alerts.append(("Congestion", f"High congestion detected on your route. Estimated delay: {congestion} minutes"))
        
        if safety_issues:
            alerts.append(("Safety", "Potential safety issues detected on your route"))
        
        if delays:
            alerts.append(("Delay", f"Service delays detected. Estimated additional wait time: {delays} minutes"))
        
        return alerts
    
    def _check_congestion(self, route):
        """Check for congestion on the route (simulated)"""
        # In a real implementation, this would use real-time traffic data
        return np.random.choice([0, 5, 10, 15], p=[0.6, 0.25, 0.1, 0.05])
    
    def _check_safety(self, route):
        """Check for safety issues on the route (simulated)"""
        # In a real implementation, this would use crime data, user reports, etc.
        return np.random.choice([False, True], p=[0.8, 0.2])
    
    def _check_delays(self, route):
        """Check for delays on the route (simulated)"""
        # In a real implementation, this would use real-time transit data
        return np.random.choice([0, 3, 8], p=[0.7, 0.2, 0.1])
