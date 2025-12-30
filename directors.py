import csv
from collections import defaultdict

# Read directors.csv to create a mapping from movie IMDB ID to directors
directors_map = defaultdict(list)
with open('directors.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        movie_imdb_id = row['movie_imdb_id']
        director_name = row['director_name']
        director_imdb_id = row['director_imdb_id']
        directors_map[movie_imdb_id].append({
            'name': director_name,
            'imdb_id': director_imdb_id
        })

# Read reordered_output.csv and process it
output_rows = []
with open('reordered_output.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    output_rows.append(header)
    
    for row in reader:
        output_rows.append(row)
        
        # If this is a movie row, add director(s) below it
        if row[0] == 'Movie' and len(row) > 3:
            movie_imdb_id = row[3]  # IMDB id is in column 3 (0-indexed)
            
            # Get directors for this movie
            if movie_imdb_id in directors_map:
                for director in directors_map[movie_imdb_id]:
                    # Create director row: Type, Active, Name, Imdb id, Movie Tier, Production Cost, Rank, Price
                    director_row = [
                        'Director',  # Type
                        'TRUE',      # Active
                        director['name'],  # Name
                        director['imdb_id'],  # Imdb id
                        '',          # Movie Tier (blank)
                        '',          # Production Cost (blank)
                        '',          # Rank (blank)
                        ''           # Price (blank)
                    ]
                    output_rows.append(director_row)

# Write the output back to reordered_output.csv
with open('reordered_output.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(output_rows)

print(f"Added directors to {len(directors_map)} movies")


