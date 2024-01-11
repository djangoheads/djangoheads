import importlib
import os
import sys
from typing import Any, Optional

from django.conf import settings

from .check__base import CheckBase


class CeleryBrokerAvailableCheck(CheckBase):
    """Check celery broker availability."""

    message = "CELERY IS AVAILABLE"

    def check(self) -> bool:
        """Check method implementation."""
        celery_url = getattr(settings, "CELERY_BROKER_URL", getattr(settings, "BROKER_URL", None))
        if celery_url is None:
            self._print_check("CELERY IS NOT CONFIGURED", None)
            return True

        celery_app = self._find_celery_module()
        if celery_app is None:
            self._print_check("CELERY APP IS NOT FOUND", False)
            return False

        try:
            celery_inspect = importlib.import_module("celery.app.control").Inspect
            celery_inspect(app=celery_app, timeout=0.25).ping()  # throws exception if broker isnt available
            self._print_check(self.message)
            return True
        except Exception as exc:
            self._print_check(self.message, exception=exc, exta_info=f"Broker URL: {celery_url}")
        return False

    @staticmethod
    def _find_celery_module() -> Optional[Any]:
        """Find celery module."""
        work_dir = os.getcwd()
        for root, dirs, files in os.walk(work_dir):
            if os.path.relpath(root, work_dir).count(os.sep) < 3 and "celery.py" in files:
                sys.path.append(root)
                module_name = f"{os.path.basename(root)}.celery"
                try:
                    module = importlib.import_module(module_name)
                    celery_app = getattr(module, "celery_app", None)
                    if celery_app is not None:
                        return celery_app
                    del sys.modules[module_name]
                except ModuleNotFoundError:
                    continue
        return None
