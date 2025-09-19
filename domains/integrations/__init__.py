# domains/integrations - External Integration Layer
#
# This domain handles all external API integrations and cross-platform coordination.
# Moved from core/services per architectural refactoring to centralize integration logic.

from .smart_sync import SmartSyncService

__all__ = ["SmartSyncService"]
