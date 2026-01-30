"""Crew runner that captures output and integrates with job management."""
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional

from financial_researcher.crew import FinancialResearcher
from financial_researcher.job_manager import JobManager, JobState
from financial_researcher.log_parser import LogParser


class CrewOutputCapture:
    """Captures stdout/stderr and forwards to job manager with parsing."""
    
    def __init__(self, job_manager: JobManager, job_id: str):
        self.job_manager = job_manager
        self.job_id = job_id
        self.buffer = io.StringIO()
        self.parser = LogParser()
    
    def write(self, text: str):
        """Write to buffer, parse, and forward to job manager."""
        if text and text.strip():
            self.buffer.write(text)
            
            # Add raw log
            self.job_manager.add_log(self.job_id, text.strip())
            
            # Parse and extract structured events
            events = self.parser.parse_line(text.strip())
            for event in events:
                self.job_manager.add_event(self.job_id, event)
        
        return len(text)
    
    def flush(self):
        """Flush the buffer."""
        self.buffer.flush()
    
    def getvalue(self) -> str:
        """Get all captured output."""
        return self.buffer.getvalue()


def run_crew_with_logging(company_name: str, job_manager: JobManager, job_id: str) -> Optional[str]:
    """
    Run the financial research crew with output capture.
    
    Args:
        company_name: The company to research
        job_manager: JobManager instance to track progress
        job_id: The job ID to update
    
    Returns:
        Path to the generated report, or None if failed
    """
    # Update job to running state
    job_manager.update_job(job_id, JobState.RUNNING, f"Starting research for {company_name}...")
    
    try:
        # Create output capture
        capture = CrewOutputCapture(job_manager, job_id)
        
        # Prepare inputs
        inputs = {'company': company_name}
        
        # Run crew with output capture
        job_manager.add_log(job_id, "Initializing AI agents...")
        
        with redirect_stdout(capture), redirect_stderr(capture):
            crew_instance = FinancialResearcher()
            result = crew_instance.crew().kickoff(inputs=inputs)
        
        # Determine report path
        report_path = f"output/report_{company_name}.md"
        
        job_manager.add_log(job_id, "Research completed successfully!")
        job_manager.set_result(job_id, report_path)
        
        return report_path
        
    except Exception as e:
        error_msg = f"Error during research: {str(e)}"
        job_manager.update_job(job_id, JobState.FAILED, error_msg)
        return None
