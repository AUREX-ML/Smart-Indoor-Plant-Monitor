import sqlite3
import pandas as pd

# Connect to the database created by the simulation
conn = sqlite3.connect("plant_data.db")

# Load into Pandas for "Analysis"
df = pd.read_sql_query("SELECT * FROM sensor_logs", conn)

print("--- HISTORICAL DATA ---")
print(df.head(10)) 
conn.close()