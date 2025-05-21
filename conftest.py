import sys
import os
import pytest

# if "RUN_SERVICE_TESTS" not in os.environ:
#     os.environ["RUN_SERVICE_TESTS"] = "true"

def pytest_collection_modifyitems(config, items):
    run_service_tests = os.getenv("RUN_SERVICE_TESTS", "true").lower() == "true"
    if not run_service_tests:
        skip_marker = pytest.mark.skip(reason="Skipping service tests in CI")
        for item in items:
            if "service" in item.keywords:
                item.add_marker(skip_marker)

# def pytest_runtest_setup(item):
#     if "service" in item.keywords and os.getenv("RUN_SERVICE_TESTS", "false").lower() != "true":
#         pytest.skip("Skipping service tests by default")
