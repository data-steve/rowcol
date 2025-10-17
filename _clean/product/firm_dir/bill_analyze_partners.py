import pandas as pd

# Categorized keywords for better analysis
TECH_KEYWORDS = ['saas', 'technology', 'software', 'startup', 'tech', 'early-stage', 'high-growth', 'scaling', 'innovation', 'digital', 'cloud', 'platform']
QBO_KEYWORDS = ['quickbooks', 'qbo', 'xero', 'cloud accounting', 'intuit', 'automation', 'integration', 'api', 'workflow']
SERVICE_KEYWORDS = ['fractional', 'controller', 'cfo', 'outsourced', 'virtual accounting', 'bookkeeping', 'financial analysis', 'monthly close', 'real-time', 'reporting', 'advisory']
BUSINESS_KEYWORDS = ['subscription', 'recurring', 'b2b', 'enterprise', 'smb', 'small business', 'medium business']

TIER_BONUS = {'platinum': 2, 'gold': 1}

def extract_firm_attributes(description, tier_level):
    """Extract structured attributes from firm description."""
    desc = str(description or '').lower()
    tier = str(tier_level or '').lower()
    
    # Find matching keywords in each category
    tech_matches = [kw for kw in TECH_KEYWORDS if kw in desc]
    qbo_matches = [kw for kw in QBO_KEYWORDS if kw in desc]
    service_matches = [kw for kw in SERVICE_KEYWORDS if kw in desc]
    business_matches = [kw for kw in BUSINESS_KEYWORDS if kw in desc]
    
    # Calculate normalized scores (per 100 words to avoid length bias)
    word_count = len(desc.split())
    normalization_factor = max(1, word_count / 100)  # Avoid division by zero
    
    tech_score = len(tech_matches) / normalization_factor
    qbo_score = len(qbo_matches) / normalization_factor
    service_score = len(service_matches) / normalization_factor
    business_score = len(business_matches) / normalization_factor
    
    # Tier bonus
    tier_score = TIER_BONUS.get('platinum' if 'platinum' in tier else 'gold' if 'gold' in tier else 'none', 0)
    
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
    
    # Extract tech stack expertise
    tech_stack = []
    if 'quickbooks' in desc or 'qbo' in desc:
        tech_stack.append('QuickBooks')
    if 'xero' in desc:
        tech_stack.append('Xero')
    if 'cloud accounting' in desc:
        tech_stack.append('Cloud Accounting')
    
    return {
        'fit_score': round(total_score, 2),
        'tech_score': round(tech_score, 2),
        'qbo_score': round(qbo_score, 2),
        'service_score': round(service_score, 2),
        'business_score': round(business_score, 2),
        'tier_score': tier_score,
        'focus_areas': '; '.join(focus_areas) if focus_areas else '',
        'service_types': '; '.join(service_types) if service_types else '',
        'tech_stack': '; '.join(tech_stack) if tech_stack else '',
        'word_count': word_count,
        'tech_keywords': ', '.join(tech_matches) if tech_matches else '',
        'qbo_keywords': ', '.join(qbo_matches) if qbo_matches else '',
        'service_keywords': ', '.join(service_matches) if service_matches else ''
    }

def analyze_bill_partners_data(csv_file):
    """Analyze Bill partners and add structured fields."""
    try:
        df = pd.read_csv(csv_file)

        # Extract all attributes for each partner
        attributes = []
        for _, row in df.iterrows():
            attrs = extract_firm_attributes(row.get('description'), row.get('tier_level'))
            attributes.append(attrs)
        
        # Add all new columns
        for key in attributes[0].keys():
            df[key] = [attr[key] for attr in attributes]

        # write back in-place
        df.to_csv(csv_file, index=False)

        # Show top partners by fit_score
        top = df.nlargest(5, 'fit_score')[['partner_name', 'tier_level', 'fit_score', 'focus_areas', 'service_types']]
        print(f"Added structured analysis to {len(df)} partners")
        print("Top 5 by fit_score:")
        for _, row in top.iterrows():
            print(f"- {row['partner_name']}: {row['fit_score']} ({row['focus_areas']})")

    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Run the scraper first.")
    except Exception as e:
        print(f"Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_bill_partners_data('bill_partners.csv')
