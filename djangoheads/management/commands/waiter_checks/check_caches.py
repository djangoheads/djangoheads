from django.conf import settings
from django.core.cache import InvalidCacheBackendError, caches
from django.core.exceptions import ImproperlyConfigured

from .check__base import CheckBase


class CachesAvailableCheck(CheckBase):
    """Check caches availability."""

    message_template = "CACHE IS AVAILABLE [{}]"

    def check(self) -> bool:
        """Check method implementation."""
        try:
            for cache_name in settings.CACHES:
                self.message = self.message_template.format(cache_name)
                cache = caches[cache_name]
                test_key = f"__test_{self._get_random_hexstr()}__"
                test_value = "1"
                cache.set(test_key, test_value, timeout=60)
                if cache.get(test_key) != test_value:
                    self._print_check(self.message, False)
                    break
            else:
                self._print_check(self.message, True)
                return True
        except InvalidCacheBackendError as exc:
            if isinstance(exc, ImproperlyConfigured):
                self._print_check("CACHES ARE NOT CONFIGURED", None)
                return True
            self._print_check(self.message, False, exception=exc)
        except Exception as exc:
            self._print_check(self.message, exception=exc)
        return False
