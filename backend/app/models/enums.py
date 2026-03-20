import enum


class AccountStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    pending = "pending"


class JobStatus(enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    assigned = "assigned"
    in_progress = "in_progress"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class PriorityLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class IssueSeverity(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    blocker = "blocker"


class IssueStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"
    wont_fix = "wont_fix"


class TaskStatus(enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"
    skipped = "skipped"


class VerificationType(enum.Enum):
    check_in = "check_in"
    check_out = "check_out"
    task = "task"
    job_acceptance = "job_acceptance"
    job_completion = "job_completion"
    delivery = "delivery"
    issue_report = "issue_report"
    identity_verify = "identity_verify"


class DeviceType(enum.Enum):
    ios = "ios"
    android = "android"
    tablet = "tablet"
    desktop = "desktop"
    web = "web"
    other = "other"


class SyncStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    conflict = "conflict"


class CredentialType(enum.Enum):
    license = "license"
    certification = "certification"
    training = "training"
    award = "award"


class VendorSyncStatus(enum.Enum):
    pending = "pending"
    synced = "synced"
    failed = "failed"
    ignored = "ignored"
