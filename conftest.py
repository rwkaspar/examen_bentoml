import os
import pytest

def pytest_collection_modifyitems(config, items):
    run_service_tests = os.getenv("RUN_SERVICE_TESTS", "true").lower() == "true"
    if not run_service_tests:
        skip_marker = pytest.mark.skip(reason="Skipping service tests in CI")
        for item in items:
            if "service" in item.keywords:
                item.add_marker(skip_marker)
