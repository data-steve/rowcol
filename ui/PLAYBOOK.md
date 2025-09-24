# Oodaloo UI/UX Playbook
## Complete Design System & Implementation Guide

---

## Design Principles & Audit Framework

Every UI element must answer three questions in order:

1. **Where am I?** (state) → concise, linear time indicator
2. **What changed?** (delta) → variance vs plan/last week  
3. **What do I do now?** (one primary action) → explicit runway delta from the action

### Design Constraints
- **Linear > circular** for time coverage visualization
- **Few big events > many small ones** (Top-N AR/AP + payroll)
- Always show **date** and **days** together ("Covered until Oct 6 (14 days)")
- **List Mode parity** for accessibility and mobile
- **One primary verb** per action with explicit runway delta

---

## 1. Design Tokens as Single Source of Truth

### Core Token Structure
Implement in `tailwind.config.js` and `globals.css`:

```css
:root {
  --brand: 222 89% 55%; /* Coral #FF6F61 */
  --bg: 210 20% 98%; /* Light gray #F5F7FA */
  --fg: 222 30% 12%; /* Navy #1A2634 */
  --muted: 222 12% 40%; /* Muted navy #5C6B7F */
  --success: 142 71% 45%; /* Green #34C759 */
  --warn: 40 89% 55%; /* Yellow #FFC107 */
  --danger: 0 89% 55%; /* Red #FF3B30 */
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 14px;
  --focus-ring: 0 0 0 3px hsl(var(--brand) / 0.3);
  --shadow-sm: 0 1px 2px hsl(0 0% 0% / 0.06);
  --shadow-md: 0 2px 8px hsl(0 0% 0% / 0.08);
  --shadow-lg: 0 8px 24px hsl(0 0% 0% / 0.12);
  --transition-fast: 120ms;
  --transition-slow: 240ms;
}

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}

:root[data-theme="dark"] {
  --bg: 222 30% 7%; /* Dark navy #121926 */
  --fg: 210 25% 96%; /* Light gray #F0F2F5 */
  --muted: 222 10% 70%; /* Light navy #A3B1C6 */
}
```

### A11y & Motion Tokens
- Semantic tokens for focus outline (`--focus-ring`)
- Elevation levels (`--shadow-sm/md/lg`) 
- Motion speeds (`--transition-fast/slow`)
- Motion-reduced variants must be respected (`prefers-reduced-motion`)

### Why It's Critical
Tokens ensure unified navy/coral aesthetic across Digest, Console, and Prep Tray while enabling theme switching and WCAG compliance for QBO App Store approval.

---

## 2. Product Primitives (Complete Component Library)

### Core Primitives

#### RunwayCoverageBar (Linear Time Indicator)
**REPLACES** circular RunwayMeter gauge
```tsx
Props: { 
  coveredUntil: Date, 
  days: number, 
  payrollDate?: Date, 
  atRisk?: boolean, 
  hint?: string 
}
```
- **Visual**: Horizontal bar from Today → Coverage End Date with colored segments
- **Annotations**: "Covered until **Oct 6** — **14 days**" + payroll badge
- **Why Better**: Linear time, accommodates dates, precise, small-space friendly

#### Runway Flowband (Signature Visualization)
```tsx
Props: { 
  events: Event[], 
  horizonWeeks: 2|3|4, 
  payrollMarkers: Date[], 
  onAction?: (evt, action) => void 
}
```
- **Scope**: 2–4 week horizon, top-N events only (8–12), payroll markers
- **Interaction**: Hover details, action pills with explicit "+X days" deltas
- **Guardrails**: Sparse & actionable—if it can't say "Do X → **+Y days**," it doesn't ship
- **List Mode**: Toggle renders same events as accessible cards with identical actions

#### PaymentTimeline (Per-Item Control)
```tsx
Props: { 
  dueDate: Date, 
  latestSafeDate: Date, 
  currentDate: Date, 
  amount: number, 
  onChange(date): void, 
  runwayDeltaFor(date): number 
}
```
- **Purpose**: Micro-timeline for single AP/AR item
- **Visual**: Slider showing due date, latest safe date, constrained movement
- **Interaction**: Handle tooltip shows "Oct 6 (latest safe) → **+3 days** runway"

#### VarianceChip (Storytelling Element)
```tsx
Props: { 
  deltaDays: number, 
  reason?: string, 
  severity: 'pos'|'neg',
  aggregatedCount?: number 
}
```
- **Integration**: Embedded in Flowband and Digest cards
- **Aggregation Rule**: Multiple micro-events → single message ("–7 days today from 4 events")
- **Action**: One-click CTA routes to relevant tray fix

