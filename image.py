import csv
import requests
from bs4 import BeautifulSoup
import time

def get_imdb_image_url(imdb_id, entity_type):
    """
    Fetches the image URL from an IMDb page.
    
    Args:
        imdb_id: The IMDb ID (e.g., 'tt10329560' or 'nm2946516')
        entity_type: 'Movie', 'Actor', or 'Director'
    
    Returns:
        The image URL string, or empty string if not found
    """
    # Construct the URL based on entity type
    if entity_type == 'Movie':
        url = f"https://www.imdb.com/title/{imdb_id}/"
    else:  # Actor or Director
        url = f"https://www.imdb.com/name/{imdb_id}/"
    
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # First, try to get image from Open Graph meta tag (most reliable)
        meta_img = soup.find('meta', property='og:image')
        if meta_img and meta_img.get('content'):
            image_url = meta_img.get('content')
            # Convert to high-res version if it's a thumbnail
            if '_V1_' in image_url and '_V1_FMjpg_UX1000_' not in image_url:
                # Replace with high-res version
                image_url = image_url.split('._V1_')[0] + '._V1_FMjpg_UX1000_.jpg'
            return image_url
        
        # For movies, look for poster image in various locations
        if entity_type == 'Movie':
            # Try poster container
            poster_div = soup.find('div', class_='ipc-media')
            if poster_div:
                img = poster_div.find('img')
                if img:
                    image_url = img.get('src') or img.get('data-src')
                    if image_url:
                        return process_image_url(image_url)
            
            # Try alternative poster selectors
            for selector in ['img.ipc-image', 'div.poster img', 'a.ipc-lockup-overlay img']:
                img = soup.select_one(selector)
                if img:
                    image_url = img.get('src') or img.get('data-src')
                    if image_url:
                        return process_image_url(image_url)
        else:
            # For actors/directors, look for headshot
            # Try name photo widget
            photo_div = soup.find('div', class_='name-overview-widget__photo')
            if photo_div:
                img = photo_div.find('img')
                if img:
                    image_url = img.get('src') or img.get('data-src')
                    if image_url:
                        return process_image_url(image_url)
            
            # Try alternative selectors for actor/director photos
            for selector in ['div.photo img', 'img.headshot', 'div.name-overview-widget img']:
                img = soup.select_one(selector)
                if img:
                    image_url = img.get('src') or img.get('data-src')
                    if image_url:
                        return process_image_url(image_url)
        
        return ''
    
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ''
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return ''

def process_image_url(image_url):
    """
    Processes an image URL to get the high-resolution version.
    """
    if not image_url:
        return ''
    
    # If it's already a high-res URL, return as is
    if '_V1_FMjpg_UX1000_' in image_url:
        return image_url
    
    # Convert thumbnail to high-res
    if '_V1_' in image_url:
        # Extract base URL and convert to high-res format
        base_url = image_url.split('._V1_')[0]
        # Remove any existing extension and add the high-res format
        if '.' in base_url:
            base_url = base_url.rsplit('.', 1)[0]
        return f"{base_url}._V1_FMjpg_UX1000_.jpg"
    
    return image_url

def process_csv(input_file, output_file):
    """
    Reads the CSV file, adds image URLs, and saves to output file.
    """
    rows = []
    
    # Read the CSV file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Handle case where fieldnames is None (empty CSV or no header)
        if fieldnames is None:
            print("Error: CSV file appears to be empty or has no header row.")
            return
        
        # Add 'image' column if it doesn't exist
        if 'image' not in fieldnames:
            fieldnames = list(fieldnames) + ['image']
        
        for row in reader:
            imdb_id = row.get('Imdb id', '').strip()
            entity_type = row.get('Type', '').strip()
            
            if imdb_id:
                print(f"Fetching image for {entity_type}: {row.get('Name', 'Unknown')} ({imdb_id})...")
                image_url = get_imdb_image_url(imdb_id, entity_type)
                row['image'] = image_url
                print(f"  Found: {image_url[:80]}..." if image_url else "  Not found")
                
                # Be polite to IMDb - add a small delay
                time.sleep(1)
            else:
                row['image'] = ''
            
            rows.append(row)
    
    # Write the updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nProcessed {len(rows)} rows. Output saved to {output_file}")

if __name__ == "__main__":
    input_file = "tier_output.csv"
    output_file = "test.csv"  # Overwrite the input file, or change to a different name
    
    process_csv(input_file, output_file)

