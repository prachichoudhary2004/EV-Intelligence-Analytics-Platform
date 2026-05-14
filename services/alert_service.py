from utils.logger import logger

class AlertService:
    """
    Handles alerts for when things go wrong or need attention.
    """
    
    def __init__(self):
        self.alert_history = []

    def trigger_alert(self, level, message):
        """Log an alert and keep track of it."""
        if level == "CRITICAL":
            logger.error(f"🚨 ALERT: {message}")
        else:
            logger.warning(f"⚠️ NOTIFICATION: {message}")
            
        self.alert_history.append({
            "level": level,
            "message": message,
            "status": "UNREAD"
        })

    def check_thresholds(self, kpis):
        """Check if any KPIs are below what we expect."""
        if kpis['yoy_growth'] < 5:
            self.trigger_alert("CRITICAL", f"Market stagnation detected. YoY growth at {kpis['yoy_growth']}% is below the 5% threshold.")
        
        if kpis['infrastructure_score'] < 2:
            self.trigger_alert("WARNING", f"Charging infrastructure bottleneck. Score: {kpis['infrastructure_score']}.")

    def get_unread_alerts(self):
        """Get all alerts that haven't been read yet."""
        return [a for a in self.alert_history if a['status'] == "UNREAD"]

# So we can use it anywhere in the app
alert_service = AlertService()
