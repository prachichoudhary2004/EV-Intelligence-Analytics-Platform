from utils.logger import logger

class AlertService:
    """
    Simulates an enterprise alerting system for anomalies and threshold violations.
    """
    
    def __init__(self):
        self.alert_history = []

    def trigger_alert(self, level, message):
        """Log and store a system alert."""
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
        """Automated check against business threshold targets."""
        if kpis['yoy_growth'] < 5:
            self.trigger_alert("CRITICAL", f"Market stagnation detected. YoY growth at {kpis['yoy_growth']}% is below the 5% threshold.")
        
        if kpis['infrastructure_score'] < 2:
            self.trigger_alert("WARNING", f"Charging infrastructure bottleneck. Score: {kpis['infrastructure_score']}.")

    def get_unread_alerts(self):
        """Retrieve all unread alerts for the dashboard."""
        return [a for a in self.alert_history if a['status'] == "UNREAD"]

# Global instance
alert_service = AlertService()
