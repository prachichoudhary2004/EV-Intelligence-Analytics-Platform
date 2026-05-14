import random
from datetime import datetime


class StreamingService:
    """Lightweight 'live strip' numbers — plausible India EV headlines, not a real feed."""

    def __init__(self):
        self.manufacturers = [
            "Tata Motors",
            "Mahindra Electric",
            "Ola Electric",
            "Ather Energy",
            "MG Motor",
            "BYD India",
            "TVS iQube",
            "Hero Electric",
        ]
        self.states = [
            "Maharashtra",
            "Karnataka",
            "Delhi",
            "Tamil Nadu",
            "Gujarat",
            "Telangana",
            "Uttar Pradesh",
            "Kerala",
        ]

    def get_ticker_update(self):
        """Stable keys — UI expects these names even if you fork `StreamingService`."""
        return {
            "fast_charger_share": float(round(random.uniform(0.34, 0.58), 4)),
            "two_wheeler_mix": float(round(random.uniform(0.42, 0.62), 4)),
            "top_state": random.choice(self.states),
            "policy_watch": random.choice(
                ["FAME-II utilisation tracking", "state subsidy caps", "public charging uptime"]
            ),
            "oem_pulse": random.choice(self.manufacturers),
        }


streaming_service = StreamingService()
