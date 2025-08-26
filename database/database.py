import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('transit.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            preferences TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS travel_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_location TEXT,
            end_location TEXT,
            route_data TEXT,
            travel_time INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER,
            predicted_time INTEGER,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default user if not exists
    c.execute('''
        INSERT OR IGNORE INTO users (id, username, preferences) 
        VALUES (1, 'default_user', '{}')
    ''')
    
    conn.commit()
    conn.close()

def save_route(start, end, route_data):
    conn = sqlite3.connect('transit.db')
    c = conn.cursor()
    
    # For simplicity, using a default user ID
    user_id = 1
    
    c.execute('''
        INSERT INTO travel_history (user_id, start_location, end_location, route_data, travel_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, start, end, json.dumps(route_data), route_data['duration']))
    
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('transit.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT id, start_location, end_location, travel_time, timestamp 
        FROM travel_history 
        ORDER BY timestamp DESC
    ''')
    
    history = c.fetchall()
    conn.close()
    
    return history

def get_user_preferences(user_id=1):
    conn = sqlite3.connect('transit.db')
    c = conn.cursor()
    
    c.execute('SELECT preferences FROM users WHERE id = ?', (user_id,))
    preferences = c.fetchone()
    
    conn.close()
    
    if preferences and preferences[0]:
        return json.loads(preferences[0])
    else:
        return {
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

def save_user_preferences(preferences, user_id=1):
    conn = sqlite3.connect('transit.db')
    c = conn.cursor()
    
    c.execute('''
        UPDATE users 
        SET preferences = ?
        WHERE id = ?
    ''', (json.dumps(preferences), user_id))
    
    conn.commit()
    conn.close()