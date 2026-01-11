import os
import pandas as pd
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class DataService:
    
    def __init__(self):
        self.df = None
        self._load_or_prepare_data()
    
    def _load_or_prepare_data(self):
        if os.path.exists(Config.DATASET_PROCESSED):
            logger.info("Loading processed dataset")
            self.df = self._read_csv(Config.DATASET_PROCESSED)
        else:
            logger.info("Preparing dataset from source files")
            self.df = self._prepare_migration_data()
    
    def _read_csv(self, file_path):
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully read {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            raise
    
    def _prepare_migration_data(self):
        try:
            os.makedirs('dataset', exist_ok=True)
            
            df_immigration = self._read_csv(Config.DATASET_IMMIGRATION)
            df_emigration = self._read_csv(Config.DATASET_EMIGRATION)
            
            # clean data
            df_immigration = df_immigration.drop(columns=[
                'DATAFLOW', 'LAST UPDATE', 'freq', 'citizen', 'agedef', 
                'age', 'unit', 'sex', 'OBS_FLAG', 'CONF_STATUS'
            ], errors='ignore')
            df_immigration = df_immigration.rename(columns={
                'geo': 'Country',
                'TIME_PERIOD': 'Year',
                'OBS_VALUE': 'Im_Value'
            })
            
            df_emigration = df_emigration.drop(columns=[
                'DATAFLOW', 'LAST UPDATE', 'freq', 'citizen', 'agedef',
                'age', 'unit', 'sex', 'OBS_FLAG', 'CONF_STATUS'
            ], errors='ignore')
            df_emigration = df_emigration.rename(columns={
                'geo': 'Country',
                'TIME_PERIOD': 'Year',
                'OBS_VALUE': 'Em_Value'
            })
            
            # merge datasets
            df_merged = pd.merge(
                df_immigration, 
                df_emigration, 
                on=['Country', 'Year'], 
                how='inner'
            )
            
            #  net migration
            df_merged['Net_Migration'] = df_merged['Im_Value'] - df_merged['Em_Value']
            
            #  duplicates and EU27_2020 
            df_merged = df_merged.drop_duplicates(subset=['Country', 'Year'])
            df_merged = df_merged[df_merged['Country'] != 'EU27_2020']
            
            # map to ISO-3166-1 alpha-3 codes
            country_mapping = {
                'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'CH': 'CHE', 'CY': 'CYP',
                'CZ': 'CZE', 'DE': 'DEU', 'DK': 'DNK', 'EE': 'EST', 'EL': 'GRC',
                'ES': 'ESP', 'FI': 'FIN', 'FR': 'FRA', 'GE': 'GEO', 'HR': 'HRV',
                'HU': 'HUN', 'IE': 'IRL', 'IS': 'ISL', 'IT': 'ITA', 'LI': 'LIE',
                'LT': 'LTU', 'LU': 'LUX', 'LV': 'LVA', 'MD': 'MDA', 'ME': 'MNE',
                'MK': 'MKD', 'MT': 'MLT', 'NL': 'NLD', 'NO': 'NOR', 'PL': 'POL',
                'PT': 'PRT', 'RO': 'ROU', 'SE': 'SWE', 'SI': 'SVN', 'SK': 'SVK',
                'TR': 'TUR', 'UK': 'GBR'
            }
            
            df_merged['Country'] = df_merged['Country'].map(country_mapping)
            df_merged = df_merged.dropna(subset=['Country'])
            
            # save processed data
            df_merged.to_csv(Config.DATASET_PROCESSED, index=False)
            logger.info(f"Processed data saved to {Config.DATASET_PROCESSED}")
            
            return df_merged
            
        except Exception as e:
            logger.error(f"Error preparing migration data: {str(e)}")
            raise
    
    def get_all_data(self):
        if self.df is None or self.df.empty:
            raise ValueError("No data available")
        return self.df
    
    def filter_data(self, countries=None, start_year=None, end_year=None, year=None):
        df = self.df.copy()
        
        if year:
            df = df[df['Year'] == year]
        else:
            if start_year:
                df = df[df['Year'] >= start_year]
            if end_year:
                df = df[df['Year'] <= end_year]
        
        if countries:
            df = df[df['Country'].isin(countries)]
        
        return df
    
    def get_country_summary(self, country_code):
        df = self.df[self.df['Country'] == country_code]
        
        if df.empty:
            return None
        
        return {
            'country': country_code,
            'years_available': [int(df['Year'].min()), int(df['Year'].max())],
            'total_immigration': int(df['Im_Value'].sum()),
            'total_emigration': int(df['Em_Value'].sum()),
            'total_net_migration': int(df['Net_Migration'].sum()),
            'avg_immigration': float(df['Im_Value'].mean()),
            'avg_emigration': float(df['Em_Value'].mean()),
            'avg_net_migration': float(df['Net_Migration'].mean())
        }
    
    def get_year_summary(self, year):
        df = self.df[self.df['Year'] == year]
        
        if df.empty:
            return None
        
        return {
            'year': year,
            'countries_count': len(df),
            'total_immigration': int(df['Im_Value'].sum()),
            'total_emigration': int(df['Em_Value'].sum()),
            'total_net_migration': int(df['Net_Migration'].sum()),
            'top_immigration': df.nlargest(5, 'Im_Value')[['Country', 'Im_Value']].to_dict('records'),
            'top_emigration': df.nlargest(5, 'Em_Value')[['Country', 'Em_Value']].to_dict('records')
        }
    
    def get_available_countries(self):
        return sorted(self.df['Country'].unique().tolist())
    
    def get_available_years(self):
        return sorted(self.df['Year'].unique().tolist())
    
    def get_statistics(self):
        return {
            'total_records': len(self.df),
            'countries_count': self.df['Country'].nunique(),
            'years_range': [int(self.df['Year'].min()), int(self.df['Year'].max())],
            'total_immigration': int(self.df['Im_Value'].sum()),
            'total_emigration': int(self.df['Em_Value'].sum()),
            'total_net_migration': int(self.df['Net_Migration'].sum())
        }

data_service = DataService()