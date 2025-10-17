import pandas as pd

# Categorized keywords for better analysis
TECH_KEYWORDS = ['saas', 'technology', 'software', 'startup', 'tech', 'early-stage', 'high-growth', 'scaling', 'innovation', 'digital', 'cloud', 'platform']
QBO_KEYWORDS = ['quickbooks', 'qbo', 'xero', 'cloud accounting', 'intuit', 'automation', 'integration', 'api', 'workflow']
SERVICE_KEYWORDS = ['fractional', 'controller', 'cfo', 'outsourced', 'virtual accounting', 'bookkeeping', 'financial analysis', 'monthly close', 'real-time', 'reporting', 'advisory']
BUSINESS_KEYWORDS = ['subscription', 'recurring', 'b2b', 'enterprise', 'smb', 'small business', 'medium business']

# Additional service type detection
TAX_KEYWORDS = ['tax', 'taxes', 'taxation', 'irs', 'tax return', 'tax filing', 'tax planning', 'tax compliance', 'tax credit', 'tax advisory']
FULL_SERVICE_KEYWORDS = ['full service', 'comprehensive', 'complete', 'end-to-end', 'all-in-one', 'one-stop', 'full-service']
AUDIT_KEYWORDS = ['audit', 'auditing', 'audited', 'auditor', 'audit support', 'audit preparation']
PAYROLL_KEYWORDS = ['payroll', 'payroll services', 'payroll processing', 'payroll administration', 'payroll management']

TIER_BONUS = {'platinum': 2, 'gold': 1, 'silver': 0.5}

