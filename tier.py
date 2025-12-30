import csv
import re

# Read movies.csv to create a mapping of IMDB ID to movie tier
movie_tier_map = {}
with open('movies.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        imdb_id = row.get('Imdb_Id', '').strip()
        tier_str = row.get('Movie Tier (Indie/Mainstream/Blockbuster)', '').strip()
        
        if imdb_id and tier_str:
            # Extract just the tier name (Mainstream, Indie, or Blockbuster)
            # The format is like "Mainstream (Price 50,000)" or "Indie (Price 25,000)" or "Blockbuster (Price 100,000)"
            tier_match = re.search(r'^(Mainstream|Indie|Blockbuster)', tier_str, re.IGNORECASE)
            if tier_match:
                tier = tier_match.group(1).capitalize()
                # Normalize to match expected format
                if tier.lower() == 'blockbuster':
                    tier = 'Blockbuster'
                elif tier.lower() == 'mainstream':
                    tier = 'Mainstream'
                elif tier.lower() == 'indie':
                    tier = 'Indie'
                movie_tier_map[imdb_id] = tier

# Function to get production cost based on tier
def get_production_cost(tier):
    tier_lower = tier.lower() if tier else ''
    if tier_lower == 'indie':
        return 5000000
    elif tier_lower == 'mainstream':
        return 50000000
    elif tier_lower == 'blockbuster':
        return 150000000
    return 0

# Function to get movie price based on tier
def get_movie_price(tier):
    tier_lower = tier.lower() if tier else ''
    if tier_lower == 'indie':
        return 25000
    elif tier_lower == 'mainstream':
        return 50000
    elif tier_lower == 'blockbuster':
        return 100000
    return 0

# Function to get price based on tier and rank
def get_price(tier, rank):
    if not rank or not tier:
        return 0
    
    try:
        rank = int(rank)
    except (ValueError, TypeError):
        return 0
    
    tier_lower = tier.lower() if tier else ''
    
    if tier_lower == 'indie':
        if 1 <= rank <= 5:
            return 5000
        elif 6 <= rank <= 10:
            return 2500
        elif 11 <= rank <= 15:
            return 1000
    elif tier_lower == 'mainstream':
        if 1 <= rank <= 5:
            return 15000
        elif 6 <= rank <= 10:
            return 10000
        elif 11 <= rank <= 15:
            return 5000
    elif tier_lower == 'blockbuster':
        if 1 <= rank <= 5:
            return 25000
        elif 6 <= rank <= 10:
            return 15000
        elif 11 <= rank <= 15:
            return 5000
    
    return 0

# Read reordered_output.csv and process it
rows = []
current_movie_tier = None
current_movie_production_cost = None

with open('reordered_output.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    
    for row in reader:
        row_type = row.get('Type', '').strip()
        imdb_id = row.get('Imdb id', '').strip()
        
        # If this is a Movie row, get the tier and production cost
        if row_type == 'Movie' and imdb_id:
            if imdb_id in movie_tier_map:
                current_movie_tier = movie_tier_map[imdb_id]
                current_movie_production_cost = get_production_cost(current_movie_tier)
            else:
                current_movie_tier = None
                current_movie_production_cost = None
        
        # Update Movie Tier column
        if row_type == 'Movie' and current_movie_tier:
            row['Movie Tier'] = current_movie_tier
        elif row_type in ['Director', 'Actor'] and current_movie_tier:
            # Directors and Actors don't have Movie Tier, but we keep it empty
            pass
        
        # Update Production Cost column
        if row_type == 'Movie' and current_movie_production_cost is not None:
            row['Production Cost'] = current_movie_production_cost
        
        # Update Price column for Movies based on tier
        if row_type == 'Movie' and current_movie_tier:
            movie_price = get_movie_price(current_movie_tier)
            row['Price'] = movie_price
        
        # Update Price column for Actors based on rank
        if row_type == 'Actor':
            rank = row.get('Rank', '').strip()
            if rank and current_movie_tier:
                price = get_price(current_movie_tier, rank)
                row['Price'] = price
        
        # Update Price column for Directors (same as rank 1-5)
        if row_type == 'Director' and current_movie_tier:
            price = get_price(current_movie_tier, 1)  # Use rank 1 price (same as 1-5)
            row['Price'] = price
        
        rows.append(row)

# Write the output to a new CSV file
output_filename = 'tier_output.csv'
with open(output_filename, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Processing complete! Output written to {output_filename}")
print(f"Processed {len(rows)} rows")
print(f"Found {len(movie_tier_map)} movies with tier information")

