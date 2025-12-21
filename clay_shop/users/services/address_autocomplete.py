import hashlib
import logging

import httpx
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AddressAutocompleteService:
    API_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
    CACHE_TIMEOUT = 3600
    CACHE_PREFIX = "address_suggest"

    @staticmethod
    def _get_cache_key(query: str, count: int) -> str:
        key_data = f"{query}:{count}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{AddressAutocompleteService.CACHE_PREFIX}:{key_hash}"

    @staticmethod
    def get_suggestions(query: str, count: int = 10) -> list[dict]:
        if not query or len(query) < 3:
            return []

        cache_key = AddressAutocompleteService._get_cache_key(query, count)
        cached_result = cache.get(cache_key)

        if cached_result:
            logger.info(f"Cache HIT for query: {query}")
            return cached_result

        logger.info(f"Cache MISS for query: {query}")

        api_key = getattr(settings, "DADATA_API_KEY", None)
        if not api_key:
            logger.warning("DADATA_API_KEY не установлен в settings")
            return []

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    AddressAutocompleteService.API_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Token {api_key}",
                    },
                    json={
                        "query": query,
                        "count": count,
                        "language": "ru"
                    }
                )
            if response.status_code == 200:
                data = response.json()
                suggestions = AddressAutocompleteService._format_suggestions(
                    data.get("suggestions", [])
                )

                cache.set(
                    cache_key,
                    suggestions,
                    AddressAutocompleteService.CACHE_TIMEOUT
                )

                return suggestions
            else:
                logger.error(f"DaData API error: {response.status_code}")
                return []
        except httpx.TimeoutException:
            logger.error("DaData API timeout")
            return []
        except Exception as e:
            logger.error(f"Error calling DaData API: {str(e)}")
            return []

    @staticmethod
    def _format_suggestions(suggestions: list[dict]) -> list[dict]:
        formatted = []

        for suggestion in suggestions:
            data = suggestion.get("data", {})
            formatted.append(
                {
                    "value": suggestion.get("value", ""),
                    "unrestricted_value": suggestion.get("unrestricted_value", ""),
                    "postal_code": data.get("postal_code", ""),
                    "country": data.get("country", ""),
                    "region": data.get("region_with_type", ""),
                    "city": data.get("city", ""),
                    "street": data.get("street", ""),
                    "house": data.get("house", ""),
                    "flat": data.get("flat", ""),
                    "geo_lat": data.get("geo_lat"),
                    "geo_lon": data.get("geo_lon"),
                }
            )
        return formatted
