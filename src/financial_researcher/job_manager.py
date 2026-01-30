"""Job management system for tracking research jobs."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from threading import Lock


class JobState(Enum):
    """Job execution states."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobStatus:
    """Represents the status of a research job."""
    job_id: str
    company_name: str
    state: JobState
    created_at: datetime
    updated_at: datetime
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    report_path: Optional[str] = None


class JobManager:
    """Manages research jobs and their status."""
    
    def __init__(self):
        self._jobs: Dict[str, JobStatus] = {}
        self._lock = Lock()
    
    def create_job(self, company_name: str) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        now = datetime.now()
        
        with self._lock:
            self._jobs[job_id] = JobStatus(
                job_id=job_id,
                company_name=company_name,
                state=JobState.QUEUED,
                created_at=now,
                updated_at=now
            )
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobStatus]:
        """Retrieve job status by ID."""
        with self._lock:
            return self._jobs.get(job_id)
    
    def update_job(self, job_id: str, state: JobState, message: Optional[str] = None) -> bool:
        """Update job state and optionally add a status message."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            job.state = state
            job.updated_at = datetime.now()
            
            if message:
                job.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            
            if state == JobState.FAILED and message:
                job.error_message = message
            
            return True
    
    def add_log(self, job_id: str, message: str) -> bool:
        """Add a log message to the job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            job.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            job.updated_at = datetime.now()
            return True
    
    def set_result(self, job_id: str, report_path: str) -> bool:
        """Set the completed report path for the job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            job.report_path = report_path
            job.state = JobState.COMPLETED
            job.updated_at = datetime.now()
            return True
    
    def get_logs(self, job_id: str) -> List[str]:
        """Get all logs for a job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return []
            return job.logs.copy()
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove jobs older than max_age_hours. Returns count of removed jobs."""
        now = datetime.now()
        removed = 0
        
        with self._lock:
            job_ids = list(self._jobs.keys())
            for job_id in job_ids:
                job = self._jobs[job_id]
                age_hours = (now - job.created_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    del self._jobs[job_id]
                    removed += 1
        
        return removed
