import sqlite3
import pandas as pd
import os

# Database file path
db_path = 'data/iphone_data.db'

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
print("Creating tables...")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER,
        quarter TEXT,
        region TEXT,
        state TEXT,
        model TEXT,
        units_sold INTEGER,
        revenue REAL,
        market_share REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_demographics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age_group TEXT,
        income_level TEXT,
        gender TEXT,
        region TEXT,
        users_count INTEGER,
        avg_purchase_value REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS social_sentiment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        platform TEXT,
        sentiment TEXT,
        mentions INTEGER,
        engagement_rate REAL,
        topic TEXT
    )
''')

conn.commit()

# Load and insert sales data
print("Loading sales data...")
try:
    sales_df = pd.read_csv('data/sales_data.csv')
    sales_df.to_sql('sales_data', conn, if_exists='replace', index=False)
    print(f"Inserted {len(sales_df)} sales records")
except Exception as e:
    print(f"Error loading sales data: {e}")

# Load and insert demographics data
print("Loading demographics data...")
try:
    demographics_df = pd.read_csv('data/user_demographics.csv')
    demographics_df.to_sql('user_demographics', conn, if_exists='replace', index=False)
    print(f"Inserted {len(demographics_df)} demographic records")
except Exception as e:
    print(f"Error loading demographics data: {e}")

# Load and insert sentiment data
print("Loading sentiment data...")
try:
    sentiment_df = pd.read_csv('data/social_sentiment.csv')
    sentiment_df.to_sql('social_sentiment', conn, if_exists='replace', index=False)
    print(f"Inserted {len(sentiment_df)} sentiment records")
except Exception as e:
    print(f"Error loading sentiment data: {e}")

# Verify data
print("\nVerifying data...")
cursor.execute('SELECT COUNT(*) FROM sales_data')
print(f"Sales records: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM user_demographics')
print(f"Demographics records: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM social_sentiment')
print(f"Sentiment records: {cursor.fetchone()[0]}")

# Close connection
conn.close()
print("\nDatabase initialization complete!")
