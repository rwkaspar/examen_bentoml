import sys
import os
import pytest

if "RUN_SERVICE_TESTS" not in os.environ:
    os.environ["RUN_SERVICE_TESTS"] = "true"


# def pytest_runtest_setup(item):
#     if "service" in item.keywords and os.getenv("RUN_SERVICE_TESTS", "false").lower() != "true":
#         pytest.skip("Skipping service tests by default")
