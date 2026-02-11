import pandas as pd
import sqlite3
import os

# Database path
db_path = 'data/iphone_data.db'
excel_path = 'data/apple_products.xlsx'

# Create database connection
conn = sqlite3.connect(db_path)

print("📊 Loading data from Excel file...")

try:
    # Read all sheets from Excel
    revenue_df = pd.read_excel(excel_path, sheet_name='Annual Revenue')
    market_pen_df = pd.read_excel(excel_path, sheet_name='Market Penetration(iphone)')
    country_share_df = pd.read_excel(excel_path, sheet_name='Country-wise share')
    quarterly_df = pd.read_excel(excel_path, sheet_name='Quarterly-share')
    model_share_df = pd.read_excel(excel_path, sheet_name='Model share')
    region_revenue_df = pd.read_excel(excel_path, sheet_name='Apple  revenue by region')
    
    # Store data in database
    revenue_df.to_sql('annual_revenue', conn, if_exists='replace', index=False)
    print(f"✅ Loaded {len(revenue_df)} revenue records")
    
    market_pen_df.to_sql('market_penetration', conn, if_exists='replace', index=False)
    print(f"✅ Loaded {len(market_pen_df)} market penetration records")
    
    country_share_df.to_sql('country_share', conn, if_exists='replace', index=False)
    print(f"✅ Loaded {len(country_share_df)} country share records")
    
    quarterly_df.to_sql('quarterly_share', conn, if_exists='replace', index=False)
    print(f"✅ Loaded {len(quarterly_df)} quarterly records")
    
    model_share_df.to_sql('model_share', conn, if_exists='replace', index=False)
    print(f"✅ Loaded {len(model_share_df)} model share records")
    
    region_revenue_df.to_sql('region_revenue', conn, if_exists='replace', index=False)
    print(f"✅ Loaded {len(region_revenue_df)} region revenue records")
    
    # Verify data
    cursor = conn.cursor()
    cursor.execute("SELECT Year, `Revenue ($bn)` FROM annual_revenue ORDER BY Year DESC LIMIT 5")
    latest_revenue = cursor.fetchall()
    
    print("\n📈 Latest Revenue Data:")
    for year, revenue in latest_revenue:
        print(f"   {year}: ${revenue:.1f}B")
    
    print("\n✨ Database successfully updated with your Excel data!")
    print(f"   Total tables: 6")
    print(f"   Database location: {db_path}")
    
except Exception as e:
    print(f"❌ Error loading Excel data: {e}")
    print("   Make sure apple_products.xlsx is in the data/ folder")

finally:
    conn.close()
