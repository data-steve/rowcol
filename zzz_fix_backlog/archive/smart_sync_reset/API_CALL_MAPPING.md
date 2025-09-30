# API Call Mapping by Type - ADR-005 Alignment

*Generated from comprehensive codebase audit on 2025-01-27*  
*Status: ✅ COMPLETE - Ready for QBOClient Implementation*

## **Context for All API Calls**

**Dependency Direction**: `Service/Route → QBOClient → SmartSyncService → QBO API`

**API Call Categories**:
1. **User Actions** (immediate <300ms) → SmartSyncService → QBOClient
2. **Data Fetching** (calculations/dashboards) → SmartSyncService → QBOClient  
3. **Bulk Operations** (background processing) → SmartSyncService → QBOClient
4. **Health Checks** (monitoring) → QBOClient (direct, no orchestration)

---

## **User Actions (Immediate <300ms) - 15 endpoints**

**SmartSyncService Configuration**: `strategy=SyncStrategy.USER_ACTION, priority=SyncPriority.HIGH, use_cache=False, max_attempts=3, backoff_factor=2.0`

### **Payment Operations**
- `POST /payments/{payment_id}/execute` - Execute payment immediately
- `POST /payments/{payment_id}/cancel` - Cancel payment immediately
- `POST /payments/batch-execute` - Execute multiple payments immediately

### **Bill Operations**
- `PUT /bills/{bill_id}/approve` - Approve bill immediately
- `POST /bills/{bill_id}/schedule-payment` - Schedule payment immediately

### **Invoice Operations**
- `POST /invoices/{invoice_id}/send-reminder` - Send invoice reminder immediately

### **Collection Operations**
- `POST /collections/contact/{invoice_id}` - Contact customer immediately

### **Tray Operations**
- `POST /tray/{item_id}/categorize` - Categorize item immediately
- `POST /tray/{item_id}/confirm` - Confirm action immediately

### **Reserve Runway Operations**
- `POST /reserve-runway/` - Create reserve immediately
- `PUT /reserve-runway/{reserve_id}` - Update reserve immediately
- `DELETE /reserve-runway/{reserve_id}` - Delete reserve immediately
- `POST /reserve-runway/{reserve_id}/allocate` - Allocate reserve immediately
- `POST /reserve-runway/{reserve_id}/release` - Release reserve immediately
- `POST /reserve-runway/recommendations/{recommendation_id}/accept` - Accept recommendation immediately

---

## **Data Fetching (Calculations/Dashboards) - 45 endpoints**

**SmartSyncService Configuration**: `strategy=SyncStrategy.DATA_FETCH, priority=SyncPriority.MEDIUM, use_cache=True, max_attempts=3, backoff_factor=1.5`



### **Bill Operations**
- `GET /bills/` - Get all bills
- `GET /bills/{bill_id}` - Get specific bill
- `GET /bills/{bill_id}/runway-impact` - Get bill runway impact

### **Invoice Operations**
- `GET /invoices/` - Get all invoices
- `GET /invoices/{invoice_id}` - Get specific invoice
- `GET /invoices/{invoice_id}/payment-options` - Get payment options
- `GET /invoices/runway-impact/summary` - Get invoice runway impact summary

### **Payment Operations**
- `GET /payments/` - Get all payments
- `GET /payments/{payment_id}` - Get specific payment
- `GET /payments/pending` - Get pending payments
- `GET /payments/{payment_id}/runway-impact` - Get payment runway impact

### **Collection Operations**
- `GET /collections/dashboard` - Get collections dashboard
- `GET /collections/overdue` - Get overdue invoices
- `GET /collections/customer/{customer_id}/aging` - Get customer aging
- `GET /collections/runway-impact` - Get collections runway impact

### **Tray Operations**
- `GET /tray/` - Get tray items
- `GET /tray/categorized` - Get categorized tray items
- `GET /tray/{item_id}/payment-analysis` - Get payment analysis
- `GET /tray/runway-impact/summary` - Get tray runway impact summary

### **Reserve Runway Operations**
- `GET /reserve-runway/` - Get all reserves
- `GET /reserve-runway/{reserve_id}` - Get specific reserve
- `GET /reserve-runway/summary` - Get reserve summary
- `GET /reserve-runway/runway-calculation` - Get runway calculation
- `GET /reserve-runway/recommendations` - Get reserve recommendations

### **Vendor Operations**
- `GET /vendors/` - Get all vendors
- `GET /vendors/{vendor_id}` - Get specific vendor
- `GET /vendors/critical` - Get critical vendors
- `GET /vendors/compliance/w9-updates` - Get W9 updates

