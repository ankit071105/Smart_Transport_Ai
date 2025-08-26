import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import time
from datetime import datetime
import sqlite3
import requests
from geopy.geocoders import Nominatim
import plotly.express as px
from streamlit_option_menu import option_menu
import json
import os

# Import custom modules
try:
    from utils.map_utils import get_route, get_route_with_waypoints, get_crowd_data, geocode_location
    from utils.voice_utils import text_to_speech
    from utils.alert_utils import send_alert
    from agents.route_agent import RouteAgent
    from database.database import init_db, save_route, get_history, get_user_preferences, save_user_preferences
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please make sure all module files are in the correct directories")

# Page configuration
st.set_page_config(
    page_title="Smart Transit AI",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for route tracking
if 'current_route' not in st.session_state:
    st.session_state.current_route = None
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "Route Planner"

# Custom CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        
        .description {
            color: #6c757d;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .stButton button:first-child {
            background-color: #0d6efd;
            border-color: #0d6efd;
        }
        
        .css-1fv8s86 e16fv1kl2 {
            background-color: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .stTextInput input {
            border-radius: 8px;
            border: 1px solid #ced4da;
        }
        
        .stTextInput input:focus {
            border-color: #0d6efd;
            box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
        }
        
        .stSelectbox select {
            border-radius: 8px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f8f9fa;
            border-radius: 8px 8px 0 0;
            padding: 10px 16px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #0d6efd;
            color: white;
        }
        
        .streamlit-expanderHeader {
            font-weight: 600;
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

# Try to load CSS
try:
    local_css("assets/css/style.css")
except:
    pass

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# Initialize route agent
try:
    agent = RouteAgent()
except Exception as e:
    st.error(f"Agent initialization error: {e}")
    agent = None

# App title and description
st.title("🚌 Smart AI Public Transport & Route Optimizer")
st.markdown("""
    <div class="description">
    Find the fastest, least crowded, and safest routes using AI-powered recommendations
    </div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    try:
        st.image("assets/images/logo.png", width=150)
    except:
        st.markdown("### 🚌 Smart Transit AI")
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Route Planner", "Live Tracking", "Travel History", "Settings", "Help"],
        icons=["geo-alt", "map", "clock-history", "gear", "question-circle"],
        default_index=0,
    )
    
    # Store the selected tab in session state
    st.session_state.selected_tab = selected

# Function to display route information
def display_route(route, index):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Estimated Time", f"{route['duration']} min")
    
    with col2:
        st.metric("Distance", f"{route['distance']} km")
    
    with col3:
        crowd_level = "Low" if route['crowd_level'] < 3 else "Medium" if route['crowd_level'] < 7 else "High"
        st.metric("Crowd Level", crowd_level)
    
    # Display route on map
    try:
        start_coords = route['geometry']['coordinates'][0]
        m = folium.Map(
            location=[start_coords[1], start_coords[0]],
            zoom_start=12
        )
        
        # Add route to map
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in route['geometry']['coordinates']],
            color='blue',
            weight=5,
            opacity=0.7,
            popup=f"Route {index+1}"
        ).add_to(m)
        
        # Add markers for start and end
        folium.Marker(
            [route['geometry']['coordinates'][0][1], route['geometry']['coordinates'][0][0]],
            popup="Start",
            icon=folium.Icon(color='green')
        ).add_to(m)
        
        folium.Marker(
            [route['geometry']['coordinates'][-1][1], route['geometry']['coordinates'][-1][0]],
            popup="End",
            icon=folium.Icon(color='red')
        ).add_to(m)
        
        # Display map
        folium_static(m, width=700, height=400)
    except Exception as e:
        st.error(f"Error displaying map: {e}")
    
    # Step-by-step directions
    with st.expander("View Step-by-Step Directions"):
        for i, step in enumerate(route['steps']):
            st.write(f"{i+1}. {step}")
    
    # Select this route button
    if st.button(f"Select Route {index+1}", key=f"route_{index}", use_container_width=True):
        st.session_state.current_route = route
        st.success(f"Route {index+1} selected! Navigate to the Live Tracking tab to begin your journey.")
        # Save to history
        try:
            save_route(origin, destination, route)
        except Exception as e:
            st.error(f"Error saving route: {e}")

# Main content based on navigation
if selected == "Route Planner":
    st.header("📍 Plan Your Journey")
    
    # Input form
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("Starting Point", placeholder="Enter your starting location")
    with col2:
        destination = st.text_input("Destination", placeholder="Enter your destination")
    
    # Additional options
    col1, col2, col3 = st.columns(3)
    with col1:
        transport_mode = st.selectbox(
            "Transport Mode",
            ["Bus", "Train", "Multi-modal", "Walking"]
        )
    with col2:
        priority = st.selectbox(
            "Priority",
            ["Fastest", "Least Crowded", "Safest", "Balanced"]
        )
    with col3:
        avoid_congestion = st.checkbox("Avoid Congestion", value=True)
    
    # Find route button
    if st.button("Find Best Route", type="primary", use_container_width=True):
        if origin and destination:
            if agent is None:
                st.error("Route agent is not initialized. Please check the error messages above.")
            else:
                with st.spinner("Finding the best route for you..."):
                    # Get route recommendations
                    routes = agent.get_route_recommendations(origin, destination, transport_mode, priority)
                    
                    if routes:
                        # Display routes
                        st.success("Found the best routes for your journey!")
                        
                        # Create tabs for different routes
                        tab1, tab2, tab3 = st.tabs(["Recommended Route", "Alternative 1", "Alternative 2"])
                        
                        with tab1:
                            display_route(routes[0], 0)
                        
                        with tab2:
                            display_route(routes[1], 1)
                        
                        with tab3:
                            display_route(routes[2], 2)
                        
                        # Voice guidance option
                        if st.button("🔊 Get Voice Guidance", use_container_width=True):
                            try:
                                text_to_speech(f"Your route from {origin} to {destination} will take approximately {routes[0]['duration']} minutes.")
                            except Exception as e:
                                st.error(f"Voice guidance error: {e}")
                    else:
                        st.error("Could not find routes for your journey. Please check your locations and try again.")
        else:
            st.warning("Please enter both starting point and destination.")

elif selected == "Live Tracking":
    st.header("📡 Live Tracking")
    
    if st.session_state.current_route is None:
        st.info("Plan a route first to enable live tracking. Go to the Route Planner tab to get started.")
        st.stop()
    
    # Display live map
    st.subheader("Your Current Route")
    
    # Simulate live tracking
    progress = st.slider("Journey Progress", 0, 100, 0)
    
    # Get current position based on progress
    route = st.session_state.current_route
    try:
        total_points = len(route['geometry']['coordinates'])
        current_index = int((progress / 100) * (total_points - 1))
        current_pos = route['geometry']['coordinates'][current_index]
        
        # Create map
        m = folium.Map(location=[current_pos[1], current_pos[0]], zoom_start=13)
        
        # Add route
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in route['geometry']['coordinates']],
            color='blue',
            weight=5,
            opacity=0.7
        ).add_to(m)
        
        # Add current position marker
        folium.Marker(
            [current_pos[1], current_pos[0]],
            popup="Your position",
            icon=folium.Icon(color='green', icon='user')
        ).add_to(m)
        
        # Add start and end markers
        folium.Marker(
            [route['geometry']['coordinates'][0][1], route['geometry']['coordinates'][0][0]],
            popup="Start",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        folium.Marker(
            [route['geometry']['coordinates'][-1][1], route['geometry']['coordinates'][-1][0]],
            popup="End",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
        
        # Display map
        folium_static(m, width=800, height=500)
    except Exception as e:
        st.error(f"Error displaying live map: {e}")
    
    # Alerts and notifications
    st.subheader("Alerts & Notifications")
    
    # Simulate alerts
    if progress > 30 and progress < 40:
        st.warning("🚧 Congestion ahead. Consider alternative route.")
        if st.button("Find Alternative Route"):
            # This would call the agent to find an alternative
            st.info("Finding alternative route...")
    
    if progress > 70:
        st.info("🔄 You're 70% through your journey. Next stop in 5 minutes.")
    
    # SOS button
    if st.button("🆘 SOS Alert", type="secondary", use_container_width=True):
        try:
            send_alert("SOS activated. User needs assistance.")
            st.success("SOS alert sent to emergency contacts")
        except Exception as e:
            st.error(f"Error sending SOS: {e}")

elif selected == "Travel History":
    st.header("📊 Travel History")
    
    # Get user history
    try:
        history = get_history()
        
        if history:
            # Convert to DataFrame for display
            df = pd.DataFrame(history, columns=["ID", "Start", "End", "Duration", "Timestamp"])
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Journeys", len(df))
            with col2:
                st.metric("Average Duration", f"{df['Duration'].mean():.1f} min")
            with col3:
                st.metric("Most Frequent Destination", df['End'].mode()[0] if not df['End'].mode().empty else "N/A")
            
            # Display history table
            st.dataframe(df[["Start", "End", "Duration", "Timestamp"]], use_container_width=True)
            
            # Display chart
            fig = px.line(df, x='Timestamp', y='Duration', title='Travel Time History')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No travel history yet. Plan a route to get started!")
    except Exception as e:
        st.error(f"Error loading travel history: {e}")

elif selected == "Settings":
    st.header("⚙️ Settings")
    
    # Get current preferences
    try:
        current_prefs = get_user_preferences()
    except Exception as e:
        st.error(f"Error loading preferences: {e}")
        current_prefs = {
            'walking_speed': 'moderate',
            'max_walking_time': 15,
            'crowd_tolerance': 'moderate',
            'safety_priority': 7,
            'voice_guidance': True,
            'congestion_alerts': True,
            'delay_alerts': True,
            'safety_alerts': True,
            'emergency_contact': ''
        }
    
    # User preferences
    st.subheader("User Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        walking_speed = st.select_slider(
            "Walking Speed",
            options=["Slow", "Moderate", "Fast"],
            value=current_prefs.get('walking_speed', 'Moderate').capitalize()
        )
        
        max_walking_time = st.slider(
            "Maximum Walking Time (minutes)",
            min_value=5,
            max_value=30,
            value=current_prefs.get('max_walking_time', 15)
        )
    
    with col2:
        crowd_tolerance = st.select_slider(
            "Crowd Tolerance",
            options=["Avoid Crowds", "Moderate", "No Preference"],
            value=current_prefs.get('crowd_tolerance', 'Moderate').capitalize()
        )
        
        safety_priority = st.slider(
            "Safety Priority",
            min_value=1,
            max_value=10,
            value=current_prefs.get('safety_priority', 7)
        )
    
    # Notification settings
    st.subheader("Notification Preferences")
    
    notif_col1, notif_col2 = st.columns(2)
    with notif_col1:
        voice_guidance = st.checkbox("Voice Guidance", value=current_prefs.get('voice_guidance', True))
        congestion_alerts = st.checkbox("Congestion Alerts", value=current_prefs.get('congestion_alerts', True))
    
    with notif_col2:
        delay_alerts = st.checkbox("Delay Alerts", value=current_prefs.get('delay_alerts', True))
        safety_alerts = st.checkbox("Safety Alerts", value=current_prefs.get('safety_alerts', True))
    
    # Emergency contacts
    st.subheader("Emergency Contacts")
    emergency_contact = st.text_input("Emergency Contact Number", value=current_prefs.get('emergency_contact', ''))
    
    if st.button("Save Preferences", type="primary"):
        preferences = {
            'walking_speed': walking_speed.lower(),
            'max_walking_time': max_walking_time,
            'crowd_tolerance': crowd_tolerance.lower(),
            'safety_priority': safety_priority,
            'voice_guidance': voice_guidance,
            'congestion_alerts': congestion_alerts,
            'delay_alerts': delay_alerts,
            'safety_alerts': safety_alerts,
            'emergency_contact': emergency_contact
        }
        try:
            save_user_preferences(preferences)
            st.success("Preferences saved successfully!")
        except Exception as e:
            st.error(f"Error saving preferences: {e}")

elif selected == "Help":
    st.header("❓ Help & Support")
    
    st.subheader("How to Use")
    st.markdown("""
    1. **Plan Your Route**: Enter your start and destination points, then select your preferences
    2. **View Recommendations**: See the best routes based on your criteria
    3. **Live Tracking**: Monitor your journey in real-time with live updates
    4. **History**: Review your past journeys and travel patterns
    """)
    
    st.subheader("Frequently Asked Questions")
    with st.expander("How does the AI determine the best route?"):
        st.write("Our AI uses machine learning models trained on historical traffic data, crowd information, and real-time conditions to predict the fastest and safest routes.")
    
    with st.expander("Is my data secure?"):
        st.write("Yes, we prioritize user privacy and only store essential journey information to improve your experience.")
    
    with st.expander("How accurate are the crowd predictions?"):
        st.write("Our crowd predictions are based on historical patterns, real-time ticketing data, and user reports, with an average accuracy of 85%.")
    
    st.subheader("Contact Support")
    st.write("Having issues? Contact our support team at support@smarttransit.ai or call +91-XXXXX-XXXXX")

if __name__ == "__main__":
    # This is already the main app
    pass
