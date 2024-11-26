import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot

from flask import Flask, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import json
import requests
from datetime import datetime
import numpy as np
from io import StringIO
import os

app = Flask(__name__)

# Add number formatting filter
@app.template_filter('format_number')
def format_number(value):
    return "{:,}".format(value)

# Global variable to store the data
covid_data = None

def load_covid_data():
    """Load and cache COVID-19 data"""
    global covid_data
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    print("Fetching data from:", url)
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        covid_data = pd.read_csv(StringIO(response.text))
        print("Data loaded successfully")
        print("Total rows:", len(covid_data))
        print("Columns:", covid_data.columns.tolist())
        
        covid_data['date'] = pd.to_datetime(covid_data['date'])
        return covid_data
        
    except Exception as e:
        print("Error loading data:", str(e))
        # Create an empty DataFrame with required columns if data loading fails
        covid_data = pd.DataFrame(columns=['date', 'location', 'total_cases', 'new_cases', 
                                         'total_deaths', 'total_vaccinations', 'gdp_per_capita',
                                         'population', 'total_cases_per_million'])
        return covid_data

def create_trend_analysis():
    """Create global trend analysis plot"""
    plt.figure(figsize=(12, 6))
    df = covid_data.groupby('date')['new_cases'].sum().reset_index()
    df['rolling_avg'] = df['new_cases'].rolling(window=7).mean()
    
    plt.plot(df['date'], df['new_cases'], color='lightgray', alpha=0.5, label='Daily Cases')
    plt.plot(df['date'], df['rolling_avg'], color='blue', label='7-day Moving Average')
    
    plt.title('Global COVID-19 Cases Trend')
    plt.xlabel('Date')
    plt.ylabel('Number of Cases')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot
    plt.savefig('static/images/trend_plot.png')
    plt.close()

def create_vaccination_analysis():
    """Create vaccination progress analysis"""
    plt.figure(figsize=(10, 6))
    recent_data = covid_data[covid_data['date'] == covid_data['date'].max()]
    top_countries = recent_data.nlargest(15, 'people_fully_vaccinated_per_hundred')
    
    sns.barplot(data=top_countries, 
               y='location', 
               x='people_fully_vaccinated_per_hundred',
               color='red')
    
    plt.title('Vaccination Progress by Country')
    plt.xlabel('Fully Vaccinated (%)')
    plt.ylabel('Country')
    plt.tight_layout()
    
    # Save plot
    plt.savefig('static/images/vaccination_plot.png')
    plt.close()

def create_geographic_comparison():
    """Create geographic comparison of total cases"""
    plt.figure(figsize=(10, 6))
    recent_data = covid_data[covid_data['date'] == covid_data['date'].max()]
    
    print("Initial data shape:", recent_data.shape)
    print("Columns available:", recent_data.columns.tolist())
    
    # Check for missing columns
    required_columns = ['gdp_per_capita', 'total_cases_per_million', 'population', 'location']
    missing_columns = [col for col in required_columns if col not in recent_data.columns]
    if missing_columns:
        print("Missing columns:", missing_columns)
        # Create a simple scatter plot instead
        plt.text(0.5, 0.5, 'Data not available', ha='center', va='center')
        plt.title('COVID-19 Cases vs GDP per Capita')
        plt.tight_layout()
        plt.savefig('static/images/geographic_plot.png')
        plt.close()
        return

    # Print value ranges before filtering
    print("GDP range:", recent_data['gdp_per_capita'].min(), "-", recent_data['gdp_per_capita'].max())
    print("Cases range:", recent_data['total_cases_per_million'].min(), "-", recent_data['total_cases_per_million'].max())
    print("Population range:", recent_data['population'].min(), "-", recent_data['population'].max())
    
    # Filter out rows with missing or invalid values
    valid_data = recent_data.dropna(subset=['gdp_per_capita', 'total_cases_per_million', 'population'])
    print("After dropping NA:", valid_data.shape)
    
    valid_data = valid_data[
        (valid_data['gdp_per_capita'] > 0) & 
        (valid_data['total_cases_per_million'] > 0) &
        (valid_data['population'] > 0)
    ]
    print("After filtering zeros:", valid_data.shape)
    
    if valid_data.empty:
        plt.text(0.5, 0.5, 'No valid data available', ha='center', va='center')
        plt.title('COVID-19 Cases vs GDP per Capita')
        plt.tight_layout()
        plt.savefig('static/images/geographic_plot.png')
        plt.close()
        return
    
    # Create basic scatter plot
    plt.scatter(valid_data['gdp_per_capita'], 
               valid_data['total_cases_per_million'],
               alpha=0.6,
               s=valid_data['population']/1e6,
               c='blue')
    
    plt.title('COVID-19 Cases vs GDP per Capita')
    plt.xlabel('GDP per Capita')
    plt.ylabel('Total Cases per Million')
    
    # Only use log scale if we have valid positive values
    if (valid_data['gdp_per_capita'] > 0).any() and (valid_data['total_cases_per_million'] > 0).any():
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('GDP per Capita (log scale)')
        plt.ylabel('Total Cases per Million (log scale)')
    
    plt.grid(True, alpha=0.3)
    
    # Add text labels for some notable countries
    for idx, row in valid_data.nlargest(5, 'total_cases_per_million').iterrows():
        plt.annotate(row['location'], 
                    (row['gdp_per_capita'], row['total_cases_per_million']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8)
    
    plt.tight_layout()
    plt.savefig('static/images/geographic_plot.png')
    plt.close()

@app.route('/')
def index():
    if covid_data is None:
        load_covid_data()
    
    # Create images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Generate plots
    create_trend_analysis()
    create_vaccination_analysis()
    create_geographic_comparison()
    
    # Get summary data
    recent_date = covid_data['date'].max()
    recent_data = covid_data[covid_data['date'] == recent_date]
    
    summary = {
        'total_cases': int(recent_data['total_cases'].sum()),
        'total_deaths': int(recent_data['total_deaths'].sum()),
        'total_vaccinations': int(recent_data['total_vaccinations'].sum()),
        'countries_reported': len(recent_data),
        'last_updated': recent_date.strftime('%Y-%m-%d')
    }
    
    return render_template('index.html', summary=summary)

@app.route('/api/summary')
def get_summary():
    """API endpoint for summary statistics"""
    recent_date = covid_data['date'].max()
    recent_data = covid_data[covid_data['date'] == recent_date]
    
    summary = {
        'total_cases': int(recent_data['total_cases'].sum()),
        'total_deaths': int(recent_data['total_deaths'].sum()),
        'total_vaccinations': int(recent_data['total_vaccinations'].sum()),
        'countries_reported': len(recent_data),
        'last_updated': recent_date.strftime('%Y-%m-%d')
    }
    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
