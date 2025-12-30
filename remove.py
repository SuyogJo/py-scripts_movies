import pandas as pd

# Read the CSV file
df = pd.read_csv('ordered_data.csv')

# Filter out rows where rank > 16 (keep only rows where rank <= 16)
df_filtered = df[df['rank'] < 16]

# Save the filtered data back to the CSV file
df_filtered.to_csv('ordered_data.csv', index=False)

print(f"Removed rows with rank > 16. Original rows: {len(df)}, Remaining rows: {len(df_filtered)}")