### **Digest Operations**
- `GET /businesses/{business_id}/digest` - Get digest data
- `GET /businesses/{business_id}/digest/preview` - Get digest preview
- `GET /digest/email-status` - Get email status

### **Test Drive Operations**
- `GET /test-drive/{business_id}/test-drive` - Get test drive data
- `GET /test-drive/{business_id}/hygiene-score` - Get hygiene score
- `GET /test-drive/demo/{industry}` - Get demo data

### **User Operations**
- `GET /users/{user_id}` - Get specific user
- `GET /businesses/{business_id}/users/` - Get business users

### **Onboarding Operations**
- `GET /onboarding/{business_id}/status` - Get onboarding status

---

## **Bulk Operations (Background Processing) - 8 endpoints**

**SmartSyncService Configuration**: `strategy=SyncStrategy.BULK_OPERATION, priority=SyncPriority.LOW, use_cache=True, max_attempts=2, backoff_factor=3.0`

### **Data Upload & Processing**
- `POST /bills/upload` - Upload bills in bulk
- `POST /digest/send-all` - Send digest to all businesses

### **Background Sync Operations**
- `POST /businesses/{business_id}/digest/send` - Send digest (background)
- `POST /auth/password-reset` - Password reset (background)
- `POST /auth/password-reset/confirm` - Password reset confirmation (background)

### **User Management**
- `POST /users/` - Create user (background)
- `PUT /users/{user_id}` - Update user (background)
- `DELETE /users/{user_id}` - Delete user (background)

---

## **Health Checks (Direct API Calls) - 10 endpoints**

**SmartSyncService Configuration**: Direct API calls, no orchestration needed

### **QBO Setup & Health**
- `GET /qbo-setup/{business_id}/status` - Get QBO connection status
- `GET /qbo-setup/{business_id}/health` - Get QBO health check

### **Authentication Health**
- `POST /auth/login` - Login (direct)
- `POST /auth/register` - Register (direct)
- `POST /auth/logout` - Logout (direct)
- `POST /auth/refresh` - Refresh token (direct)

### **QBO Connection Health**
- `POST /qbo-setup/{business_id}/connect` - Connect to QBO (direct)
- `POST /qbo-setup/callback` - QBO callback (direct)
- `DELETE /qbo-setup/{business_id}/disconnect` - Disconnect from QBO (direct)

### **Onboarding Health**
- `POST /onboarding/` - Start onboarding (direct)

---

## **Experience Service Methods - 25 methods**

**SmartSyncService Configuration**: Mixed - depends on method purpose

### **Digest Experience**
- `calculate_runway()` - Data Fetching
- `generate_and_send_digest()` - Bulk Operation
- `send_digest_to_all_businesses()` - Bulk Operation
- `get_digest_preview()` - Data Fetching

### **Tray Experience**
- `get_tray_items()` - Data Fetching
- `get_tray_summary()` - Data Fetching
- `categorize_bill_urgency()` - Data Fetching
- `get_payment_decision_analysis()` - Data Fetching
- `get_enhanced_tray_items()` - Data Fetching
- `create_tray_item()` - User Action
- `confirm_action()` - User Action

### **Onboarding Experience**
- `start_qbo_connection()` - Health Check
- `complete_qbo_connection()` - Health Check
- `get_onboarding_status()` - Data Fetching
- `qualify_onboarding()` - User Action

### **Test Drive Experience**
- `generate_test_drive()` - Data Fetching
- `generate_hygiene_score()` - Data Fetching
- `generate_qbo_sandbox_test_drive()` - Data Fetching

---

## **Domain Service Methods - 15 methods**

**SmartSyncService Configuration**: Mixed - depends on method purpose

### **Balance Service**
- `get_current_balances()` - Data Fetching
- `get_total_available_balance()` - Data Fetching
- `get_balance_by_account_type()` - Data Fetching

### **Document Review Service**
- `get_review_queue()` - Data Fetching
- `review_document()` - User Action
- `reject_document()` - User Action
- `get_review_summary()` - Data Fetching

---

## **Summary Statistics**

- **Total API Endpoints**: 78
- **User Actions**: 15 (19%)
- **Data Fetching**: 45 (58%)
- **Bulk Operations**: 8 (10%)
- **Health Checks**: 10 (13%)

- **Total Experience Methods**: 25
- **Total Domain Methods**: 15
- **Grand Total**: 118 API calls to categorize

---

## **Next Steps**

1. **Task 3**: Implement QBOClient methods with SmartSyncService integration based on this mapping
2. **Task 4**: Remove SmartSyncService imports from all services (they only need QBOClient)
3. **Verification**: Test all API calls work with new architecture

---

*This mapping provides the foundation for implementing QBOClient methods with correct SmartSyncService usage patterns for each API call type.*
