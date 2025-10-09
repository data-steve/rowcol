# Smart Sync Pattern Specification

*The architecture pattern that should connect domain services, data orchestrators, transaction logs, and state mirror tables*

## **The Intended Smart Sync Pattern**

### **What Should Happen**
```
Domain Service → QBOSyncService → Smart Decision → DB (if fresh) OR API (if stale)
```

### **The Smart Switching Logic**
1. **Domain Service** calls `QBOSyncService.get_bills_by_due_days()`
2. **QBOSyncService** checks if local data is fresh enough
3. **If fresh**: Return data from local DB (fast)
4. **If stale**: Call QBO API, update local DB, return fresh data
5. **Transaction Log**: Record all data changes for audit trail

## **What's Actually Happening (Broken)**

### **Current Reality**
```
BillService.get_bills_due_in_days() → Direct DB Query (bypasses QBOSyncService)
QBOSyncService.get_bills_by_due_days() → Direct API Call (no smart switching)
```

### **The Disconnect**
- **Domain services** do their own database queries
- **QBOSyncService** just does raw API calls
- **No smart switching** between DB and API
- **No connection** between domain services and sync service
- **Transaction logs** not integrated with the switching logic

## **The Complete Architecture That Should Exist**

### **Layer 1: Domain Services (Business Logic)**
```python
class BillService:
    def get_bills_due_in_days(self, days: int = 30):
        # Should call QBOSyncService, not direct DB query
        return await self.qbo_sync.get_bills_by_due_days(days)
```

### **Layer 2: Smart Sync Service (Infrastructure)**
```python
class QBOSyncService:
    async def get_bills_by_due_days(self, days: int = 30):
        # Check if local data is fresh enough
        if self.is_data_fresh("bills", days):
            return self.get_from_local_db("bills", days)
        else:
            # Call API, update local DB, log transaction
            api_data = await self.qbo_client.get_bills_from_qbo(days)
            self.update_local_db(api_data)
            self.log_transaction("bills_sync", api_data)
            return api_data
```

### **Layer 3: Data Orchestrators (Runway)**
```python
class DigestDataOrchestrator:
    async def get_digest_data(self, business_id: str):
        # Should call domain services, not QBOSyncService directly
        bill_service = BillService(self.db, business_id)
        bills = await bill_service.get_bills_due_in_days(30)
        return {"bills": bills}
```

## **The Missing Connections**

### **1. Domain Services → QBOSyncService**
- **Current**: Domain services bypass QBOSyncService
- **Should be**: Domain services call QBOSyncService for all data needs

### **2. Smart Switching Logic**
- **Current**: QBOSyncService just calls API
- **Should be**: Check DB freshness, switch between DB and API

### **3. Transaction Log Integration**
- **Current**: Transaction logs separate from sync logic
- **Should be**: Every data change logged automatically

### **4. Data Orchestrators → Domain Services**
- **Current**: Data orchestrators call QBOSyncService directly
- **Should be**: Data orchestrators call domain services

## **The Complete Data Flow That Should Exist**

### **Read Operations (Smart)**
```
User Request → Runway Service → Data Orchestrator → Domain Service → QBOSyncService → Smart Decision → DB/API
```

### **Sync Operations (Background)**
```
Background Job → QBOSyncService → QBO API → Local DB Update → Transaction Log
```

### **Transaction Log Integration**
```
Every Data Change → Transaction Log Service → Immutable Audit Trail
```

## **Why This Pattern Is Important**

### **Performance**
- Fast responses using cached data when possible
- Live data when accuracy is critical
- Automatic optimization without domain service complexity

### **Data Consistency**
- Single source of truth for data freshness decisions
- Automatic sync when data becomes stale
- Transaction logs for complete audit trail

### **Architecture Clarity**
- Domain services focus on business logic
- QBOSyncService handles all data access decisions
- Clear separation of concerns

## **What's Been Missing All Day**

The user has been trying to articulate this pattern, but the AI assistant has:
1. **Claimed it was working** when it clearly wasn't
2. **Made false architectural claims** about circular dependencies
3. **Suggested wrong solutions** that made the problem worse
4. **Not actually read the code** to see the disconnection
5. **Wasted time** on non-existent problems instead of fixing the real issue

## **The Real Fix Needed**

1. **Connect domain services to QBOSyncService** - Make them call the sync service instead of direct DB queries
2. **Implement smart switching** - Add DB freshness checks and API fallback
3. **Integrate transaction logs** - Log every data change automatically
4. **Fix data orchestrators** - Make them call domain services, not QBOSyncService directly

## **Conclusion**

The Smart Sync pattern is a sophisticated architecture that should provide:
- **Smart data access** (DB when fresh, API when stale)
- **Automatic sync** (background jobs keep data fresh)
- **Complete audit trail** (transaction logs for all changes)
- **Clean separation** (domain logic vs infrastructure concerns)

But it's currently broken because the pieces aren't connected. Domain services bypass the sync service, there's no smart switching, and the architecture isn't implemented as designed.

The user has been trying to explain this all day, but the AI assistant has been making false claims and not listening to the actual problems.

---

*This document represents the architecture that should exist but currently doesn't, despite claims to the contrary.*
