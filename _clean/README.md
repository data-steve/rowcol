# RowCol Clean Architecture

*Strangler-Fig Recovery Documentation*

## **What This Is**

This is the **clean architecture documentation and MVP recovery plan** for RowCol. It contains:

- **Architecture**: Clean ADRs and comprehensive architecture docs
- **Product Strategy**: E2E vision and PRDs for Tray, Console, Digest
- **Recovery Plan**: Detailed migration manifest and stepped implementation plan
- **MVP Code**: QBO-only MVP with Smart Sync pattern

## **Folder Structure**

```
_clean/
├── architecture/          # Clean ADRs and architecture docs
├── e2e/                  # End-to-end product strategy
├── mvp/                  # QBO-only MVP code
├── product/              # PRDs for Tray, Console, Digest
├── strangled_fig/        # Migration manifest and stepped plan
├── .cursorrules          # Prevents contamination during recovery
└── pyproject.toml        # MVP dependencies
```

## **Key Documents**

### **Architecture**
- `architecture/comprehensive_architecture.md` - Complete architecture vision
- `architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `architecture/ADR-005-qbo-api-strategy.md` - QBO API strategy with Smart Sync
- `architecture/ADR-007-service-boundaries.md` - Service boundaries and patterns

### **Product Strategy**
- `e2e/product_strategy.md` - Complete e2e product vision
- `product/hygiene_tray_prd.md` - Hygiene Tray PRD (post-Ramp era)
- `product/digest_prd.md` - Digest PRD (advisor-first UI)
- `product/decision_console_prd.md` - Decision Console PRD (insights focus)

### **Recovery Plan**
- `mvp/recovery_build_plan.md` - Complete recovery strategy
- `strangled_fig/migration_manifest.md` - File-by-file porting instructions
- `strangled_fig/stepped_plan.md` - Detailed implementation roadmap

## **Running the Recovery Plan**

### **1. Start New Thread**
```bash
# Reference this README and recovery_build_plan.md
# Follow the stepped plan exactly
```

### **2. Follow Guards**
- `.cursorrules` - Only edit files in `_clean/`
- `scripts/ci_guard.sh` - CI blocks changes outside MVP lane
- No legacy code imports in runway

### **3. Execute Steps**
1. Bootstrap MVP structure
2. Copy QBO client and mappers
3. Create domain interfaces
4. Implement infra repos
5. Create sync orchestrator
6. Implement infra gateways
7. Wire runway services
8. Add tests and validate

## **Architecture Principles**

### **Dependency Direction**
```
runway/ → domains/ → infra/
```

### **Smart Sync Pattern**
- Transaction Log (append-only audit trail)
- State Mirror (fast local reads)
- Sync Orchestrator (centralized sync logic)
- Domain Gateways (rail-agnostic interfaces)

### **Progressive Hub Model**
- **MVP**: QBO-centric (QBO as ledger hub)
- **Future**: RowCol as operational hub, QBO as ledger hub

## **Status**

**Current Phase**: Documentation complete, ready for implementation
**Next Step**: Execute recovery plan in new thread
**Target**: QBO-only MVP with Smart Sync pattern

## **Success Criteria**

- [ ] QBO client connects to sandbox
- [ ] Domain gateways are defined
- [ ] Sync orchestrator implements Smart Sync pattern
- [ ] Runway services compose domain gateways
- [ ] All 5 tests pass
- [ ] No legacy code imports in runway

## **Notes**

- This is a **Strangler-Fig recovery** to eliminate architectural rot
- We're starting with QBO-only MVP to prove the architecture
- Multi-rail features will be added later using the same patterns
- All documentation is clean and aligned with current vision
