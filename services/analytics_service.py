import pandas as pd
from services.data_service import data_service
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalyticsService:
    
    def __init__(self):
        self.data_service = data_service
    
    def get_trend_analysis(self, countries=None, start_year=None, end_year=None):
        df = self.data_service.filter_data(countries, start_year, end_year)
        
        if df.empty:
            return None

        yearly = df.groupby('Year').agg({
            'Im_Value': 'sum',
            'Em_Value': 'sum',
            'Net_Migration': 'sum'
        }).reset_index()
        
        return yearly.to_dict('records')
    
    def get_country_comparison(self, countries, start_year=None, end_year=None):
        df = self.data_service.filter_data(countries, start_year, end_year)
        
        if df.empty:
            return None
        
        comparison = df.groupby('Country').agg({
            'Im_Value': ['sum', 'mean'],
            'Em_Value': ['sum', 'mean'],
            'Net_Migration': ['sum', 'mean']
        }).reset_index()
        
        comparison.columns = ['Country', 'Total_Immigration', 'Avg_Immigration',
                              'Total_Emigration', 'Avg_Emigration',
                              'Total_Net_Migration', 'Avg_Net_Migration']
        
        return comparison.to_dict('records')
    
    def get_top_countries(self, metric='net', limit=10, year=None):
        if year:
            df = self.data_service.filter_data(year=year)
        else:
            df = self.data_service.get_all_data()
            df = df.groupby('Country').agg({
                'Im_Value': 'sum',
                'Em_Value': 'sum',
                'Net_Migration': 'sum'
            }).reset_index()
        
        metric_map = {
            'immigration': 'Im_Value',
            'emigration': 'Em_Value',
            'net': 'Net_Migration'
        }
        
        sort_column = metric_map.get(metric, 'Net_Migration')
        top = df.nlargest(limit, sort_column)
        
        return top.to_dict('records')
    
    def get_migration_balance(self, countries=None, start_year=None, end_year=None):
        #! positive/negative net migration
        df = self.data_service.filter_data(countries, start_year, end_year)
        
        if df.empty:
            return None
        
        positive = df[df['Net_Migration'] > 0]
        negative = df[df['Net_Migration'] < 0]
        
        return {
            'positive_net_migration': {
                'count': len(positive),
                'total': int(positive['Net_Migration'].sum()),
                'countries': positive.groupby('Country')['Net_Migration'].sum().to_dict()
            },
            'negative_net_migration': {
                'count': len(negative),
                'total': int(negative['Net_Migration'].sum()),
                'countries': negative.groupby('Country')['Net_Migration'].sum().to_dict()
            }
        }
    
    def get_yearly_growth(self, country=None):
        #* calculate year-over-year growth
        if country:
            df = self.data_service.filter_data(countries=[country])
        else:
            df = self.data_service.get_all_data()
            df = df.groupby('Year').agg({
                'Im_Value': 'sum',
                'Em_Value': 'sum',
                'Net_Migration': 'sum'
            }).reset_index()
        
        df = df.sort_values('Year')
        
        #  growth rates
        df['Im_Growth'] = df['Im_Value'].pct_change() * 100
        df['Em_Growth'] = df['Em_Value'].pct_change() * 100
        df['Net_Growth'] = df['Net_Migration'].pct_change() * 100
        
        return df.to_dict('records')
    
    def get_correlation_analysis(self):
        df = self.data_service.get_all_data()
        
        correlation = df[['Im_Value', 'Em_Value', 'Net_Migration']].corr()
        
        return correlation.to_dict()
    
    def get_distribution_stats(self, metric='net'):
        df = self.data_service.get_all_data()
        
        metric_map = {
            'immigration': 'Im_Value',
            'emigration': 'Em_Value',
            'net': 'Net_Migration'
        }
        
        column = metric_map.get(metric, 'Net_Migration')
        
        return {
            'mean': float(df[column].mean()),
            'median': float(df[column].median()),
            'std': float(df[column].std()),
            'min': float(df[column].min()),
            'max': float(df[column].max()),
            'q25': float(df[column].quantile(0.25)),
            'q75': float(df[column].quantile(0.75))
        }

analytics_service = AnalyticsService()
