from bs4 import BeautifulSoup
import re
import csv

def extract_partner_data(html_content):
    """
    Extract partner data from Ramp partners HTML page content.
    
    Args:
        html_content (str): The full HTML content of the page containing partner cards.
    
    Returns:
        list[dict]: A list of dictionaries, each containing:
            - 'url': Full or relative URL to partner page
            - 'ramp_level': The tier (e.g., 'Platinum')
            - 'partner_name': Name of the partner firm
            - 'description': Description text
            - 'num_stars': Number of stars (float, e.g., 5.0; None if not present)
            - 'num_reviews': Number of reviews (int, e.g., 0; None if not present)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all partner card anchors (<a> elements with data-test-service-partner-card attribute)
    partner_cards = soup.find_all('a', attrs={'data-test-service-partner-card': ''})
    
    partners = []
    
    for card in partner_cards:
        # Extract URL from href
        url = card.get('href', '').strip()
        if url and not url.startswith('http'):
            url = 'https://accountants.ramp.com' + url  # Assuming base URL
        
        # Extract Ramp level from the tier div
        tier_div = card.find('div', {'data-test-tier-name': ''})
        ramp_level = tier_div.get_text(strip=True) if tier_div else None
        
        # Extract partner name
        name_h2 = card.find('h2', {'data-test-partner-name': True})
        partner_name = name_h2.get_text(strip=True) if name_h2 else None
        
        # Extract description
        desc_div = card.find('div', {'data-test-partner-description': True})
        description = desc_div.get_text(strip=True) if desc_div else None
        
        # Extract reviews section (contains both stars and review count)
        reviews_section = card.find('div', {'data-test-partner-reviews': ''})
        num_stars = None
        num_reviews = None
        
        if reviews_section:
            # Extract star rating from span with class "text-text font-semibold" (e.g., "5.0")
            stars_span = reviews_section.find('span', class_='text-text font-semibold')
            if stars_span:
                try:
                    num_stars = float(stars_span.get_text(strip=True))
                except (ValueError, AttributeError):
                    num_stars = None
            
            # Extract number of reviews from span like "(0)", "(2)", or "(8)"
            reviews_span = reviews_section.find('span', class_='text-text-subtle')
            if reviews_span:
                reviews_match = re.search(r'\((\d+)\)', reviews_span.get_text(strip=True))
                num_reviews = int(reviews_match.group(1)) if reviews_match else None
        
        if partner_name:  # Only add if we have a name
            partners.append({
                'url': url,
                'ramp_level': ramp_level,
                'partner_name': partner_name,
                'description': description,
                'num_stars': num_stars,
                'num_reviews': num_reviews
            })
    
    return partners

if __name__ == "__main__":
    import os
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define file paths - look for HTML file in script directory first, then current working directory
    html_file = os.path.join(script_dir, 'ramp_partner_table.html')
    if not os.path.exists(html_file):
        # Try current working directory (when run with poetry run from project root)
        html_file = 'ramp_partner_table.html'
    
    # CSV file goes in the same directory as the script
    csv_file = os.path.join(script_dir, 'ramp_partners.csv')
    
    # Check if HTML file exists
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        print("Make sure ramp_partner_table.html is in the same directory as this script.")
        exit(1)
    
    # Read HTML content
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        exit(1)
    
    # Extract partner data
    partners = extract_partner_data(html_content)
    print(f"Found {len(partners)} partners")

    if partners:
        # Write to CSV
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['partner_name', 'ramp_level', 'num_stars', 'num_reviews', 'description', 'url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for p in partners:
                    writer.writerow(p)
            
            print(f"✓ Wrote {len(partners)} partners to {csv_file}")
            
            # Also print to console for quick view
            print("\nFirst 5 partners:")
            for p in partners[:5]:
                print(f"  - {p['partner_name']} ({p['ramp_level']}) - {p['num_stars']} stars")
        except Exception as e:
            print(f"Error writing CSV file: {e}")
    else:
        print("⚠ No partners found. Check HTML structure.")