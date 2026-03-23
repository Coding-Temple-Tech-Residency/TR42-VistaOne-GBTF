"""Coverage-focused tests for model reprs and schema post_load methods."""

import uuid

from app.models.audit_log import AuditLog
from app.models.biometric_verifications import BiometricVerification
from app.models.contractor_credentials import ContractorCredential
from app.models.contractor_devices import ContractorDevice
from app.models.contractor_insurance import ContractorInsurance
from app.models.contractor_sessions import ContractorSession
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
from app.schemas.audit_log import AuditLogSchema
from app.schemas.biometric_verification import BiometricVerificationSchema
from app.schemas.contractor_credential import ContractorCredentialSchema
from app.schemas.contractor_device import ContractorDeviceSchema
from app.schemas.contractor_insurance import ContractorInsuranceSchema
from app.schemas.contractor_session import ContractorSessionSchema
from app.schemas.job import JobSchema
from app.schemas.job_assignment import JobAssignmentSchema
from app.schemas.job_completion import JobCompletionSchema
from app.schemas.job_response import JobResponseSchema
from app.schemas.local_sync_queue import LocalSyncQueueSchema
from app.schemas.notification_preference import NotificationPreferenceSchema
from app.schemas.progress_update import ProgressUpdateSchema
from app.schemas.task import TaskSchema
from app.schemas.vendor_sync_queue import VendorSyncQueueSchema


def test_schema_loads_cover_post_load_and_model_repr():
    contractor_id = uuid.uuid4()
    job_id = uuid.uuid4()
    vendor_id = uuid.uuid4()

    audit_log = AuditLogSchema().load(
        {
            "table_name": "contractors",
            "record_id": str(uuid.uuid4()),
            "action": "INSERT",
        }
    )
    assert isinstance(audit_log, AuditLog)
    assert "AuditLog" in repr(audit_log)

    biometric = BiometricVerificationSchema().load(
        {
            "contractor_id": str(contractor_id),
            "verification_type": "check_in",
        }
    )
    assert isinstance(biometric, BiometricVerification)
    assert "BiometricVerification" in repr(biometric)

    credential = ContractorCredentialSchema().load(
        {
            "contractor_id": str(contractor_id),
            "credential_type": "license",
            "credential_name": "Electrical License",
        }
    )
    assert isinstance(credential, ContractorCredential)
    assert "Electrical License" in repr(credential)

    device = ContractorDeviceSchema().load(
        {
            "contractor_id": str(contractor_id),
            "device_id": "device-123",
            "device_name": "iPhone",
            "device_type": "ios",
        }
    )
    assert isinstance(device, ContractorDevice)
    assert "iPhone" in repr(device)

    insurance = ContractorInsuranceSchema().load(
        {
            "contractor_id": str(contractor_id),
            "insurance_type": "general_liability",
            "policy_number": "POL-123",
        }
    )
    assert isinstance(insurance, ContractorInsurance)
    assert "POL-123" in repr(insurance)

    session = ContractorSessionSchema().load(
        {
            "contractor_id": str(contractor_id),
        }
    )
    assert isinstance(session, ContractorSession)
    assert "ContractorSession" in repr(session)

    job = JobSchema().load(
        {
            "job_number": "JOB-REPR-1",
        }
    )
    assert isinstance(job, Job)
    assert "JOB-REPR-1" in repr(job)

    assignment = JobAssignmentSchema().load(
        {
            "job_id": str(job_id),
            "contractor_id": str(contractor_id),
        }
    )
    assert isinstance(assignment, JobAssignment)
    assert "job=" in repr(assignment)

    completion = JobCompletionSchema().load(
        {
            "job_id": str(job_id),
            "contractor_id": str(contractor_id),
        }
    )
    assert isinstance(completion, JobCompletion)
    assert "JobCompletion" in repr(completion)

    response = JobResponseSchema().load(
        {
            "job_id": str(job_id),
            "contractor_id": str(contractor_id),
            "response_type": "accept",
        }
    )
    assert isinstance(response, JobResponse)
    assert "JobResponse" in repr(response)

    local_sync = LocalSyncQueueSchema().load(
        {
            "contractor_id": str(contractor_id),
            "table_name": "site_visits",
            "record_id": str(uuid.uuid4()),
            "operation": "INSERT",
        }
    )
    assert isinstance(local_sync, LocalSyncQueue)
    assert "LocalSyncQueue" in repr(local_sync)

    preference = NotificationPreferenceSchema().load(
        {
            "contractor_id": str(contractor_id),
        }
    )
    assert isinstance(preference, NotificationPreference)
    assert str(contractor_id) in repr(preference)

    progress = ProgressUpdateSchema().make_progress_update(
        {
            "job_id": job_id,
            "contractor_id": contractor_id,
            "work_description": "Installed conduit",
        }
    )
    assert isinstance(progress, ProgressUpdate)
    assert "ProgressUpdate" in repr(progress)

    task = TaskSchema().load(
        {
            "job_id": str(job_id),
            "task_name": "Inspect panel",
        }
    )
    assert isinstance(task, Task)
    assert "Inspect panel" in repr(task)

    vendor_sync = VendorSyncQueueSchema().load(
        {
            "vendor_id": str(vendor_id),
            "direction": "outbound",
            "entity_type": "job",
            "payload": {"job_id": str(job_id)},
        }
    )
    assert isinstance(vendor_sync, VendorSyncQueue)
    assert "VendorSyncQueue" in repr(vendor_sync)


def test_remaining_model_repr_methods():
    issue = Issue(job_id=uuid.uuid4(), issue_title="Broken hinge")
    assert "Broken hinge" in repr(issue)

    photo = Photo(
        job_id=uuid.uuid4(),
        contractor_id=uuid.uuid4(),
        photo_url="https://example.com/photo.jpg",
        photo_filename="photo.jpg",
    )
    assert "photo.jpg" in repr(photo)

    visit = SiteVisit(job_id=uuid.uuid4(), contractor_id=uuid.uuid4())
    assert "SiteVisit" in repr(visit)

    submission = Submission(
        job_id=uuid.uuid4(),
        contractor_id=uuid.uuid4(),
        submission_number="SUB-100",
    )
    assert "SUB-100" in repr(submission)

    execution = TaskExecution(
        task_id=uuid.uuid4(),
        job_id=uuid.uuid4(),
        contractor_id=uuid.uuid4(),
    )
    assert "TaskExecution" in repr(execution)

    vendor = Vendor(vendor_code="V-100", vendor_name="Vendor 100")
    assert "V-100" in repr(vendor)
