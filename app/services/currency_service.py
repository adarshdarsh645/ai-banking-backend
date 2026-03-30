import time
import urllib.request
import json
from typing import Dict, Any

class CurrencyService:
    _cache: Dict[str, Any] = {}
    _cache_ttl: int = 3600  # 1 hour
    _last_fetched: float = 0.0

    @classmethod
    def get_rates(cls) -> Dict[str, Any]:
        """Fetch Exchange Rates using synchronous urllib logic to avoid extra deps. Caches for 1h."""
        now = time.time()
        
        if cls._cache and (now - cls._last_fetched < cls._cache_ttl):
            return cls._cache

        url = "https://open.er-api.com/v6/latest/USD"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "AIBankingApp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    rates = data.get("rates", {})
                    # Return only requested major currencies
                    filtered_rates = {
                        "USD": rates.get("USD", 1.0),
                        "EUR": rates.get("EUR"),
                        "GBP": rates.get("GBP"),
                    }
                    
                    cls._cache = {
                        "base": "USD",
                        "rates": filtered_rates,
                    }
                    cls._last_fetched = now
                    return cls._cache
        except Exception:
            pass

        # Fallback if API fails & cache empty
        if cls._cache:
            return cls._cache
            
        return {
            "base": "USD",
            "rates": {"USD": 1.0, "EUR": 0.92, "GBP": 0.79}, # hardcoded fallback
            "fallback": True
        }
