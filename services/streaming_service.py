import random
import time
from datetime import datetime
from utils.logger import logger

class StreamingService:
    """
    Fakes real-time data for testing our dashboard.
    """
    def __init__(self):
        self.manufacturers = ["Tesla", "BYD", "Rivian", "Lucid", "Ford", "GM"]
        self.states = ["California", "Texas", "Florida", "New York", "Washington"]

    def generate_live_sale(self):
        """Make up a fake sale event."""
        sale = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "manufacturer": random.choice(self.manufacturers),
            "state": random.choice(self.states),
            "units": random.randint(1, 5),
            "price": random.randint(35000, 120000)
        }
        return sale

    def get_ticker_update(self):
        """Create fake market data for ticker."""
        update = {
            "market_index": round(random.uniform(100, 150), 2),
            "index_change": round(random.uniform(-2, 2), 2),
            "top_mover": random.choice(self.manufacturers),
            "momentum_score": random.randint(1, 100)
        }
        return update

# Use this anywhere
streaming_service = StreamingService()