#### PrepTrayList (Game Board Layout)
```tsx
Props: { 
  tasks: { 
    id: string, 
    severity: 'urgent'|'optional', 
    action: string,
    runwayDelta: number 
  }[] 
}
```
- **Columns**: Must Pay / Can Delay / Chasing
- **Cards**: Each previews runway delta and includes ExplainHint
- **Verbs**: Delay, Nudge, Approve (never generic "Update")

#### Additional Primitives
- **EarmarkBadge**: `{ amount: number, rule: string }` (Runway Reserve tags)
- **CollectionPlaybookCard**: `{ invoiceId: string, amount: number, reliability: 'reliable'|'slow'|'risky', nextAction: string }`
- **AgingBuckets**: `{ buckets: { days: number, amount: number }[] }` (AR/AP aging)
- **ExplainHint**: `{ text: string, icon?: 'info'|'risk' }` (inline "why this matters")
- **ListModeToggle**: `{ enabled: boolean }` (accessibility fallback)
- **DigestRecipientField**: `{ email: string }` (CC bookkeeper, no RBAC)

---

## 3. Signature Visualization Strategy

### Runway Flowband as Category Anchor
The Flowband is Oodaloo's unique visual signature:

**ASCII Concept:**
```
[Cash Runway Flowband]
$50k |=====[AR +$8k]=====[Payroll -$10k]===[AP -$5k]===| $43k
     |      ^ Client X      ^ 15th         ^ Rent     |
     |<-- 2 weeks -->|<-- 1 week -->|<-- 1 week -->|
     [Variance: -3 days vs. plan] [Protect: Delay AP]
```

**Why It Wins Over Competitors:**
- **Fathom Waterfall**: Explains past (reporting), Flowband focuses on future actions
- **Float Timeline**: Shows trajectory, Flowband adds interactive "what if" + variance
- **QBO Reports**: Static tables, Flowband is a decision surface

**Implementation Requirements:**
- Chart.js streamplot with coral/green/red segments (~15h)
- Animated transitions respecting reduced-motion
- Overlay payroll markers and variance chips
- Drag-and-drop AP/AR events for "What If" scenarios

---

## 4. Surface-Specific Design Decisions

### Digest (Email/In-App Card)
**Primary Goal**: Quick orientation and top action

1. **Runway Coverage Bar** (replaces circular gauge)
   - "Covered until **Oct 6** — **14 days**"
   - Payroll badge: "Payroll Oct 4: **OK**" / "**At risk**"
   - Primary CTA: "Open Console" + top fix preview

2. **Variance Chip** 
   - "**–3 days vs plan** (AR shortfall –$6k)"
   - Links to filtered tray view

3. **Top 3 Action Cards**
   - "Delay $5k Rent to Oct 6 → +3d"
   - "Nudge Client X on $8k → +2d (typical 47d payer)"

**NO-GOs**: Circular gauges, pie charts, dense heatmaps

### Console (Primary App Interface)
**Primary Goal**: Context + immediate action

1. **Runway Flowband** (main panel)
   - 2–4 week horizon, top-N events only
   - Action pills with inline "+X days" deltas
   - Variance chip in header filters to causes

2. **Prep Tray** (secondary panel)
   - Three lanes: Must Pay / Can Delay / Chasing
   - Each card shows runway delta preview
   - ExplainHint for context ("Vendor charges late fees after 10 days")

3. **PaymentTimeline** (per-item adjustment)
   - Appears in event popovers or tray detail
   - Constrained slider with safety boundaries
   - Real-time runway delta preview

**NO-GOs**: Circular gauges, waterfall as primary view, stacked areas with dozens of series

---

## 5. Variance Tracking Integration

### Elevation Strategy
Transform Drift Alerts into front-and-center storytelling:

- **Console**: Chip inside Flowband ("–3 days vs plan") → click filters tray
- **Digest**: "Expected AR: $25k, Actual: $19k → –3 days runway"
- **Aggregation**: >N events/day → single alert with inline breakdown
- **UI**: Neumorphic chip with coral highlight, animated number increment

### Implementation
- Compare actual AR/AP events to projections in `domains/forecasting/`
- Surface deltas in `digest.py` and console components
- Respect reduced-motion preferences
- **Effort**: ~15h (UI: 10h, backend tweaks: 5h)

---

## 6. Lightweight "What If" Mode

### Scope Constraints
- **Single overlay** only (base vs one scenario)
- **2–3 controls max**: delay bill, shift AR, toggle reserve
- **No multi-scenario sandboxing** at MVP

