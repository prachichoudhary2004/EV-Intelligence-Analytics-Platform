import pandas as pd
from fpdf import FPDF
from config.config import config
from utils.logger import logger
import os

class ReportService:
    """
    Creates PDF and CSV reports for execs.
    """
    
    def export_to_csv(self, df, filename="market_report.csv"):
        """Save dataframe as CSV file."""
        path = config.BASE_DIR / "reports" / filename
        df.to_csv(path, index=False)
        logger.info(f"Report exported to CSV: {path}")
        return path

    def generate_pdf_report(self, kpis, narrative):
        """Make a nice PDF report for execs."""
        pdf = FPDF()
        pdf.add_page()
        
        # Title section
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(0, 255, 65) # Primary Green
        pdf.cell(200, 20, "EV Market Intelligence Platform", ln=True, align="C")
        
        pdf.set_font("Arial", "I", 12)
        pdf.set_text_color(160, 160, 160)
        pdf.cell(200, 10, "Executive Performance Report - Enterprise Edition", ln=True, align="C")
        pdf.ln(10)
        
        # Show the KPIs
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, "Market Performance Indicators", ln=True)
        pdf.set_font("Arial", "", 12)
        
        for key, val in kpis.items():
            pdf.cell(200, 8, f"- {key.replace('_', ' ').title()}: {val}", ln=True)
        
        pdf.ln(10)
        
        # Add the insights
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Strategic Insights", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, narrative.replace("#", "").replace("*", "-"))
        
        # Save the file
        report_path = config.BASE_DIR / "reports" / "executive_summary.pdf"
        pdf.output(str(report_path))
        logger.info(f"Executive PDF generated at: {report_path}")
        return report_path

# Available app-wide
report_service = ReportService()
