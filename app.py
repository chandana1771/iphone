from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
DATABASE = 'data/iphone_data.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = get_db()
    for csv_file, table in [
        ('data/annual_revenue.csv',    'annual_revenue'),
        ('data/market_penetration.csv','market_penetration'),
        ('data/country_share.csv',     'country_share'),
        ('data/quarterly_share.csv',   'quarterly_share'),
        ('data/model_share.csv',       'model_share'),
        ('data/region_revenue.csv',    'region_revenue'),
        ('data/sales_data.csv',        'sales_data'),
        ('data/user_demographics.csv', 'user_demographics'),
        ('data/social_sentiment.csv',  'social_sentiment'),
    ]:
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df.to_sql(table, conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/story')
def story():
    return render_template('story.html')

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('SELECT SUM("Revenue ($bn)") FROM annual_revenue WHERE Year >= 2019')
        total_rev = c.fetchone()[0] or 0
        c.execute('SELECT MAX("Revenue ($bn)") FROM annual_revenue')
        peak_rev = c.fetchone()[0] or 0
        c.execute('SELECT SUM("Units sold (mm)") FROM market_penetration WHERE Year >= 2019')
        total_units = c.fetchone()[0] or 0
        c.execute('SELECT MAX("Active Users (mm)") FROM market_penetration')
        active_users = c.fetchone()[0] or 0
    except:
        total_rev, peak_rev, total_units, active_users = 1294.7, 394.3, 1058.3, 1334
    conn.close()
    return jsonify({
        'total_revenue': round(float(total_rev), 1),
        'peak_revenue':  round(float(peak_rev), 1),
        'total_units':   round(float(total_units), 1),
        'active_users':  round(float(active_users), 0)
    })

@app.route('/api/revenue')
def get_revenue():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Year, "Revenue ($bn)" FROM annual_revenue ORDER BY Year')
    rows = [{'year': r[0], 'revenue': r[1]} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/penetration')
def get_penetration():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Year, "Units sold (mm)", "Revenue Generated", "Active Users (mm)" FROM market_penetration ORDER BY Year')
    rows = [{'year': r[0], 'units': r[1], 'revenue': r[2], 'active_users': r[3]} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/region-revenue')
def get_region_revenue():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Year, Americas, Europe, China, Japan, "Rest of Asia Pacific" FROM region_revenue ORDER BY Year')
    rows = [{'year': r[0], 'Americas': r[1], 'Europe': r[2], 'China': r[3], 'Japan': r[4], 'Asia_Pacific': r[5]} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/model-share')
def get_model_share():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Models, "Sales Share" FROM model_share ORDER BY "Sales Share" DESC')
    rows = [{'model': r[0].replace('Apple ',''), 'share': round(float(r[1])*100, 1)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/country-share')
def get_country_share():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Country, Models, "Sales Share" FROM country_share ORDER BY Country, "Sales Share" DESC')
    rows = [{'country': r[0], 'model': r[1].replace('Apple ',''), 'share': round(float(r[2])*100,1)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/quarterly')
def get_quarterly():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Year, Brand, Q1, Q2, Q3, Q4 FROM quarterly_share ORDER BY Year, Brand')
    rows = [{'year': r[0], 'brand': r[1],
             'Q1': round(float(r[2])*100,1), 'Q2': round(float(r[3])*100,1),
             'Q3': round(float(r[4])*100,1), 'Q4': round(float(r[5])*100,1)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/sales')
def get_sales():
    conn = get_db()
    c = conn.cursor()
    region = request.args.get('region')
    year   = request.args.get('year')
    q = 'SELECT * FROM sales_data WHERE 1=1'
    params = []
    if region: q += ' AND Region=?'; params.append(region)
    if year:   q += ' AND Year=?';   params.append(year)
    c.execute(q + ' ORDER BY Year, Quarter, Region', params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/sales-summary')
def get_sales_summary():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Region, SUM(Units_Sold) as u, SUM(Revenue) as r, AVG(Market_Share) as s FROM sales_data GROUP BY Region')
    rows = [{'region': r[0], 'units': int(r[1]), 'revenue': round(r[2]/1e9,2), 'share': round(r[3],2)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/sales-by-model')
def get_sales_by_model():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Model, SUM(Units_Sold) as u, SUM(Revenue) as r FROM sales_data GROUP BY Model ORDER BY u DESC')
    rows = [{'model': r[0], 'units': int(r[1]), 'revenue': round(r[2]/1e9,2)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/demographics')
def get_demographics():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Age_Group, SUM(Users_Count) as total, AVG(Avg_Purchase_Value) as avg_val FROM user_demographics GROUP BY Age_Group ORDER BY Age_Group')
    rows = [{'age': r[0], 'users': int(r[1]), 'avg_value': round(r[2],0)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/demographics-income')
def get_demographics_income():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Income_Level, SUM(Users_Count) as total FROM user_demographics GROUP BY Income_Level')
    rows = [{'level': r[0], 'users': int(r[1])} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/demographics-gender')
def get_demographics_gender():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Gender, SUM(Users_Count) as total FROM user_demographics GROUP BY Gender')
    rows = [{'gender': r[0], 'users': int(r[1])} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/demographics-region')
def get_demographics_region():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Region, SUM(Users_Count) as total, AVG(Avg_Purchase_Value) as avg_val FROM user_demographics GROUP BY Region')
    rows = [{'region': r[0], 'users': int(r[1]), 'avg_value': round(r[2],0)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/sentiment')
def get_sentiment():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Sentiment, COUNT(*) as cnt, SUM(Mentions) as total, AVG(Engagement_Rate) as eng FROM social_sentiment GROUP BY Sentiment')
    rows = [{'sentiment': r[0], 'count': r[1], 'mentions': int(r[2]), 'engagement': round(r[3],2)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/sentiment-platform')
def get_sentiment_platform():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Platform, Sentiment, SUM(Mentions) as total FROM social_sentiment GROUP BY Platform, Sentiment')
    rows = [{'platform': r[0], 'sentiment': r[1], 'mentions': int(r[2])} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/sentiment-topics')
def get_sentiment_topics():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT Topic, SUM(Mentions) as total, AVG(Engagement_Rate) as eng FROM social_sentiment GROUP BY Topic ORDER BY total DESC LIMIT 8')
    rows = [{'topic': r[0], 'mentions': int(r[1]), 'engagement': round(r[2],2)} for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