### Implementation
- Toggle in Cash Console duplicates base curve
- Sliders for AR/AP event adjustments
- Overlay shows delta ("+3 days if rent on Oct 6")
- Extend `ForecastingService` for scenario objects
- **Effort**: ~40h (backend: 20h, UI: 20h)

---

## 7. Brand Integration & Inspirations

### Visual Language
- **Linear + Gusto**: Two-pane layout (Flowband left, Prep Tray right), friendly microcopy
- **Stripe**: Sharp data visualization with navy/coral contrast
- **Mercury**: Neumorphic cards and dark mode for modern trust
- **Narrative-first copy**: "Protect 3 runway days by delaying rent to Oct 6"
- **Celebratory states**: "Payroll safe 🎉" for confidence building

### Brand Assets
- **Tagline**: "Oodaloo: Your Cash Flow Co-Pilot. Master Your Runway with QBO."
- **QBO App Store**: Screenshot of Flowband with coral payroll marker
- **Demo video**: Digest → Prep Tray → "Vacation Ready" confetti sequence

---

## 8. Onboarding & Trust Surfaces

### First-Run Experience
- **Runway Replay**: Show past 4 weeks + decisions they *would* have made
- **Narrative Hygiene Score**: "Fix these 3 items → **+2 runway days**"
- **Runway Checkup Email**: Auto-send immediate snapshot (shareable for CAS)

### Collaboration Lite
- **Digest CC Field**: Optional bookkeeper email → send identical digest
- **No RBAC**: Test multi-user fit without complex permissions

---

## 9. Component Stack & Development Guardrails

### Technology Foundation
- **React + Vite + Tailwind + shadcn/ui + Radix**
- **Chart.js** for Flowband and data visualization
- **Class-variance-authority (CVA)** for clean props-to-className mappings
- **Storybook** for component validation and visual regression testing

### Development Rules
```markdown
# Oodaloo UI Playbook Constraints
- Use tokens only (--brand, --bg, --fg, --muted, --success, --warn, --danger)
- Components: shadcn Button, Card, Dialog, Table, Toast + Oodaloo primitives
- Do: Use tokens, existing primitives, Storybook stories, a11y (ARIA labels, keyboard traps)
- Don't: Use inline colors, fork styles, skip stories, use circular gauges for time
- Patterns: Bento dashboard, two-pane layout, right-side drawers
- Accessibility: WCAG AA, focus rings, VoiceOver support, List Mode parity
- Copy tone: Narrative-first ("Do X → +Y days"), celebratory states
```

### Linting & Quality
- **Lint to ban raw hexes** in components; enforce token usage
- **Storybook tests** for keyboard nav & focus order on all interactive elements
- **Performance**: Flowband renders <300ms, ≤25 event pills
- **A11y**: Error-free keyboard traversal, AA contrast compliance

---

## 10. Success Metrics & Instrumentation

### Desirability Metrics
- ≥70% pilots mention Flowband positively in feedback
- App Store CTR uplift vs. standard KPI screenshot
- Qualitative feedback on "decision surface" vs. "reporting tool"

### Usefulness Metrics  
- ≥30% of AP/AR actions initiated from Flowband interactions
- ≥50% of digest variance chips clicked through to console
- Average time from variance alert to corrective action

### Quality Metrics
- Error-free keyboard traversal across all interactive elements
- No more than 1 alert/day average (due to aggregation)
- <300ms Flowband render time on typical data sets

---

## 11. Decision Matrix: Which Visualization Answers Which Question?

| User Question | Best Element | Why | Primary Action |
|---------------|--------------|-----|----------------|
| "Am I safe till payroll?" | **Runway Coverage Bar** | Linear time, exact date & days | "Open Console" / top fix |
| "What shifted since last week?" | **Variance Chip** | Delta-first, compact | "View causes" (filters tray) |
| "What should I do right now?" | **Action Cards / Tray lanes** | Verb-first list | "Delay / Nudge / Approve" |
| "What's the shape of next 2–4 weeks?" | **Flowband** | Context + event affordances | Inline action pills |
| "How far can I safely push this bill?" | **PaymentTimeline** | Constrained, per-item timeline | Confirm new date |
| "What if I delay X or AR slips?" | **Flowband overlay (What-If)** | Immediate delta feedback | Apply scenario |

---

## 12. Implementation Timeline Integration

