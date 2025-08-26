def send_alert(message, alert_type="info"):
    """Send an alert to the user"""
    # In a real implementation, this would send push notifications, SMS, etc.
    # For now, we'll just print to console and show in the UI
    
    print(f"ALERT ({alert_type}): {message}")
    
    # Return the alert for display in the UI
    return {
        "type": alert_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }