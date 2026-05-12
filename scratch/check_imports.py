import sys
import os

# Add root to path
sys.path.append(os.getcwd())

print("Checking Service Imports...")

try:
    from services.spark_engine import spark_engine
    print("SUCCESS: spark_engine imported")
except Exception as e:
    print(f"FAILED: spark_engine import failed: {e}")

try:
    from services.kpi_engine import kpi_engine
    print("SUCCESS: kpi_engine imported")
except Exception as e:
    print(f"FAILED: kpi_engine import failed: {e}")

try:
    from services.insight_engine import insight_engine
    print("SUCCESS: insight_engine imported")
except Exception as e:
    print(f"FAILED: insight_engine import failed: {e}")

try:
    from services.streaming_service import streaming_service
    print("SUCCESS: streaming_service imported")
except Exception as e:
    print(f"FAILED: streaming_service import failed: {e}")

try:
    from models.forecaster import forecaster
    print("SUCCESS: forecaster imported")
except Exception as e:
    print(f"FAILED: forecaster import failed: {e}")

try:
    from services.data_quality import dq_monitor
    print("SUCCESS: dq_monitor imported")
except Exception as e:
    print(f"FAILED: dq_monitor import failed: {e}")
