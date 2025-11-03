import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="World Population Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class PopulationDashboard:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        """Load and generate sample population data"""
        # In a real application, you would load from CSV/API
        # For demo purposes, we'll generate synthetic data
        
        countries = [
            'China', 'India', 'United States', 'Indonesia', 'Pakistan',
            'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico',
            'Japan', 'Ethiopia', 'Philippines', 'Egypt', 'Vietnam',
            'DR Congo', 'Turkey', 'Iran', 'Germany', 'Thailand'
        ]
        
        regions = {
            'Asia': ['China', 'India', 'Indonesia', 'Pakistan', 'Bangladesh', 
                    'Japan', 'Philippines', 'Vietnam', 'Iran', 'Thailand'],
            'Europe': ['Russia', 'Germany', 'Turkey'],
            'North America': ['United States', 'Mexico'],
            'South America': ['Brazil'],
            'Africa': ['Nigeria', 'Ethiopia', 'Egypt', 'DR Congo']
        }
        
        # Generate population data for multiple years
        years = list(range(1950, 2024, 5))
        data = []
        
        base_populations = {
            'China': 550, 'India': 350, 'United States': 150, 'Indonesia': 70,
            'Pakistan': 40, 'Brazil': 50, 'Nigeria': 30, 'Bangladesh': 40,
            'Russia': 100, 'Mexico': 30, 'Japan': 80, 'Ethiopia': 20,
            'Philippines': 20, 'Egypt': 20, 'Vietnam': 25, 'DR Congo': 15,
            'Turkey': 20, 'Iran': 20, 'Germany': 70, 'Thailand': 20
        }
        
        for country in countries:
            base_pop = base_populations[country] * 1e6  # Convert to actual numbers
            growth_rate = np.random.uniform(0.005, 0.025)  # 0.5% to 2.5% annual growth
            
            for year in years:
                years_passed = year - 1950
                population = base_pop * (1 + growth_rate) ** years_passed
                
                # Add some randomness
                population *= np.random.uniform(0.95, 1.05)
                
                # Find region
                region = next((reg for reg, countries in regions.items() 
                             if country in countries), 'Other')
                
                data.append({
                    'Country': country,
                    'Year': year,
                    'Population': int(population),
                    'Region': region
                })
        
        self.df = pd.DataFrame(data)
        
        # Create summary statistics
        self.summary_df = self.df.groupby(['Country', 'Region']).agg({
            'Population': ['min', 'max']
        }).round(0)
        self.summary_df.columns = ['Population_1950', 'Population_2023']
        self.summary_df = self.summary_df.reset_index()
        self.summary_df['Growth'] = ((self.summary_df['Population_2023'] - 
                                    self.summary_df['Population_1950']) / 
                                   self.summary_df['Population_1950'] * 100)
    
    def create_world_map(self, selected_year):
        """Create an interactive world map"""
        year_data = self.df[self.df['Year'] == selected_year]
        
        fig = px.choropleth(
            year_data,
            locations="Country",
            locationmode="country names",
            color="Population",
            hover_name="Country",
            hover_data={"Population": True, "Year": True},
            color_continuous_scale="Viridis",
            title=f"World Population Distribution - {selected_year}",
            projection="natural earth"
        )
        
        fig.update_layout(
            height=600,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            )
        )
        
        return fig
    
    def create_population_trend(self, selected_countries):
        """Create population trend line chart"""
        filtered_df = self.df[self.df['Country'].isin(selected_countries)]
        
        fig = px.line(
            filtered_df,
            x="Year",
            y="Population",
            color="Country",
            title="Population Trends Over Time",
            labels={"Population": "Population", "Year": "Year"}
        )
        
        fig.update_layout(
            height=500,
            xaxis=dict(tickmode='linear', dtick=10),
            yaxis=dict(tickformat=",d")
        )
        
        return fig
    
    def create_population_pyramid(self, selected_year):
        """Create a population pyramid (simulated age distribution)"""
        # Generate synthetic age distribution data
        countries = st.session_state.get('selected_countries', ['China', 'India'])
        pyramid_data = []
        
        for country in countries:
            # Simulate different age distributions
            if country == 'China':
                base_pop = self.df[(self.df['Country'] == country) & 
                                 (self.df['Year'] == selected_year)]['Population'].values[0]
                # Older population structure
                age_groups = ['0-14', '15-24', '25-54', '55-64', '65+']
                male_dist = [0.15, 0.12, 0.35, 0.18, 0.20]
                female_dist = [0.14, 0.11, 0.33, 0.19, 0.23]
            else:
                # Younger population structure
                age_groups = ['0-14', '15-24', '25-54', '55-64', '65+']
                male_dist = [0.25, 0.20, 0.40, 0.10, 0.05]
                female_dist = [0.24, 0.19, 0.38, 0.12, 0.07]
            
            for age_group, male_pct, female_pct in zip(age_groups, male_dist, female_dist):
                pyramid_data.extend([
                    {
                        'Country': country,
                        'Age Group': age_group,
                        'Gender': 'Male',
                        'Population': int(base_pop * male_pct * 0.5),  # 50% of percentage
                        'Percentage': male_pct * 100
                    },
                    {
                        'Country': country,
                        'Age Group': age_group,
                        'Gender': 'Female',
                        'Population': int(base_pop * female_pct * 0.5),
                        'Percentage': female_pct * 100
                    }
                ])
        
        pyramid_df = pd.DataFrame(pyramid_data)
        
        fig = px.bar(
            pyramid_df,
            x="Population",
            y="Age Group",
            color="Gender",
            barmode="relative",
            orientation="h",
            facet_col="Country",
            title=f"Population Pyramid - {selected_year}",
            labels={"Population": "Population", "Age Group": "Age Group"}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_region_comparison(self):
        """Create regional population comparison"""
        region_data = self.df.groupby(['Region', 'Year'])['Population'].sum().reset_index()
        
        fig = px.area(
            region_data,
            x="Year",
            y="Population",
            color="Region",
            title="Population by Region Over Time",
            labels={"Population": "Total Population", "Year": "Year"}
        )
        
        fig.update_layout(height=500, yaxis=dict(tickformat=",d"))
        return fig
    
    def create_growth_ranking(self):
        """Create growth rate ranking chart"""
        growth_ranking = self.summary_df.nlargest(10, 'Growth')[['Country', 'Growth']]
        
        fig = px.bar(
            growth_ranking,
            x='Growth',
            y='Country',
            orientation='h',
            title="Top 10 Countries by Population Growth Rate (1950-2023)",
            labels={"Growth": "Growth Rate (%)", "Country": "Country"}
        )
        
        fig.update_layout(height=500)
        return fig

def main():
    # Initialize dashboard
    dashboard = PopulationDashboard()
    
    # Header
    st.markdown('<h1 class="main-header">🌍 World Population Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Filters & Controls")
    
    # Year selection
    years = sorted(dashboard.df['Year'].unique())
    selected_year = st.sidebar.select_slider(
        "Select Year",
        options=years,
        value=2020
    )
    
    # Country selection
    all_countries = sorted(dashboard.df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=['China', 'India', 'United States'],
        key='selected_countries'
    )
    
    # Region filter
    regions = sorted(dashboard.df['Region'].unique())
    selected_regions = st.sidebar.multiselect(
        "Filter by Region",
        options=regions,
        default=regions
    )
    
    # Apply region filter
    if selected_regions:
        filtered_countries = dashboard.df[dashboard.df['Region'].isin(selected_regions)]['Country'].unique()
        selected_countries = [c for c in selected_countries if c in filtered_countries]
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_pop = dashboard.df[dashboard.df['Year'] == selected_year]['Population'].sum()
        st.metric(
            label="World Population",
            value=f"{current_pop:,.0f}",
            delta=f"{(current_pop - dashboard.df[dashboard.df['Year'] == selected_year-5]['Population'].sum()):,.0f}"
        )
    
    with col2:
        num_countries = len(selected_countries) if selected_countries else len(all_countries)
        st.metric("Countries Displayed", num_countries)
    
    with col3:
        avg_growth = dashboard.summary_df['Growth'].mean()
        st.metric("Average Growth Rate", f"{avg_growth:.1f}%")
    
    with col4:
        total_growth = dashboard.summary_df['Growth'].sum()
        st.metric("Total Growth", f"{total_growth:,.0f}%")
    
    # Charts
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "World Map", "Trends", "Population Pyramid", "Regional View", "Growth Ranking"
    ])
    
    with tab1:
        st.plotly_chart(dashboard.create_world_map(selected_year), use_container_width=True)
    
    with tab2:
        if selected_countries:
            st.plotly_chart(dashboard.create_population_trend(selected_countries), 
                          use_container_width=True)
        else:
            st.warning("Please select at least one country to view trends.")
    
    with tab3:
        if len(selected_countries) >= 2:
            st.plotly_chart(dashboard.create_population_pyramid(selected_year), 
                          use_container_width=True)
        else:
            st.info("Select at least 2 countries to compare population pyramids.")
    
    with tab4:
        st.plotly_chart(dashboard.create_region_comparison(), use_container_width=True)
    
    with tab5:
        st.plotly_chart(dashboard.create_growth_ranking(), use_container_width=True)
    
    # Data table
    st.subheader("Population Data")
    display_df = dashboard.df[
        (dashboard.df['Country'].isin(selected_countries if selected_countries else all_countries)) &
        (dashboard.df['Year'] == selected_year)
    ][['Country', 'Region', 'Population']].sort_values('Population', ascending=False)
    
    st.dataframe(
        display_df.style.format({'Population': '{:,}'}),
        use_container_width=True
    )
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download Current View as CSV",
        data=csv,
        file_name=f"population_data_{selected_year}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()