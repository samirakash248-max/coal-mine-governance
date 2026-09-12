from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
from app.models.field import CorrectiveAction, ActionStatus, SafetyEvent
from app.models.workflow import AuditLog
from app.models.user import User, Role

class WorkflowService:
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db; self.current_user = current_user

    async def _log_audit(self, action: str, entity_type: str, entity_id: uuid.UUID, before: dict = None, after: dict = None):
        log = AuditLog(user_id=self.current_user.id, role=self.current_user.role, action=action, entity_type=entity_type, entity_id=entity_id, before_state=before, after_state=after, hash_signature='hash-placeholder')
        self.db.add(log)

    async def transition_action(self, action_id: uuid.UUID, new_status: ActionStatus) -> CorrectiveAction:
        stmt = select(CorrectiveAction).where(CorrectiveAction.id == action_id)
        action = (await self.db.execute(stmt)).scalar_one_or_none()
        if not action: raise ValueError('CorrectiveAction not found')
        old_status = action.status
        if old_status == new_status: return action
        if new_status in [ActionStatus.RESOLVED, ActionStatus.CLOSED]:
            if self.current_user.role not in [Role.MINE_MANAGER, Role.REGULATORY_AUDITOR]:
                raise PermissionError('Only authorized managers can close or resolve an action.')
        before_state = {'status': old_status.value}
        after_state = {'status': new_status.value}
        action.status = new_status
        await self._log_audit(action='TRANSITION_STATUS', entity_type='CorrectiveAction', entity_id=action.id, before=before_state, after=after_state)
        await self.db.commit()
        await self.db.refresh(action)
        return action
        
    async def review_ai_prediction(self, event_id: uuid.UUID, event_type: str, category: str, severity: str) -> SafetyEvent:
        stmt = select(SafetyEvent).where(SafetyEvent.id == event_id)
        event = (await self.db.execute(stmt)).scalar_one_or_none()
        if not event: raise ValueError('SafetyEvent not found')
        before_state = {'type': event.type.value if hasattr(event.type, 'value') else event.type, 'category': event.category.value if hasattr(event.category, 'value') else event.category, 'severity': event.severity.value if hasattr(event.severity, 'value') else event.severity}
        event.type = event_type; event.category = category; event.severity = severity
        event.human_reviewed_at = datetime.now(timezone.utc); event.human_reviewer_id = self.current_user.id
        after_state = {'type': event_type, 'category': category, 'severity': severity}
        is_override = (event_type != (event.ai_event_type.value if hasattr(event.ai_event_type, 'value') else event.ai_event_type) or category != (event.ai_category.value if hasattr(event.ai_category, 'value') else event.ai_category) or severity != (event.ai_severity.value if hasattr(event.ai_severity, 'value') else event.ai_severity))
        event.is_ai_overridden = is_override
        action_name = 'AI_RESULT_OVERRIDDEN' if is_override else 'AI_RESULT_APPROVED'
        await self._log_audit(action=action_name, entity_type='SafetyEvent', entity_id=event.id, before=before_state, after=after_state)
        await self.db.commit()
        await self.db.refresh(event)
        return event
