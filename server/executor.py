
import pandas as pd
import matplotlib.pyplot as plt

# Read dataset path from temp file
with open('./uploads/temp.txt', 'r', encoding='utf-8') as f:
    dataset_path = f.readline().strip()

# Load the dataset
df = pd.read_csv(dataset_path)

# Data Cleaning and Preparation
# Convert 'Year' to datetime objects, handling potential errors
try:
    df['Year'] = pd.to_datetime(df['Year'], format='%Y', errors='raise').dt.year
except ValueError:
    try:
        df['Year'] = pd.to_datetime(df['Year'], errors='raise').dt.year
    except ValueError:
        print("Error: Could not convert 'Year' column to datetime.  Check format (YYYY or other date format).")
        exit()

# Group by year and sum global sales
sales_by_year = df.groupby('Year')['Global_Sales'].sum()

# Create the bar chart
plt.figure(figsize=(12, 6))  # Adjust figure size for better readability

sales_by_year.plot(kind='bar', color='skyblue') # Added some visual appeal

plt.title('Global Sales per Year', fontsize=16)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Global Sales (Millions)', fontsize=12)
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
plt.tight_layout() # Adjust layout to prevent labels from overlapping

# Save the chart
plt.savefig('./uploads/global_sales_per_year_barchart.png')
