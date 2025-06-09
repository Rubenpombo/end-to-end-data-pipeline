from flask import Flask, render_template, jsonify
from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging
from datetime import datetime
import json
import plotly

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if pd.isna(obj):
            return None
        return super().default(obj)

app.json_encoder = JSONEncoder

def get_cassandra_session():
    """
    Creates and returns a Cassandra session.
    """
    try:
        cluster = Cluster(['localhost'], port=9042, load_balancing_policy=RoundRobinPolicy(), protocol_version=5)
        session = cluster.connect()
        session.set_keyspace('spark_streams')
        return cluster, session
    except Exception as e:
        logging.error(f"Failed to connect to Cassandra: {e}")
        raise

def get_cassandra_data():
    """
    Connects to Cassandra and retrieves data from the 'created_users' table.
    Returns the data as a Pandas DataFrame.
    """
    cluster, session = get_cassandra_session()
    
    try:
        # Query all relevant columns
        query = """SELECT id, first_name, last_name, gender, email, nationality, 
                   dob, registered_date FROM created_users"""
        rows = session.execute(query)

        data = []
        for row in rows:
            data.append({
                'id': str(row.id),
                'first_name': row.first_name,
                'last_name': row.last_name,
                'gender': row.gender,
                'email': row.email,
                'nationality': row.nationality,
                'dob': row.dob,
                'registered_date': row.registered_date
            })

        df = pd.DataFrame(data)
        logging.info(f"Successfully fetched {len(df)} records from Cassandra")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching data from Cassandra: {e}")
        raise
    finally:
        cluster.shutdown()

def process_dataframe(df):
    """
    Process the dataframe to clean and prepare data for visualizations.
    """
    if df.empty:
        return df
    
    # Convert date columns
    df['dob'] = pd.to_datetime(df['dob'], errors='coerce')
    df['registered_date'] = pd.to_datetime(df['registered_date'], errors='coerce')
    
    # Calculate age
    current_date = pd.Timestamp.now()
    df['age'] = ((current_date - df['dob']).dt.days / 365.25).round(0)
    
    # Clean gender data (handle case variations)
    df['gender'] = df['gender'].str.title().fillna('Unknown')
    
    # Clean nationality data
    df['nationality'] = df['nationality'].str.title().fillna('Unknown')
    
    # Remove rows with invalid ages (negative or > 120)
    df = df[(df['age'] >= 0) & (df['age'] <= 120)]
    
    return df

@app.route('/')
def index():
    """
    Renders the main dashboard page.
    """
    return render_template('index.html')

@app.route('/data')
def data():
    """
    API endpoint to fetch data from Cassandra and return it as JSON.
    """
    try:
        df = get_cassandra_data()
        df = process_dataframe(df)
        logging.info(f"Data processed successfully. Records: {len(df)}")
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logging.error(f"Error in data endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """
    API endpoint to get basic statistics about the data.
    """
    try:
        df = get_cassandra_data()
        df = process_dataframe(df)
        
        if df.empty:
            return jsonify({'error': 'No data available'})
        
        stats = {
            'total_users': len(df),
            'avg_age': df['age'].mean().round(1) if not df['age'].isna().all() else 0,
            'gender_distribution': df['gender'].value_counts().to_dict(),
            'nationality_count': df['nationality'].nunique(),
            'date_range': {
                'earliest': df['registered_date'].min().isoformat() if not df['registered_date'].isna().all() else None,
                'latest': df['registered_date'].max().isoformat() if not df['registered_date'].isna().all() else None
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Error generating stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/visualization_gender_nationality')
def visualization_gender_nationality():
    """
    Generates an enhanced bar chart showing gender distribution by nationality.
    """
    try:
        df = get_cassandra_data()
        df = process_dataframe(df)
        
        if df.empty:
            logging.warning("No data available for gender-nationality visualization.")
            return "<div style='text-align: center; padding: 50px;'><h3>No data available to visualize</h3></div>"
        
        # Group data and get top 15 nationalities to avoid overcrowding
        nationality_counts = df['nationality'].value_counts().head(15).index
        df_filtered = df[df['nationality'].isin(nationality_counts)]
        
        # Create grouped bar chart
        fig = px.histogram(
            df_filtered, 
            x='nationality', 
            color='gender',
            title='User Distribution by Nationality and Gender (Top 15 Countries)',
            labels={'nationality': 'Country', 'count': 'Number of Users'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        # Enhance the layout
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title=dict(x=0.5, font=dict(size=16)),
            xaxis=dict(tickangle=45),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=500
        )
        
        logging.info("Gender-nationality visualization generated successfully.")
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    except Exception as e:
        logging.error(f"Error generating gender-nationality visualization: {e}")
        return f"<div style='text-align: center; padding: 50px;'><h3>Error generating visualization: {str(e)}</h3></div>"

@app.route('/visualization_age_registration')
def visualization_age_registration():
    """
    Generates an enhanced scatter plot showing the relationship between user age and registration date.
    """
    try:
        df = get_cassandra_data()
        df = process_dataframe(df)
        
        if df.empty:
            logging.warning("No data available for age-registration visualization.")
            return "<div style='text-align: center; padding: 50px;'><h3>No data available to visualize</h3></div>"
        
        # Remove rows with missing age or registration date
        df_clean = df.dropna(subset=['age', 'registered_date'])
        
        if df_clean.empty:
            return "<div style='text-align: center; padding: 50px;'><h3>No valid age/registration data available</h3></div>"
        
        # Create scatter plot
        fig = px.scatter(
            df_clean, 
            x='registered_date', 
            y='age',
            color='gender',
            title='User Age vs Registration Date',
            labels={'registered_date': 'Registration Date', 'age': 'Age (Years)'},
            hover_data=['nationality', 'first_name', 'last_name'],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        # Add trend line
        fig.add_traces(px.scatter(df_clean, x='registered_date', y='age', trendline="lowess").data[1:])
        
        # Enhance the layout
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title=dict(x=0.5, font=dict(size=16)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=500,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray')
        )
        
        logging.info("Age-registration visualization generated successfully.")
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    except Exception as e:
        logging.error(f"Error generating age-registration visualization: {e}")
        return f"<div style='text-align: center; padding: 50px;'><h3>Error generating visualization: {str(e)}</h3></div>"

@app.route('/visualization_age_distribution')
def visualization_age_distribution():
    """
    Generates a histogram showing age distribution.
    """
    try:
        df = get_cassandra_data()
        df = process_dataframe(df)
        
        if df.empty or df['age'].isna().all():
            return "<div style='text-align: center; padding: 50px;'><h3>No age data available</h3></div>"
        
        fig = px.histogram(
            df, 
            x='age', 
            nbins=20,
            title='Age Distribution of Users',
            labels={'age': 'Age (Years)', 'count': 'Number of Users'},
            color_discrete_sequence=['#636EFA']
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title=dict(x=0.5, font=dict(size=16)),
            height=400,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    except Exception as e:
        logging.error(f"Error generating age distribution visualization: {e}")
        return f"<div style='text-align: center; padding: 50px;'><h3>Error generating visualization: {str(e)}</h3></div>"

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    return "Internal server error", 500

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)