### Phase 0: Foundation & Core Ritual (80h, Weeks 1–2)
- Resolve existing issues (14h)
- Set up tokens, shadcn/ui, Storybook (20h)
- Design Cash Console/Digest wireframes (20h)
- Prototype micro-interactions (10h)
- Accessibility audit (6h)
- **Drift → VarianceChip implementation** (10h)

### Phase 1: Smart AP & Core Enhancements (100h, Weeks 3–4)
- Implement Smart AP (50h)
- **Build Runway Flowband v1** (15h)
- **RunwayCoverageBar + PaymentTimeline** (15h)
- **Digest CC field + email plumbing** (5h)
- Onboarding checklist & tooltips (10h)
- Accessibility polish (5h)

### Phase 2: Smart AR & Firm Prep (100h, Weeks 5–6)
- Implement Smart AR (50h)
- CollectionPlaybookCard & AgingBuckets (15h)
- **Narrative Hygiene Score** (6h)
- **Runway Checkup Email** (6h)
- **List Mode parity for Flowband** (8h)
- Prototype "What If" UI (10h)
- **Runway Replay onboarding** (5h)

### Phase 2.5: Smart Budgets (60h, Week 7)
- Budget dashboard & variance alerts (20h)
- Vacation Readiness Score (15h)
- Beta testing and polish (15h)
- 3D icons and kinetic typography (10h)

### Phase 3: Smart Automation & "What If" (80h, Week 8)
- Automation rules (50h)
- **What-If scenario engine** (20h)
- Notifications polish + aggregation (10h)

### Phase 4: Analytics Pack (60h, Week 9)
- AR/AP aging heatmaps & forecasting widgets (50h)
- **Narrative waterfall** for Analytics Pack only (10h)

### Validation (20h, Week 10)
- Q4 2025 beta testing (5–10 agencies)
- CAS firm demos with **mock "Agency Inc." profile**
- Flowband engagement metrics collection
- Variance chip click-through analysis

---

## 13. Component Rename/Replace Actions

### Immediate Changes Required
- ✅ **Rename** `RunwayMeter` → `RunwayCoverageBar`; implement linear variant
- ✅ **Remove** circular gauge entirely from all surfaces
- ✅ **Add** coverage date + payroll risk badge to the bar
- ✅ **Enforce** Flowband sparsity (top-N events; List Mode parity)
- ✅ **Ensure** every action preview shows **+X days** runway delta
- ✅ **Keep** Waterfall strictly in Analytics Pack (not console/digest)
- ✅ **Write** Storybook stories asserting: linear date labeling, variance chip wording, one primary CTA per object

### Why Circular Gauge Fails
- **Implies** cyclic progress/percent complete vs. linear time coverage
- **Hides** the critical coverage date
- **Invites** misread of precision
- **Not compatible** with "coverage to payroll date" mental model
- **Runway Coverage Bar** communicates better in same footprint

---

## 14. Copy & Micro-interaction Standards

### Standardized Labels
- **Coverage**: "Covered until **Oct 6** — **14 days**"
- **Payroll Status**: "Payroll Oct 4: **OK**" / "**At risk**"
- **Variance**: "**–3 days vs plan** (AR shortfall –$6k)"
- **Event Details**: "$5,000 Rent — Due Sep 28 — Latest safe Oct 6 → **+3 days**"
- **Timeline Tooltips**: "Oct 6 (latest safe) → **+3 days** runway"

### Action Verbs
- **Primary**: Delay, Nudge, Approve, Send, Schedule
- **Never**: Update, Manage, Edit, Configure
- **Format**: "Delay $5k Rent to Oct 6 → **+3d**"

### Celebratory States
- **Success**: "Payroll safe 🎉", "Runway extended!", "Vacation ready!"
- **Progress**: "2 of 3 fixes complete", "Almost there!"
- **Encouragement**: "Great catch!", "Smart move!"

---

## Final Vision Statement

Oodaloo's UI/UX is a **runway-first decision surface** anchored by the **Runway Flowband**—kept **sparse, actionable, and explainable**—with variance chips, lightweight What-If capabilities, and **narrative-first onboarding** (Runway Replay + Hygiene Score + Runway Checkup). 

Collaboration stays **lite** (Digest CC) to test CAS distribution without complex RBAC. The **RunwayCoverageBar** replaces all circular gauges with linear time visualization. Tokens + primitives + Storybook + List Mode ensure development speed, visual coherence, and accessibility compliance.

Together, this positions Oodaloo as the new category: **"QBO's Weekly Cash Runway Ritual"** — a decision surface that answers "Where am I?", "What changed?", and "What do I do now?" in that exact order, every time.
