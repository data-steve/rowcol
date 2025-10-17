from bs4 import BeautifulSoup
import csv

def extract_bill_partner_data(html_content):
    """
    Extract partner data from Bill partners HTML page content.

    Args:
        html_content (str): The full HTML content of the page containing partner cards.

    Returns:
        list[dict]: A list of dictionaries, each containing:
            - 'url': Full or relative URL to partner page
            - 'tier_level': The tier (e.g., 'Platinum Partner')
            - 'partner_name': Name of the partner firm
            - 'description': Description text
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all partner card anchors (<a> elements with data-test-service-partner-card attribute)
    # Try both empty string and True for the attribute value
    partner_cards = soup.find_all('a', attrs={'data-test-service-partner-card': ''})
    if not partner_cards:
        partner_cards = soup.find_all('a', attrs={'data-test-service-partner-card': True})

    partners = []

    for card in partner_cards:
        # Extract URL from href
        url = card.get('href', '').strip()
        if url and not url.startswith('http'):
            url = 'https://accountants.bill.com' + url  # Assuming base URL

        # Extract tier level from the tier div
        tier_div = card.find('div', {'data-test-tier-name': ''})
        if not tier_div:
            tier_div = card.find('div', {'data-test-tier-name': True})
        tier_level = tier_div.get_text(strip=True) if tier_div else None

        # Extract partner name
        name_h2 = card.find('h2', {'data-test-partner-name': ''})
        partner_name = name_h2.get_text(strip=True) if name_h2 else None

        # Extract description
        desc_div = card.find('div', {'data-test-partner-description': ''})
        description = desc_div.get_text(strip=True) if desc_div else None

        if partner_name:  # Only add if we have a name
            partners.append({
                'url': url,
                'tier_level': tier_level,
                'partner_name': partner_name,
                'description': description
            })

    return partners

if __name__ == "__main__":
    import os
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define file paths - look for HTML file in script directory first, then current working directory
    html_file = os.path.join(script_dir, 'bill_partner_table.html')
    if not os.path.exists(html_file):
        # Try current working directory (when run with poetry run from project root)
        html_file = 'bill_partner_table.html'
    
    # CSV file goes in the same directory as the script
    csv_file = os.path.join(script_dir, 'bill_partners.csv')
    
    # Check if HTML file exists
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        print("Make sure bill_partner_table.html is in the same directory as this script.")
        exit(1)
    
    # Read HTML content
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        exit(1)
    
    # Extract partner data
    partners = extract_bill_partner_data(html_content)
    print(f"Found {len(partners)} partners")

    if partners:
        # Write to CSV
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['partner_name', 'tier_level', 'description', 'url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for p in partners:
                    writer.writerow(p)

            print(f"✓ Wrote {len(partners)} partners to {csv_file}")

            # Also print to console for quick view
            print("\nFirst 5 partners:")
            for p in partners[:5]:
                print(f"  - {p['partner_name']} ({p['tier_level']})")
                print(f"    {p['description'][:100]}..." if p['description'] and len(p['description']) > 100 else f"    {p['description']}")
                print()
        except Exception as e:
            print(f"Error writing CSV file: {e}")
    else:
        print("⚠ No partners found. Check HTML structure.")
