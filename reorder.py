import csv
from collections import defaultdict

# Read the ordered_data.csv file
input_file = 'ordered_data.csv'
output_file = 'reordered_output.csv'

# Group data by movie
movies_data = defaultdict(list)

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        movie_key = (row['movie_name'], row['movie_imdb_id'])
        movies_data[movie_key].append(row)

# Write to output file in standard.csv format
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # Write header
    writer.writerow(['Type', 'Active', 'Name', 'Imdb id', 'Movie Tier', 'Production Cost', 'Rank', 'Price'])
    
    # Process each movie
    movie_list = list(movies_data.items())
    for idx, ((movie_name, movie_imdb_id), actors) in enumerate(movie_list):
        # Write movie row
        writer.writerow(['Movie', 'TRUE', movie_name, movie_imdb_id, 'Mainstream', '0', '', '0'])
        
        # Write actor rows
        for actor in actors:
            writer.writerow([
                'Actor',
                'TRUE',
                actor['actor_name'],
                actor['actor_imdb_id'],
                '',  # Movie Tier (blank for actors)
                '',   # Production Cost (blank for actors)
                actor['rank'],
                '0'   # Price
            ])
        
        # Add blank line between movies (except after the last one)
        if idx < len(movie_list) - 1:
            writer.writerow(['', '', '', '', '', '', '', ''])

print(f"Successfully converted {input_file} to {output_file}")
print(f"Processed {len(movies_data)} movies")


