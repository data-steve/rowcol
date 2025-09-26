## **Infrastructure Phase 3: Create Notifications Backlog**

*Generated from infrastructure consolidation Phase 3 on 2025-01-27*

**Instructions:**
1. **Create Git Branch**: `git checkout -b cleanup/notifications`
2. **Execute Tasks Sequentially**: Work through tasks in order (they have dependencies)
3. **For Each Task**: Follow the specific implementation patterns and verification steps
4. **Test After Each Task**: Run the specified verification commands
5. **Commit After Each Task**: `git add . && git commit -m "Task: [task-name] - [brief summary]"`
6. **When All Tasks Complete**: `git checkout main && git merge cleanup/notifications && git branch -d cleanup/notifications`

**Git Workflow:**
```bash
# Start this cleanup phase
git checkout -b cleanup/notifications

# Execute tasks in order, committing after each major change
git add .
git commit -m "Task: Audit notifications - Documented current architecture"

# When all tasks complete, merge back
git checkout main
git merge cleanup/notifications
git branch -d cleanup/notifications
```

**Rollback Plan:**
```bash
# If this phase fails, abandon it
git checkout main
git branch -D cleanup/notifications

# Or rollback specific changes
git checkout main
git reset --hard HEAD~1  # Go back one commit
```

**Context for All Tasks:**
- **Notifications**: Email, SMS, webhook, and other notification delivery systems
- **Current State**: Scattered across `runway/experiences/digest.py` (commented email service), and other locations
- **Target**: Consolidated in `infra/notifications/` with clear separation of concerns
- **ADR Reference**: See ADR-004 for model complexity standards and documentation requirements

**CRITICAL WARNINGS FROM PAINFUL LESSONS:**
- **NEVER** assume notification code is simple - it often has complex templating and delivery logic
- **ALWAYS** check for commented-out code that might be important
- **ALWAYS** test notification delivery in development before deploying
- **NEVER** hardcode email templates or notification content
- **ALWAYS** verify that notification providers (SendGrid, Twilio, etc.) are properly configured

---

## **Phase 1: Analyze Current Notification Code (P0 Critical)**

#### **Task: Audit Current Notification Code**
- **Status:** `[ ]` Not started
- **Justification:** Need to understand all notification code before consolidating to avoid breaking existing functionality.
- **Specific Files to Analyze:**
  - `runway/experiences/digest.py` - Commented email service code
  - `runway/experiences/` - Any other notification-related code
  - `domains/` - Any notification logic in domain services
  - `runway/routes/` - Any notification endpoints
- **Search Commands to Run:**
  - `grep -r "email\|sms\|webhook\|notification" . --include="*.py"`
  - `grep -r "sendgrid\|twilio\|mailgun\|smtp" . --include="*.py"`
  - `grep -r "template\|template.*email\|email.*template" . --include="*.py"`
- **Required Analysis:**
  - Document all notification types currently supported
  - Identify all notification providers and configurations
  - Map all notification templates and content
  - List all notification delivery logic
- **Dependencies:** None
- **Verification:** 
  - Create comprehensive list of all notification functionality
  - Document current notification architecture
  - Identify any hardcoded templates or configurations
- **Definition of Done:**
  - Complete inventory of all notification code
  - Clear understanding of current architecture
  - List of all notification types and providers
  - Documentation of template logic
- **Next Action:** Execute Task 1: Audit Current Notification Code

---

#### **Task: Create infra/notifications/ Directory Structure**
- **Status:** `[ ]` Not started
- **Justification:** Need proper directory structure for consolidated notification infrastructure.
- **Directory Structure to Create:**
  - `infra/notifications/` - Main directory
  - `infra/notifications/email_service.py` - Email notification service
  - `infra/notifications/sms_service.py` - SMS notification service
  - `infra/notifications/webhook_service.py` - Webhook notification service
  - `infra/notifications/templates/` - Notification templates directory
  - `infra/notifications/providers/` - Notification provider implementations
  - `infra/notifications/__init__.py` - Package initialization
- **Dependencies:** `Audit Current Notification Code`
- **Verification:** 
  - Run `ls -la infra/notifications/` - should show all directories and files
  - Run `python -c "import infra.notifications"` - should import without errors
- **Definition of Done:**
  - All directory structure created
  - All files have proper docstrings
  - Package imports work correctly
- **Next Action:** Execute Task 2: Create infra/notifications/ Directory Structure

---

## **Phase 2: Consolidate Notification Services (P1 High)**

#### **Task: Create Email Notification Service**
- **Status:** `[ ]` Not started
- **Justification:** Centralize email notification functionality with proper templating and delivery.
- **Target File:**
  - `infra/notifications/email_service.py` - Email notification service
- **Required Features:**
  - Email template management
  - Multiple provider support (SendGrid, SMTP, etc.)
  - Email validation and sanitization
  - Delivery tracking and retry logic
  - HTML and text email support
- **Dependencies:** `Create infra/notifications/ Directory Structure`
- **Verification:** 
  - Run `python -c "from infra.notifications.email_service import *"` - should import without errors
  - Test email sending in development
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Email service created with all required features
  - Template management implemented
  - Provider abstraction working
  - Email sending tested and working
- **Next Action:** Execute Task 3: Create Email Notification Service

---

