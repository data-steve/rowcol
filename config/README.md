# Business Rules Architecture

## **🎯 Purpose**
Centralize business logic parameters while maintaining clear ownership and preventing both bloat and buried magic numbers.

## **🏗️ Structure**

```
config/business_rules/
├── README.md                    # This file - architecture explanation
├── __init__.py                  # Exports all rule classes
├── core_thresholds.py          # Core system thresholds (runway, data quality)
├── collections_rules.py        # AR collections business logic
├── payment_rules.py            # AP payment business logic
├── risk_assessment_rules.py    # Customer & vendor risk scoring
└── communication_rules.py      # Email frequency, contact preferences
```

## **📋 Principles**

### **1. Domain-Specific Rule Files**
- Each domain gets its own rules file
- Clear ownership and maintenance responsibility
- Easier to find and update related rules

### **2. Documented Business Logic**
- Every threshold must have business justification
- Industry standards referenced where applicable  
- Product reasoning clearly explained

### **3. Configurable by Business**
- Rules that vary by business size/industry marked as `TODO: Make configurable`
- Clear path to per-tenant customization

### **4. Version Controlled**
- All business rule changes tracked in git
- Breaking changes require migration strategies

## **🚨 Critical Requirements**

### **Documentation Standards**
```python
class CollectionsRules:
    # ✅ GOOD: Documented with business reasoning
    PAYMENT_RELIABILITY_EXCELLENT = 95  # Industry standard: 95%+ payment rate = excellent credit
    
    # ❌ BAD: Magic number without context
    SOME_THRESHOLD = 42
```

### **Industry Standards**
- Reference industry benchmarks where possible
- Document when we deviate and why
- Provide sources for standards used

### **Configurability Path**
- Mark rules that should be configurable per business
- Provide migration path for customization
- Document impact of changes
