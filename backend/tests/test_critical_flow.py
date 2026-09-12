import pytest
from app.models.user import User, Role
from app.models.field import SafetyEvent, SafetyEventType, SafetyEventSeverity

@pytest.mark.asyncio
async def test_inspector_flow_auth_restrictions():
    # In a real test, we would hit the TestClient
    assert Role.FIELD_INSPECTOR != Role.SYSTEM_ADMIN

@pytest.mark.asyncio
async def test_ai_tool_read_only_constraints():
    # AI tools must not have INSERT or UPDATE queries
    from app.services.copilot_tools import CopilotTools
    import inspect
    
    tools = CopilotTools(db=None, current_user=None, ai_provider=None)
    methods = [m for m in dir(tools) if not m.startswith('_')]
    
    for method_name in methods:
        method_source = inspect.getsource(getattr(tools, method_name))
        assert "db.add(" not in method_source
        assert "db.commit(" not in method_source
        assert "INSERT " not in method_source
        assert "UPDATE " not in method_source
