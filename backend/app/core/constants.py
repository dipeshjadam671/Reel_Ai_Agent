from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class TaskStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class CycleStatus(str, Enum):
    CREATED = "created"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    MEDIA_CURATION = "media_curation"
    PRODUCING = "producing"
    COMPLIANCE_CHECK = "compliance_check"
    QA_CHECK = "qa_check"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    REGENERATING = "regenerating"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

class SocialPlatform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"

class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    PORTUGUESE = "pt"

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    NOVELTY_CHECK_FAILED = "NOVELTY_CHECK_FAILED"
    FACT_CHECK_FAILED = "FACT_CHECK_FAILED"
    COMPLIANCE_REJECTED = "COMPLIANCE_REJECTED"
    QA_REJECTED = "QA_REJECTED"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    RENDER_FAILED = "RENDER_FAILED"
    PUBLISHING_FAILED = "PUBLISHING_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
