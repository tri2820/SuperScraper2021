import pandas as pd

# Read the csv file in
df = pd.read_csv('performance_pivot telstrasuper.csv')

# Save to file
df.to_html('telstrasuperTable.html')

# Assign to string
htmTable = df.to_html()