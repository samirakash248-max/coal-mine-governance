from enum import Enum
from typing import Set, Dict
from app.models.user import Role

class Permission(str, Enum):
    # Dashboards & Basic
    DASHBOARD_READ = "dashboard:read"
    
    # Mines
    MINE_READ = "mine:read"
    MINE_MANAGE = "mine:manage"
    
    # Inspections
    INSPECTION_READ = "inspection:read"
    INSPECTION_CREATE = "inspection:create"
    INSPECTION_UPDATE = "inspection:update"
    INSPECTION_APPROVE = "inspection:approve"
    
    # Safety
    SAFETY_READ = "safety:read"
    SAFETY_CREATE = "safety:create"
    SAFETY_UPDATE = "safety:update"
    
    # Risk
    RISK_READ = "risk:read"
    RISK_MANAGE = "risk:manage"
    
    # Weather/Environmental
    WEATHER_READ = "weather:read"
    
    # Compliance
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_CREATE = "compliance:create"
    COMPLIANCE_UPDATE = "compliance:update"
    COMPLIANCE_APPROVE = "compliance:approve"
    
    # Documents
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_VERIFY = "document:verify"
    
    # Reports
    REPORT_READ = "report:read"
    REPORT_CREATE = "report:create"
    REPORT_APPROVE = "report:approve"
    
    # Grievances
    GRIEVANCE_READ = "grievance:read"
    GRIEVANCE_CREATE = "grievance:create"
    GRIEVANCE_UPDATE = "grievance:update"
    GRIEVANCE_RESOLVE = "grievance:resolve"
    
    # Audit
    AUDIT_READ = "audit:read"
    
    # Users
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Copilot
    COPILOT_USE = "copilot:use"


# Map roles to their permissions
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.SYSTEM_ADMIN: set(Permission),  # Full access
    
    Role.MINE_MANAGER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ, Permission.MINE_MANAGE,
        Permission.INSPECTION_READ, Permission.INSPECTION_APPROVE,
        Permission.SAFETY_READ, Permission.SAFETY_UPDATE,
        Permission.RISK_READ, Permission.RISK_MANAGE,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_CREATE, Permission.COMPLIANCE_UPDATE, Permission.COMPLIANCE_APPROVE,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_UPLOAD, Permission.DOCUMENT_VERIFY,
        Permission.REPORT_READ, Permission.REPORT_CREATE, Permission.REPORT_APPROVE,
        Permission.GRIEVANCE_READ, Permission.GRIEVANCE_RESOLVE,
        Permission.AUDIT_READ,
        Permission.COPILOT_USE,
    },
    
    Role.SAFETY_OFFICER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ, Permission.INSPECTION_CREATE, Permission.INSPECTION_UPDATE,
        Permission.SAFETY_READ, Permission.SAFETY_CREATE, Permission.SAFETY_UPDATE,
        Permission.RISK_READ, Permission.RISK_MANAGE,
        Permission.WEATHER_READ,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_UPLOAD,
        Permission.REPORT_READ, Permission.REPORT_CREATE,
        Permission.COPILOT_USE,
    },
    
    Role.MINE_OFFICER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ,
        Permission.SAFETY_READ, Permission.SAFETY_CREATE,
        Permission.RISK_READ,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_CREATE,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_UPLOAD,
        Permission.REPORT_READ, Permission.REPORT_CREATE,
        Permission.COPILOT_USE,
    },
    
    Role.FIELD_INSPECTOR: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ, Permission.INSPECTION_CREATE, Permission.INSPECTION_UPDATE,
        Permission.SAFETY_READ, Permission.SAFETY_CREATE,
        Permission.WEATHER_READ,
        Permission.DOCUMENT_READ,
        Permission.REPORT_READ,
    },
    
    Role.INSPECTOR: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ, Permission.INSPECTION_CREATE, Permission.INSPECTION_UPDATE,
        Permission.SAFETY_READ, Permission.SAFETY_CREATE,
        Permission.WEATHER_READ,
        Permission.DOCUMENT_READ,
        Permission.REPORT_READ,
    },
    
    Role.ENVIRONMENT_OFFICER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_CREATE, Permission.COMPLIANCE_UPDATE,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_UPLOAD,
        Permission.REPORT_READ, Permission.REPORT_CREATE,
        Permission.COPILOT_USE,
    },
    
    Role.CONTRACTOR: {
        Permission.MINE_READ,
        Permission.SAFETY_CREATE,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_UPLOAD,
        Permission.GRIEVANCE_CREATE,
    },
    
    Role.REGULATORY_AUDITOR: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ,
        Permission.SAFETY_READ,
        Permission.RISK_READ,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_APPROVE,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_VERIFY,
        Permission.REPORT_READ, Permission.REPORT_APPROVE,
        Permission.AUDIT_READ,
    },
    
    Role.REGULATOR: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ,
        Permission.SAFETY_READ,
        Permission.RISK_READ,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ, Permission.COMPLIANCE_APPROVE,
        Permission.DOCUMENT_READ, Permission.DOCUMENT_VERIFY,
        Permission.REPORT_READ, Permission.REPORT_APPROVE,
        Permission.AUDIT_READ,
    },
    
    Role.FIELD_OFFICER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.SAFETY_CREATE,
        Permission.INSPECTION_CREATE,
    },
    
    Role.REGIONAL_MANAGER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ,
        Permission.SAFETY_READ,
        Permission.RISK_READ,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ,
        Permission.DOCUMENT_READ,
        Permission.REPORT_READ, Permission.REPORT_APPROVE,
        Permission.AUDIT_READ,
        Permission.COPILOT_USE,
    },
    
    Role.CORPORATE_MANAGER: {
        Permission.DASHBOARD_READ,
        Permission.MINE_READ,
        Permission.INSPECTION_READ,
        Permission.SAFETY_READ,
        Permission.RISK_READ,
        Permission.WEATHER_READ,
        Permission.COMPLIANCE_READ,
        Permission.DOCUMENT_READ,
        Permission.REPORT_READ, Permission.REPORT_APPROVE,
        Permission.AUDIT_READ,
        Permission.COPILOT_USE,
    },
}

def get_role_permissions(role: Role) -> Set[Permission]:
    """Returns a set of permissions for the given role."""
    return ROLE_PERMISSIONS.get(role, set())
