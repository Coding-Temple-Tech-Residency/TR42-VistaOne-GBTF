# Import all schema classes
from .audit_log import AuditLogSchema
from .auth import LoginSchema
from .biometric_verification import BiometricVerificationSchema
from .contractor import ContractorSchema
from .contractor_credential import ContractorCredentialSchema
from .contractor_device import ContractorDeviceSchema
from .contractor_insurance import ContractorInsuranceSchema
from .contractor_session import ContractorSessionSchema
from .issue import IssueSchema
from .job import JobSchema
from .job_assignment import JobAssignmentSchema
from .job_completion import JobCompletionSchema
from .job_response import JobResponseSchema
from .local_sync_queue import LocalSyncQueueSchema
from .notification_preference import NotificationPreferenceSchema
from .photo import PhotoSchema
from .progress_update import ProgressUpdateSchema
from .site_visit import SiteVisitSchema
from .submission import SubmissionSchema
from .task import TaskSchema
from .task_execution import TaskExecutionSchema
from .vendor import VendorSchema
from .vendor_sync_queue import VendorSyncQueueSchema

# List all schemas for easy import
__all__ = [
    "ContractorSchema",
    "JobSchema",
    "VendorSchema",
    "VendorSyncQueueSchema",
    "ContractorCredentialSchema",
    "ContractorInsuranceSchema",
    "ContractorDeviceSchema",
    "NotificationPreferenceSchema",
    "JobAssignmentSchema",
    "BiometricVerificationSchema",
    "JobResponseSchema",
    "SiteVisitSchema",
    "ProgressUpdateSchema",
    "TaskSchema",
    "TaskExecutionSchema",
    "IssueSchema",
    "PhotoSchema",
    "JobCompletionSchema",
    "SubmissionSchema",
    "ContractorSessionSchema",
    "LocalSyncQueueSchema",
    "AuditLogSchema",
    "LoginSchema",
]
