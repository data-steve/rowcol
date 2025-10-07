# Production Readiness Checklist

**Version**: 1.0  
**Date**: 2025-10-01  
**Purpose**: Complete production deployment checklist extracted from V5 build plan  
**Status**: Required before deploying Phase 1 to real advisors

---

## Overview

This checklist ensures the RowCol platform is production-ready with real integrations, scalable infrastructure, security hardening, and operational monitoring. Complete these tasks after Phase 1 MVP is built and before deploying to paying advisors.

**Estimated Total Effort**: 140 hours (~3.5 weeks)

---

## Stage 1: Security & Secrets Management (8h)

### **Rotate All Keys & Secrets** ⚠️ **CRITICAL**
- [ ] **Rotate all API keys/secrets** (LLM has seen .env file) *Effort: 2h*
- [ ] **Move refresh tokens to database** (currently in local files) *Effort: 3h*
- [ ] **Implement secrets manager** (AWS Secrets Manager, HashiCorp Vault) *Effort: 3h*

### **Audit Logging Coverage**
- [ ] **Confirm audit logging strategy** *Effort: 4h*
- [ ] **Review all state-mutating service methods** for correct audit logging *Effort: 4h*

---

## Stage 2: Production Database & Infrastructure (30h)

### **Database Migration**
- [ ] **PostgreSQL setup and configuration** *Effort: 4h*
- [ ] **Alembic migration system implementation** *Effort: 6h*
- [ ] **Database connection pooling and optimization** *Effort: 4h*
- [ ] **Backup and recovery strategy** *Effort: 3h*

### **Infrastructure as Code**
- [ ] **Docker containerization** (Dockerfile + docker-compose) *Effort: 6h*
- [ ] **Environment configuration management** *Effort: 4h*
- [ ] **Health checks and monitoring setup** *Effort: 3h*

---

## Stage 3: Real External Integrations (47h)

### **QBO Integration Validation** ⚠️ **CRITICAL PRODUCT VALIDATION**
- [ ] **Validate QBO API supports "single approval → multiple actions" workflow** (bill approval + payment scheduling + AR reminders) *Effort: 6h*
- [ ] **Test QBO webhook reliability** and real-time sync accuracy for runway calculations *Effort: 4h*
- [ ] **Verify vendor normalization needs** and data quality issues in real QBO data *Effort: 4h*
- [ ] **Load test QBO API rate limits** and error handling under production volumes *Effort: 4h*

### **QBO Production Integration**
- [ ] **Replace mocked QBOIntegrationService** with real QBO API calls *Effort: 8h*
- [ ] **QBO OAuth flow implementation** and token management *Effort: 6h*
- [ ] **Rate limiting, error handling, and retry logic** *Effort: 4h*
- [ ] **QBO webhook handling** for real-time updates *Effort: 3h*

### **Email Production Setup**
- [ ] **SendGrid production account** and domain verification *Effort: 2h*
- [ ] **AWS SES setup** as fallback provider *Effort: 2h*
- [ ] **Email delivery tracking** and bounce handling *Effort: 4h*

---

## Stage 4: CI/CD & Deployment Pipeline (25h)

### **CI/CD Implementation**
- [ ] **GitHub Actions workflow** for testing and deployment *Effort: 8h*
- [ ] **Automated testing pipeline** with coverage reporting *Effort: 6h*
- [ ] **Security scanning** and dependency updates *Effort: 4h*

### **Cloud Deployment**
- [ ] **AWS/GCP/Azure deployment configuration** *Effort: 4h*
- [ ] **Load balancer and SSL certificate setup** *Effort: 3h*

---

## Stage 5: Monitoring & Observability (20h)

### **Application Performance Monitoring (APM)**
- [ ] **APM integration** (New Relic, DataDog, or equivalent) *Effort: 4h*
- [ ] **Centralized logging** with structured logs *Effort: 4h*
- [ ] **Error tracking and alerting system** (Sentry or equivalent) *Effort: 4h*

