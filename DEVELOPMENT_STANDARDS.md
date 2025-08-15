# Development Standards & Anti-Patterns

*Based on Stage 0-1C implementation experience - critical for avoiding common pitfalls*

## Quick Reference
- [Development Plan](dev_plan.md)
- [Architecture Requirements](docs/Architecture_Requirements_Changes_Updated.markdown)

## 🚫 **CRITICAL ANTI-PATTERNS TO AVOID**

### **File Naming & Import Chaos**
- ❌ **Don't:** Use folder names as prefixes in filenames (`models_service.py`, `routes_engagement.py`)
- ❌ **Don't:** Bulk rename files without updating ALL imports across the codebase
- ❌ **Don't:** Assume imports will "just work" after file moves
- ✅ **Do:** Use descriptive, unique filenames (`service.py`, `engagement.py`)
- ✅ **Do:** Update imports systematically after any file reorganization

### **Schema vs. Model Confusion**
- ❌ **Don't:** Use SQLAlchemy models as `response_model` in FastAPI routes
- ❌ **Don't:** Mix Pydantic schemas and SQLAlchemy models in API responses
- ❌ **Don't:** Assume `from_attributes = True` fixes all serialization issues
- ✅ **Do:** Create separate Pydantic schemas (`*Base`, `*Create`, full models)
- ✅ **Do:** Use Pydantic schemas for `response_model`, SQLAlchemy models for database operations
- ✅ **Do:** Alias SQLAlchemy models in routes: `from models import Service as ServiceModel`

### **Database Schema Mismatches**
- ❌ **Don't:** Create seed data that doesn't match your SQLAlchemy models
- ❌ **Don't:** Assume database columns exist without checking the actual model definitions
- ❌ **Don't:** Use hardcoded field names that don't match the database schema
- ✅ **Do:** Ensure seed data exactly matches your model definitions
- ✅ **Do:** Use consistent field names across models, schemas, and seed data
- ✅ **Do:** Test database seeding before building frontend features

### **Missing Required Fields**
- ❌ **Don't:** Forget to add required fields like `firm_id` when implementing multi-tenancy
- ❌ **Don't:** Create models that inherit from mixins but don't implement required fields
- ❌ **Don't:** Assume optional fields are truly optional without checking business logic
- ✅ **Do:** Explicitly add all required fields when implementing new features
- ✅ **Do:** Use database constraints to enforce required fields
- ✅ **Do:** Validate that seed data includes all required fields

### **Route Registration & Import Issues**
- ❌ **Don't:** Assume all routes will register automatically after adding them to `routes/__init__.py`
- ❌ **Don't:** Import non-existent modules in `routes/__init__.py` (causes circular imports)
- ❌ **Don't:** Forget to include new routers in the consolidated router
- ✅ **Do:** Test route registration after any changes to the consolidated router
- ✅ **Do:** Verify all imported modules exist before adding them to routes
- ✅ **Do:** Use minimal working examples to isolate routing issues

### **Seed Data & Business Logic Integration**
- ❌ **Don't:** Hardcode business logic responses in services
- ❌ **Don't:** Return mock data from services instead of querying the database
- ❌ **Don't:** Use static responses for dynamic business rules
- ✅ **Do:** Use seed data tables for configurable business rules
- ✅ **Do:** Query real data for compliance requirements, task templates, policy rules
- ✅ **Do:** Make business logic data-driven and configurable

### **Complex Dependencies in Templates**
- ❌ **Don't:** Load heavy third-party libraries (drag-and-drop, tour libraries) in basic templates
- ❌ **Don't:** Assume CDN libraries will load correctly or have the expected global variables
- ❌ **Don't:** Mix complex JavaScript with Jinja2 template syntax
- ✅ **Do:** Start with basic React components and add complexity incrementally
- ✅ **Do:** Test external library loading before building complex features
- ✅ **Do:** Use raw JavaScript blocks or escape Jinja2 syntax conflicts

