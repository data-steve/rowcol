# Bookkeeping 101: Training Guide for Junior Bookkeepers

## Introduction
As an L6 overseeing BookClose operations, my goal is to equip you, our junior bookkeeper, with the skills to handle the bookkeeping cycle accurately and efficiently. This guide walks you through the essential steps of bookkeeping, from setting up accounts to closing the books, with practical tips and best practices. We’ll use QuickBooks Online (QBO) as the primary tool for examples, as it’s widely used by small-to-mid-size businesses. By the end, you’ll understand the full process and how our BookClose platform supercharges these tasks with automation. Let’s dive in!

## Step-by-Step Bookkeeping Guide
This guide follows the bookkeeping cycle, aligned with best practices from NACPB and QuickBooks training resources. Each step includes tasks, tools, and tips to ensure accuracy and audit-readiness.[](https://www.nacpb.org/learn-bookkeeping)[](https://www.freebookkeepingaccounting.com/free-quickbooks-online-course)[](https://www.nacpb.org/category/bookkeeping-education)

### Step 1: Set Up the Company File
- **Task**: Create or verify the company file in QBO to ensure accurate financial tracking.
- **Actions**:
  - Enter company details (name, address, EIN, fiscal year).
  - Set up the Chart of Accounts (COA) with standard accounts (e.g., Cash, Accounts Receivable, Sales, COGS, Expenses).
  - Configure settings: currency (USD default), tax settings (if applicable), and bank feed connections.
- **Tools**: QBO (Settings > Company Settings, Chart of Accounts).
- **Tips**:
  - Double-check COA for industry-specific accounts (e.g., Inventory for e-commerce, WIP for construction).
  - Avoid duplicate accounts (e.g., multiple “Office Supplies”).
  - Save a backup of the initial setup.
- **Time**: 2-4 hours for new clients, 1 hour for reviews.

### Step 2: Connect Bank and Credit Card Feeds
- **Task**: Link bank and credit card accounts to QBO for automated transaction imports.
- **Actions**:
  - Navigate to QBO Banking > Connect Account; use Plaid for secure connections.
  - Verify account details (bank name, account type, last 4 digits).
  - Set sync range (12-18 months for historical data).
- **Tools**: QBO Banking, Plaid.
- **Tips**:
  - Confirm with the client which accounts to connect (e.g., operating, payroll, credit cards).
  - Watch for duplicate feeds or closed accounts.
  - Check for bank feed lags (transactions may take 1-3 days to appear).
- **Time**: 1-2 hours.

### Step 3: Categorize Transactions
- **Task**: Assign transactions to COA accounts to reflect accurate financials.
- **Actions**:
  - Review bank feed transactions in QBO (Banking > For Review).
  - Match transactions to existing records (e.g., invoices, bills) or categorize manually (e.g., “AMZN” to Office Supplies).
  - Use QBO’s bank rules for recurring transactions (e.g., “STRIPE PAYOUT” to Sales Income).
  - Flag uncategorized or unclear transactions for client clarification.
- **Tools**: QBO Banking, Rules.
- **Tips**:
  - Prioritize high-value transactions (> $1000) for accuracy.
  - Use memos to note assumptions (e.g., “Assumed Uber = Travel”).
  - Review vendor names for consistency (e.g., “Amazon” vs. “AMZN Mktplace”).
- **Time**: 4-8 hours/month for 200 transactions.

### Step 4: Manage Accounts Payable (AP)
- **Task**: Record and pay vendor bills to track expenses and liabilities.
- **Actions**:
  - Enter bills in QBO (Expenses > Bills) from vendor emails or PDFs.
  - Code bills to COA (e.g., utilities to Utility Expense).
  - Schedule payments via QBO or Melio (mark as paid in QBO).
  - Reconcile vendor statements monthly to catch discrepancies.
- **Tools**: QBO Expenses, Melio.
- **Tips**:
  - Verify bill due dates and terms (e.g., Net 30).
  - Flag missing bills for client follow-up (PBC requests).
  - Watch for duplicate bills or incorrect amounts.
- **Time**: 3-6 hours/month for 50 bills.

### Step 5: Manage Accounts Receivable (AR)
- **Task**: Create invoices, track payments, and follow up on overdue accounts.
- **Actions**:
  - Create invoices in QBO (Sales > Invoices) from client orders or POS data.
  - Record customer payments (Sales > Receive Payment).
  - Send reminders for overdue invoices (Sales > Customers > Overdue).
  - Issue credit memos for returns or disputes.
- **Tools**: QBO Sales, Customer Statements.
- **Tips**:
  - Customize invoice templates with client branding.
  - Track AR aging weekly (e.g., over 30/60/90 days).
  - Confirm payment matches invoice amount before applying.
- **Time**: 2-4 hours/month for 30 invoices.

### Step 6: Reconcile Bank and Credit Card Accounts
- **Task**: Ensure QBO balances match bank/credit card statements.
- **Actions**:
  - Run reconciliation in QBO (Accounting > Reconcile).
  - Compare QBO ending balance to statement balance.
  - Resolve discrepancies (e.g., missing transactions, incorrect categorizations).
  - Mark as reconciled (✓ tickmark) and save statements as evidence.
- **Tools**: QBO Reconcile, Bank Statements.
- **Tips**:
  - Start with the oldest unreconciled period.
  - Check for bank fees or interest not yet recorded.
  - Document unresolved differences with memos.
- **Time**: 2-4 hours/month per account.

### Step 7: Record Payroll and Liabilities
- **Task**: Post payroll journals and track tax/benefit remittances.
- **Actions**:
  - Import payroll data from Gusto or QBO Payroll.
  - Post journal entries (DR Wages Expense, CR Cash/Payroll Liabilities).
  - Track remittance payments (e.g., payroll taxes, 401(k)).
  - Verify payroll adjustments (e.g., bonuses, garnishments).
- **Tools**: QBO Payroll, Gusto.
- **Tips**:
  - Confirm payroll totals with provider reports.
  - Separate gross wages, taxes, and benefits in JEs.
  - Flag missing payroll data for PBC requests.
- **Time**: 2-3 hours/month.

### Step 8: Manage Inventory (if applicable)
- **Task**: Track inventory receipts, sales, and adjustments.
- **Actions**:
  - Set up items in QBO (Products and Services).
  - Record inventory purchases (DR Inventory, CR AP or Cash).
  - Adjust inventory for sales or spoilage (DR COGS, CR Inventory).
  - Perform spot counts for high-value items.
- **Tools**: QBO Inventory, POS exports.
- **Tips**:
  - Use QBO’s inventory tracking for simple setups.
  - Reconcile inventory monthly with physical counts.
  - Document adjustments with evidence (e.g., count sheets).
- **Time**: 2-3 hours/month for inventory clients.

### Step 9: Pre-Close Review
- **Task**: Ensure completeness before closing the books.
- **Actions**:
  - Run completeness checks: all bank/CC accounts reconciled, AP/AR tied to GL, payroll posted.
  - Request PBC items (bank statements, payroll reports, inventory counts).
  - Flag exceptions (e.g., unreconciled transactions, missing docs).
  - Calculate close readiness score: % reconciled, % PBC received, exceptions resolved.
- **Tools**: QBO Reports (Trial Balance, GL Detail), Email/Portal for PBC.
- **Tips**:
  - Prioritize critical PBCs (e.g., bank statements).
  - Use a checklist to track progress.
  - Escalate missing items to the client by D-1.
- **Time**: 2-4 hours/month.

### Step 10: Month-End Close
- **Task**: Finalize financials with adjustments and approvals.
- **Actions**:
  - Post adjusting JEs (e.g., accruals: payroll, utilities; prepaids: insurance, SaaS).
  - Run tie-outs: AR/AP aging vs. GL, BS vs. Trial Balance.
  - Generate AP/AR snapshots for aging trends.
  - Draft close summary narrative (e.g., “AR over 90 days increased 10% due to Client X delays”).
  - Submit for firm approval; incorporate reviewer notes.
- **Tools**: QBO Journal Entries, Reports.
- **Tips**:
  - Use standard JE templates for consistency.
  - Explain variances >10% or $2500 with tickmarks (Δ=JE, A=accrual, P=prepaid).
  - Save all supporting documents (Evidence Locker).
- **Time**: 4-6 hours/month.

### Step 11: Generate Financial Reports and Binders
- **Task**: Produce audit-ready reports and binders.
- **Actions**:
  - Run reports: Balance Sheet, Income Statement, Cash Flow.
  - Compile working binder (Excel): cover, index, tickmark legend, BS/IS, JEs, narrative, AP/AR snapshots.
  - Export final binder (PDF) with SHA-256 hash for auditability.
  - Deliver to firm by D+5.
- **Tools**: QBO Reports, Excel, PDF exporter.
- **Tips**:
  - Use tickmarks consistently (✓=reconciled, T=tie-out, V=variance).
  - Include management commentary for key trends (e.g., margin compression).
  - Verify binder completeness before delivery.
- **Time**: 2-3 hours/month.

### Step 12: Continuous Improvement
- **Task**: Refine processes based on feedback and errors.
- **Actions**:
  - Log reviewer notes and post-close adjustments.
  - Update QBO bank rules or COA mappings based on corrections.
  - Track KPIs: % transactions categorized, review time, error rate.
- **Tools**: QBO Rules, Excel for KPI tracking.
- **Tips**:
  - Meet weekly with the L6 to review pain points.
  - Propose new rules for recurring issues (e.g., “SYSCO” → COGS:Food).
  - Document lessons learned for future closes.
- **Time**: 1-2 hours/month.

## Best Practices
- **Accuracy**: Double-check high-value transactions and reconciliations.
- **Consistency**: Use standardized COA, tickmarks, and memos across clients.
- **Communication**: Escalate unclear transactions or missing PBCs promptly.
- **Audit-Readiness**: Save all evidence (statements, invoices) and link to transactions.
- **Efficiency**: Prioritize tasks by materiality (e.g., focus on $1000+ transactions first).

## Training Resources
- **QuickBooks Online Tutorials**: Free courses for setup, banking, and reports (e.g., www.freebookkeepingaccounting.com).[](https://www.freebookkeepingaccounting.com/free-quickbooks-online-course)
- **NACPB Bookkeeping Certification**: Covers accounting principles, payroll, and QBO (13 weeks, $369-$449).[](https://www.nacpb.org/learn-bookkeeping)[](https://keeper.app/blog/best-online-bookkeeping-certificate-programs/)
- **Intuit Academy**: Beginner-friendly QBO training (2 months, ~$160).[](https://keeper.app/blog/best-online-bookkeeping-certificate-programs/)
- **Udemy QBO Course**: Comprehensive guide for navigating QBO and bookkeeping tasks.[](https://opencourser.com/course/uoq3iu/mastering-quickbooks-online-2025-a-comprehensive-guide)
- **Practice**: Use QBO sandbox to simulate client workflows (ask L6 for access).

## Expected Ramp
- **Month 1**: Master QBO basics, categorize 50% of transactions manually, reconcile 1-2 accounts.
- **Month 2**: Automate 50-60% of categorizations with rules, complete full close cycle with supervision.
- **Month 3**: Handle 80% of close tasks independently, propose rule improvements.