### **Operational Monitoring**
- [ ] **Health check endpoints** for load balancer integration *Effort: 2h*
- [ ] **Metrics dashboard** for operational monitoring *Effort: 3h*
- [ ] **Alert escalation procedures** *Effort: 3h*

---

## Stage 6: Security Hardening (30h)

### **Application Security**
- [ ] **Security headers and HTTPS enforcement** *Effort: 3h*
- [ ] **API rate limiting and DDoS protection** *Effort: 3h*
- [ ] **Secrets management and environment security** *Effort: 2h*
- [ ] **Security scanning** (OWASP, Snyk, or equivalent) *Effort: 4h*

### **API Safety & HTTP Edge Cases** ⚠️ **CRITICAL API VALIDATION**
- [ ] **Range Header Handling** - Verify APIs properly handle Range headers to prevent resource exhaustion *Effort: 2h*
- [ ] **Content-Type Enforcement** - Strict enforcement of Content-Type headers to avoid parser vulnerabilities *Effort: 2h*
- [ ] **Accept Header Negotiation** - Validate proper content type negotiation and fallback behavior *Effort: 2h*
- [ ] **Method Not Allowed Responses** - Ensure 405 responses include Allow header with supported methods *Effort: 1h*
- [ ] **Compression Configuration** - Review compression settings to prevent encoding-related issues *Effort: 2h*
- [ ] **Character Encoding** - Verify consistent UTF-8 encoding specification and handling *Effort: 2h*
- [ ] **Path Traversal Protection** - Test and validate protection against directory traversal attacks *Effort: 3h*
- [ ] **Request Size Limits** - Implement and test request size limits to prevent memory exhaustion *Effort: 2h*
- [ ] **Transfer-Encoding Handling** - Review Transfer-Encoding header handling to prevent request smuggling *Effort: 2h*

---

## Stage 7: Performance & Scalability (10h)

### **Performance Optimization**
- [ ] **Database query optimization and indexing** *Effort: 4h*
- [ ] **API response caching with Redis** *Effort: 3h*
- [ ] **Background job processing** for digest sending *Effort: 3h*

---

## Stage 8: Data Management (10h)

### **Data Quality & Migration**
- [ ] **Data Generator Consolidation**: Audit all mock data providers (`create_sandbox_data.py`, `scenario_runner.py`, `conftest.py` fixtures, QBO client mock data) and consolidate into unified, realistic data generation system *Effort: 6h*
- [ ] **Database migration utilities** and rollback procedures *Effort: 4h*

---

## Success Criteria

### **Production Readiness**
- ✅ Application runs with **99.9% uptime**
- ✅ Real QBO data flows correctly with **<2s API response times**
- ✅ Email delivery rate **>95%** with proper tracking
- ✅ Automated deployments work reliably
- ✅ Comprehensive monitoring and alerting in place

### **Security & Compliance**
- ✅ Zero critical vulnerabilities in security scanning
- ✅ All secrets managed via secrets manager (not .env files)
- ✅ API rate limiting prevents abuse
- ✅ Audit trail captures all state changes

### **Performance**
- ✅ Dashboard loads **<2s** for 50 clients
- ✅ QBO API calls with retry logic handle rate limits
- ✅ Background jobs process without blocking UI
- ✅ Database queries optimized with proper indexing

### **Operational Excellence**
- ✅ Health checks report accurate system state
- ✅ Alerts trigger on critical issues (not noise)
- ✅ Error tracking captures and reports issues
- ✅ Centralized logging enables debugging

---

## Notes

### **When to Complete This**
- **After Phase 1 MVP is built** (4 weeks)
- **Before deploying to paying advisors**
- Can be done in parallel with Phase 2 feature development

### **References**
- V5 Build Plan: `docs/archive/build_plan_v5.md` (Phase 6)
- Infrastructure docs: `infrastructure_consolidation_plan.md`
- QBO integration: `infra/qbo/README.md`

---

**End of Production Readiness Checklist**

