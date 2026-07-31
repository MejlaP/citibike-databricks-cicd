"""Shared pytest fixtures for local unit testing."""

import os
import sys

import pytest

# Force Spark to use THIS venv's Python for both the driver and the worker
# process it spawns. Without this, Spark can pick up a different Python
# installation from the system PATH (e.g. Anaconda), causing import errors
# or version mismatches between driver and worker.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Windows-specific fix: Spark's internal networking can fail if it tries to
# resolve the machine's real hostname (especially if it contains an
# underscore, which is an invalid character for Spark's URLs). Forcing
# 127.0.0.1 (localhost) sidesteps hostname resolution entirely.
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

# Force UTF-8 everywhere. Windows consoles often default to a legacy
# codepage (e.g. cp1250), which can cause silent encoding-related crashes
# in subprocesses like the Spark Python worker.
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"


@pytest.fixture(scope="session")
# @pytest.fixture marks this function as a pytest fixture — reusable setup
# code that test functions can request just by having a parameter with the
# same name (e.g. "def test_x(spark):"). Pytest calls this function
# automatically and passes its return value in; the test never calls
# spark() itself.
#
# scope="session" controls how often it's re-created: instead of the
# default ("function" — a fresh SparkSession for every single test, which
# would be slow), "session" means it's built ONCE for the entire pytest
# run and then shared/reused by every test that asks for it. This matters
# a lot here because creating the SparkSession via Databricks Connect
# involves waking up the remote compute, which is slow (~16s) — we only
# want to pay that cost once, not once per test.
def spark():
    """Provide a SparkSession fixture — tries Databricks Connect first,
    falls back to plain local PySpark if it's not installed (e.g. in the
    .venv_pyspark environment used for local unit testing)."""
    try:
        # Preferred path: if databricks-connect is installed in this venv,
        # use it to run the tests against a real remote Databricks cluster
        # instead of spinning up Spark locally.
        from databricks.connect import DatabricksSession
        return DatabricksSession.builder.getOrCreate()
    except ImportError:
        # NOTE: this fallback path was never successfully validated on
        # Windows — see working notes "Troubleshooting" for the full debugging story. Kept as a
        # starting point for future local testing (e.g. via WSL), not
        # currently used — tests run through the DatabricksSession branch
        # above instead.

        # Fallback path: no databricks-connect available (e.g. we're in
        # .venv_pyspark, which only has plain PySpark) — start a local
        # single-machine Spark session instead.

        # Redundant with the module-level line above, but kept here so this
        # fallback branch is self-contained even if the top of the file
        # changes later.
        os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

        from pyspark.sql import SparkSession
        return (
            SparkSession.builder
            # local[1] = run Spark with a single worker thread. Was
            # originally local[*] (use all CPU cores) but was narrowed
            # down to 1 while debugging a worker-crash issue, to rule out
            # problems caused by parallelism.
            .master("local[1]")
            # Same hostname fix as above, but as a Spark config key instead
            # of an env var — belt-and-braces during the same debugging
            # session.
            .config("spark.driver.host", "127.0.0.1")
            # Asks Spark to enable Python's faulthandler in the worker
            # process, so that if the worker crashes it prints a Python
            # traceback instead of failing silently with just a generic
            # Java-side EOFException. Added while trying to diagnose the
            # worker-crash issue; harmless to leave in.
            .config("spark.python.worker.faulthandler.enabled", "true")
            .getOrCreate()
        )