### **Database Seeding Issues**
- ❌ **Don't:** Call seeding functions multiple times without checking if data already exists
- ❌ **Don't:** Use SQLAlchemy queries to check if tables exist before seeding
- ❌ **Don't:** Assume seeding will work after table creation without proper error handling
- ✅ **Do:** Use raw SQL to check table existence and data counts
- ✅ **Do:** Implement proper error handling in seeding functions
- ✅ **Do:** Test seeding with fresh databases

## ✅ **GOOD PATTERNS TO REPLICATE**

### **Systematic Problem Solving**
- ✅ **Do:** Fix one issue at a time, test, then move to the next
- ✅ **Do:** Use error messages to guide fixes rather than guessing
- ✅ **Do:** Test APIs directly with `curl` before testing frontend
- ✅ **Do:** Check server logs for detailed error information
- ✅ **Do:** Use minimal working examples to isolate complex issues

### **Incremental Template Development**
- ✅ **Do:** Start with simple templates that just display data
- ✅ **Do:** Add interactive features only after basic functionality works
- ✅ **Do:** Use console logging to debug frontend data flow
- ✅ **Do:** Test templates in isolation before integrating with complex features

### **Proper Test Structure**
- ✅ **Do:** Use fixtures for reusable test data
- ✅ **Do:** Mock external API calls to prevent test hangs
- ✅ **Do:** Test database operations with proper setup/teardown
- ✅ **Do:** Use descriptive test names and organize tests logically
- ✅ **Do:** Centralize common mocks (like QBO) in `conftest.py`

### **Multi-Tenant Architecture**
- ✅ **Do:** Implement `TenantMixin` consistently across all models
- ✅ **Do:** Add `firm_id` filtering to all list endpoints
- ✅ **Do:** Use proper foreign key relationships with explicit constraints
- ✅ **Do:** Test tenant isolation thoroughly
- ✅ **Do:** Always include `firm_id` in domain objects

### **Code Organization**
- ✅ **Do:** Use consolidated routers in `routes/__init__.py` to keep `main.py` clean
- ✅ **Do:** Separate concerns: models (data), schemas (validation), services (logic), routes (API)
- ✅ **Do:** Use consistent naming conventions across all layers
- ✅ **Do:** Implement proper error handling with HTTP status codes

## 🔧 **IMPLEMENTATION CHECKLIST**

### **Before Starting New Feature**
- [ ] Check existing models and schemas for consistency
- [ ] Verify database schema matches model definitions
- [ ] Ensure seed data exists for business logic
- [ ] Plan multi-tenant implementation (`firm_id`, `client_id`)

### **During Development**
- [ ] Test route registration after adding new endpoints
- [ ] Verify imports work without circular dependencies
- [ ] Test database operations with real data
- [ ] Ensure proper error handling and status codes

### **Before Committing**
- [ ] Run full test suite: `poetry run pytest tests/ -q --disable-warnings`
- [ ] Verify all routes are accessible (no 404s)
- [ ] Check that seed data loads correctly
- [ ] Ensure multi-tenant isolation works

## 📚 **COMMON COMMANDS**

```bash
# Database setup
python create_tables.py
python load_seed_data.py

# Testing
poetry run pytest tests/ -q --disable-warnings
poetry run pytest tests/test_specific.py -v

# Route verification
poetry run python -c "from routes.specific import router; print(len(router.routes))"

# App startup test
poetry run python -c "from main import app; print('✅ App imports successfully')"
```

## 🚨 **TROUBLESHOOTING**

### **Route Registration Issues**
1. Check `routes/__init__.py` for missing imports
2. Verify all imported modules exist
3. Test minimal route creation
4. Check for circular imports

### **Database Issues**
1. Recreate tables: `python create_tables.py`
2. Reload seed data: `python load_seed_data.py`
3. Check model field names match database
4. Verify foreign key relationships

### **Import Errors**
1. Check file paths and naming
2. Verify `__init__.py` files exist
3. Test imports individually
4. Look for circular dependencies

---

*Last updated: Stage 1C completion*
*Next review: After Stage 1D implementation*