#### **Task: Create SMS Notification Service**
- **Status:** `[ ]` Not started
- **Justification:** Centralize SMS notification functionality with proper provider support.
- **Target File:**
  - `infra/notifications/sms_service.py` - SMS notification service
- **Required Features:**
  - Multiple provider support (Twilio, AWS SNS, etc.)
  - SMS validation and formatting
  - Delivery tracking and retry logic
  - International number support
- **Dependencies:** `Create Email Notification Service`
- **Verification:** 
  - Run `python -c "from infra.notifications.sms_service import *"` - should import without errors
  - Test SMS sending in development
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - SMS service created with all required features
  - Provider abstraction working
  - SMS sending tested and working
- **Next Action:** Execute Task 4: Create SMS Notification Service

---

#### **Task: Create Webhook Notification Service**
- **Status:** `[ ]` Not started
- **Justification:** Centralize webhook notification functionality for external integrations.
- **Target File:**
  - `infra/notifications/webhook_service.py` - Webhook notification service
- **Required Features:**
  - Webhook endpoint management
  - Payload validation and formatting
  - Delivery tracking and retry logic
  - Security (signatures, authentication)
- **Dependencies:** `Create SMS Notification Service`
- **Verification:** 
  - Run `python -c "from infra.notifications.webhook_service import *"` - should import without errors
  - Test webhook sending in development
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Webhook service created with all required features
  - Security features implemented
  - Webhook sending tested and working
- **Next Action:** Execute Task 5: Create Webhook Notification Service

---

## **Phase 3: Create Notification Templates (P1 High)**

#### **Task: Create Notification Template System**
- **Status:** `[ ]` Not started
- **Justification:** Centralize notification templates for consistent messaging across all notification types.
- **Target Directory:**
  - `infra/notifications/templates/` - Notification templates
- **Required Templates:**
  - Email templates (HTML and text)
  - SMS templates
  - Webhook payload templates
  - Template variable substitution
- **Dependencies:** `Create Webhook Notification Service`
- **Verification:** 
  - Run `ls -la infra/notifications/templates/` - should show all template files
  - Test template rendering with sample data
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Template system created
  - All required templates implemented
  - Template rendering tested and working
  - Variable substitution working correctly
- **Next Action:** Execute Task 6: Create Notification Template System

---

## **Phase 4: Integrate with Existing Code (P2 Medium)**

#### **Task: Integrate Notifications with Digest Experience**
- **Status:** `[ ]` Not started
- **Justification:** Replace commented email service in digest.py with new notification infrastructure.
- **Specific Files to Update:**
  - `runway/experiences/digest.py` - Replace commented email service
- **Required Changes:**
  - Remove commented email service code
  - Integrate with new email notification service
  - Update digest email templates
  - Test digest email sending
- **Dependencies:** `Create Notification Template System`
- **Verification:** 
  - Run `grep -r "commented.*email\|email.*commented" runway/experiences/digest.py` - should return no results
  - Test digest email generation
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Commented email service removed
  - New notification service integrated
  - Digest emails working correctly
  - All tests pass
- **Next Action:** Execute Task 7: Integrate Notifications with Digest Experience

---

#### **Task: Update All Notification Imports**
- **Status:** `[ ]` Not started
- **Justification:** Update all imports throughout codebase to use new infra/notifications/ structure.
- **Search Commands to Run:**
  - `grep -r "email\|sms\|webhook\|notification" . --include="*.py"`
- **Dependencies:** `Integrate Notifications with Digest Experience`
- **Verification:** 
  - Run `grep -r "infra.notifications" . --include="*.py"` - should show new imports
  - Run `uvicorn main:app --reload` - should start without errors
  - Run `pytest` - should pass without failures
- **Definition of Done:**
  - All imports updated to use infra/notifications/
  - Application starts without errors
  - All tests pass
- **Next Action:** Execute Task 8: Update All Notification Imports

---

#### **Task: Test Notifications End-to-End**
- **Status:** `[ ]` Not started
- **Justification:** Verify that all notification functionality works correctly after consolidation.
- **Test Scenarios:**
  - Email notifications (digest, alerts, etc.)
  - SMS notifications (if implemented)
  - Webhook notifications (if implemented)
  - Template rendering
  - Provider switching
- **Dependencies:** `Update All Notification Imports`
- **Verification:** 
  - Test each notification type manually
  - Test template rendering with various data
  - Test provider functionality
  - Run `pytest` - should pass without failures
- **Definition of Done:**
  - All notification types work correctly
  - Template rendering works for all templates
  - All providers work correctly
  - All tests pass
- **Next Action:** Execute Task 9: Test Notifications End-to-End

---

**Summary:**
- **Total Tasks:** 8
- **P0 Critical:** 1 task
- **P1 High:** 5 tasks
- **P2 Medium:** 2 tasks
- **Total Tasks:** 9 tasks

**Quick Reference Commands:**
```bash
# Check for notification code
grep -r "email\|sms\|webhook\|notification" . --include="*.py"

# Check for notification providers
grep -r "sendgrid\|twilio\|mailgun\|smtp" . --include="*.py"

# Test notifications
python -c "from infra.notifications import *"

# Test application startup
uvicorn main:app --reload
```

This backlog captures all the notification consolidation work with paranoid-level detail to avoid the painful lessons learned from the SmartSync refactoring.
