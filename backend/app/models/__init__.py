from app.models.audit_log import AuditLog
from app.models.biometric_verifications import BiometricVerification
from app.models.contractor_credentials import ContractorCredential
from app.models.contractor_devices import ContractorDevice
from app.models.contractor_insurance import ContractorInsurance
from app.models.contractor_sessions import ContractorSession
from app.models.contractors import Contractor
from app.models.issues import Issue
from app.models.job_assignments import JobAssignment
from app.models.job_completions import JobCompletion
from app.models.job_responses import JobResponse
from app.models.jobs import Job
from app.models.local_sync_queue import LocalSyncQueue
from app.models.notification_preferences import NotificationPreference
from app.models.photos import Photo
from app.models.progress_updates import ProgressUpdate
from app.models.site_visits import SiteVisit
from app.models.submissions import Submission
from app.models.task_executions import TaskExecution
from app.models.tasks import Task
from app.models.vendor_sync_queue import VendorSyncQueue
from app.models.vendors import Vendor

# Import all models for Alembic
__all__ = [
    "Contractor",
    "ContractorCredential",
    "ContractorInsurance",
    "ContractorDevice",
    "NotificationPreference",
    "Vendor",
    "VendorSyncQueue",
    "Job",
    "JobAssignment",
    "BiometricVerification",
    "JobResponse",
    "SiteVisit",
    "ProgressUpdate",
    "Task",
    "TaskExecution",
    "Issue",
    "Photo",
    "JobCompletion",
    "Submission",
    "ContractorSession",
    "LocalSyncQueue",
    "AuditLog",
]