def extract_ramp_firm_attributes(description, ramp_level):
    """Extract structured attributes from Ramp firm description."""
    desc = str(description or '').lower()
    tier = str(ramp_level or '').lower()
    
    # Find matching keywords in each category
    tech_matches = [kw for kw in TECH_KEYWORDS if kw in desc]
    qbo_matches = [kw for kw in QBO_KEYWORDS if kw in desc]
    service_matches = [kw for kw in SERVICE_KEYWORDS if kw in desc]
    business_matches = [kw for kw in BUSINESS_KEYWORDS if kw in desc]
    tax_matches = [kw for kw in TAX_KEYWORDS if kw in desc]
    full_service_matches = [kw for kw in FULL_SERVICE_KEYWORDS if kw in desc]
    audit_matches = [kw for kw in AUDIT_KEYWORDS if kw in desc]
    payroll_matches = [kw for kw in PAYROLL_KEYWORDS if kw in desc]
    
    # Calculate normalized scores (per 100 words to avoid length bias)
    word_count = len(desc.split())
    normalization_factor = max(1, word_count / 100)  # Avoid division by zero
    
    tech_score = len(tech_matches) / normalization_factor
    qbo_score = len(qbo_matches) / normalization_factor
    service_score = len(service_matches) / normalization_factor
    business_score = len(business_matches) / normalization_factor
    tax_score = len(tax_matches) / normalization_factor
    full_service_score = len(full_service_matches) / normalization_factor
    audit_score = len(audit_matches) / normalization_factor
    payroll_score = len(payroll_matches) / normalization_factor
    
    # Tier bonus
    tier_score = TIER_BONUS.get('platinum' if 'platinum' in tier else 'gold' if 'gold' in tier else 'silver' if 'silver' in tier else 'none', 0)
    
    # Total fit score (normalized)
    total_score = tech_score + qbo_score + service_score + business_score + tier_score
    
    # Extract specific focus areas
    focus_areas = []
    if 'saas' in desc or 'software' in desc:
        focus_areas.append('SaaS/Software')
    if 'startup' in desc or 'early-stage' in desc:
        focus_areas.append('Startups')
    if 'technology' in desc or 'tech' in desc:
        focus_areas.append('Technology')
    if 'high-growth' in desc or 'scaling' in desc:
        focus_areas.append('High-Growth')
    if 'nonprofit' in desc or 'non-profit' in desc:
        focus_areas.append('Nonprofit')
    
    # Extract service types
    service_types = []
    if 'fractional cfo' in desc or 'fractional controller' in desc:
        service_types.append('Fractional CFO/Controller')
    if 'outsourced accounting' in desc or 'virtual accounting' in desc:
        service_types.append('Outsourced Accounting')
    if 'controller' in desc:
        service_types.append('Controller Services')
    if 'cfo' in desc:
        service_types.append('CFO Services')
    if 'bookkeeping' in desc:
        service_types.append('Bookkeeping')
    if 'financial analysis' in desc:
        service_types.append('Financial Analysis')
    
    # Extract specialized services
    specialized_services = []
    if tax_matches:
        specialized_services.append('Tax Services')
    if full_service_matches:
        specialized_services.append('Full Service')
    if audit_matches:
        specialized_services.append('Audit Services')
    if payroll_matches:
        specialized_services.append('Payroll Services')
    
    # Extract tech stack expertise
    tech_stack = []
    if 'quickbooks' in desc or 'qbo' in desc:
        tech_stack.append('QuickBooks')
    if 'xero' in desc:
        tech_stack.append('Xero')
    if 'cloud accounting' in desc:
        tech_stack.append('Cloud Accounting')
    
    # Client focus detection
    client_focus = []
    if 'startup' in desc or 'startups' in desc:
        client_focus.append('Startups')
    if 'venture' in desc or 'vc' in desc or 'venture capital' in desc:
        client_focus.append('VC-backed')
    if 'nonprofit' in desc or 'non-profit' in desc:
        client_focus.append('Nonprofits')
    if 'small business' in desc or 'smb' in desc:
        client_focus.append('SMB')
    
    return {
        'fit_score': round(total_score, 2),
        'tech_score': round(tech_score, 2),
        'qbo_score': round(qbo_score, 2),
        'service_score': round(service_score, 2),
        'business_score': round(business_score, 2),
        'tax_score': round(tax_score, 2),
        'full_service_score': round(full_service_score, 2),
        'audit_score': round(audit_score, 2),
        'payroll_score': round(payroll_score, 2),
        'tier_score': tier_score,
        'focus_areas': '; '.join(focus_areas) if focus_areas else '',
        'service_types': '; '.join(service_types) if service_types else '',
        'specialized_services': '; '.join(specialized_services) if specialized_services else '',
        'tech_stack': '; '.join(tech_stack) if tech_stack else '',
        'client_focus': '; '.join(client_focus) if client_focus else '',
        'word_count': word_count,
        'tech_keywords': ', '.join(tech_matches) if tech_matches else '',
        'qbo_keywords': ', '.join(qbo_matches) if qbo_matches else '',
        'service_keywords': ', '.join(service_matches) if service_matches else '',
        'tax_keywords': ', '.join(tax_matches) if tax_matches else '',
        'has_tax_services': len(tax_matches) > 0,
        'has_full_service': len(full_service_matches) > 0,
        'has_audit_services': len(audit_matches) > 0,
        'has_payroll_services': len(payroll_matches) > 0
    }

def analyze_ramp_partners_data(csv_file):
    """Analyze Ramp partners and add structured fields."""
    try:
        df = pd.read_csv(csv_file)

        # Extract all attributes for each partner
        attributes = []
        for _, row in df.iterrows():
            attrs = extract_ramp_firm_attributes(row.get('description'), row.get('ramp_level'))
            attributes.append(attrs)
        
        # Add all new columns
        for key in attributes[0].keys():
            df[key] = [attr[key] for attr in attributes]

        # write back in-place
        df.to_csv(csv_file, index=False)

        # Show top partners by fit_score
        top = df.nlargest(5, 'fit_score')[['partner_name', 'ramp_level', 'fit_score', 'focus_areas', 'service_types', 'specialized_services']]
        print(f"Added structured analysis to {len(df)} Ramp partners")
        print("Top 5 by fit_score:")
        for _, row in top.iterrows():
            print(f"- {row['partner_name']}: {row['fit_score']} ({row['focus_areas']}) - {row['specialized_services']}")

        # Show service type breakdown
        print("\nService Type Summary:")
        print(f"  Tax Services: {df['has_tax_services'].sum()}")
        print(f"  Full Service: {df['has_full_service'].sum()}")
        print(f"  Audit Services: {df['has_audit_services'].sum()}")
        print(f"  Payroll Services: {df['has_payroll_services'].sum()}")

    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Run the scraper first.")
    except Exception as e:
        print(f"Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_ramp_partners_data('ramp_partners.csv')