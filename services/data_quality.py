import pandas as pd
import numpy as np
from utils.logger import logger

class DataQualityMonitor:
    """
    Enterprise-level data quality monitoring and health checks.
    """
    def __init__(self):
        self.health_reports = {}

    def check_dataframe(self, df, name="Dataset"):
        """Perform a suite of health checks on a dataframe."""
        logger.info(f"Running data quality checks on: {name}")
        
        report = {
            "name": name,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "schema": df.dtypes.apply(lambda x: str(x)).to_dict(),
            "numeric_stats": df.describe().to_dict() if not df.select_dtypes(include=[np.number]).empty else {}
        }
        
        # Calculate overall quality score (simple heuristic)
        missing_penalty = (df.isnull().sum().sum() / (df.size)) * 100 if df.size > 0 else 0
        duplicate_penalty = (report["duplicate_rows"] / len(df)) * 100 if len(df) > 0 else 0
        
        quality_score = max(0, 100 - missing_penalty - duplicate_penalty)
        report["quality_score"] = round(quality_score, 2)
        
        self.health_reports[name] = report
        
        if quality_score < 90:
            logger.warning(f"Data Quality Alert for {name}: Score {quality_score}%")
        else:
            logger.info(f"Data Quality Passed for {name}: Score {quality_score}%")
            
        return report

    def validate_schema(self, df, expected_columns):
        """Check for schema drift."""
        missing_cols = set(expected_columns) - set(df.columns)
        extra_cols = set(df.columns) - set(expected_columns)
        
        if missing_cols:
            logger.error(f"Schema Drift Detected: Missing columns {missing_cols}")
            return False
        return True

    def get_summary_report(self):
        """Return all health reports as a single summary."""
        return self.health_reports

# Global instance
dq_monitor = DataQualityMonitor()
