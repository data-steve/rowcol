"""
_decorators.py
Provides the audit_log decorator for logging service method actions. Supports standardized logging for CREATE, UPDATE, and DISPOSITION actions with optional metadata for detailed audit trails.
"""

import functools
import inspect
from typing import Any, Callable, Optional, Dict
from app.models.enums import AuditAction, EntityType
from app.services.audit_log import AuditService

def audit_log(
    action: AuditAction, 
    entity_type: EntityType, 
    id_arg: str = "id", 
    context_extractor: Optional[Callable] = None,
    metadata: Optional[Dict] = None
):
    """
    Decorator to automatically log audit events for service methods.
    
    Extracts entity ID and user from method arguments, logs the action with AuditService, and supports
    custom context extraction and metadata for detailed audit trails. Suitable for standardized actions
    (CREATE, UPDATE, DISPOSITION). For complex, multi-entity operations, consider handwritten audit logs.
    
    Args:
        action (AuditAction): The type of action being performed (e.g., CREATE, UPDATE).
        entity_type (EntityType): The type of entity being affected (e.g., ASSET, CLIENT).
        id_arg (str): The name of the argument in the decorated function that holds the entity's ID.
        context_extractor (Callable, optional): A function to extract the audit payload from the result.
        metadata (Dict, optional): Additional metadata for the audit log (e.g., {"operation": "batch_create"}).
    
    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            service_instance = args[0]
            result = await func(*args, **kwargs)

            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            current_user = bound_args.arguments.get("current_user")
            cause_id = bound_args.arguments.get("cause_id")
            entity_id = bound_args.arguments.get(id_arg)
            
            if not entity_id:
                if isinstance(result, dict):
                    entity_id = result.get("id")
                elif hasattr(result, "id"):
                    entity_id = result.id
                
            if not current_user:
                print(f"Warning: could not find 'current_user' for audit log in {func.__name__}")
                return result

            audit_payload = context_extractor(result) if context_extractor else result
            # Include metadata in the audit payload if provided
            if metadata:
                audit_payload = {**audit_payload, "metadata": metadata}

            audit_service = AuditService(
                db=service_instance.db, 
                request=getattr(service_instance, 'request', None)
            )
            await audit_service.log_audit_event(
                user_id=str(current_user.id),
                business_id=str(current_user.business_id),
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                new_values=audit_payload,
                cause_id=cause_id
            )
            
            return result
        return wrapper
    return decorator