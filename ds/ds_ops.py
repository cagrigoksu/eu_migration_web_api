# CGU
import os
import pandas as pd

def check_file_exist():
    file_path = 'dataset/estat_migration.csv'

    if os.path.exists(file_path):
        print(f"File '{file_path}' exists.")
        return True
    else:
        print(f"File '{file_path}' does not exist. Preparing file...")
        return False   
        
# read csv file
def read_csv_file(file):
    
    try:
        df = pd.read_csv(file)
        print(f"Successfully read {file}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

    return df

# delete columns from df
def delete_columns(df, columns_to_delete):
    try:
        df = df.drop(columns=columns_to_delete, errors='ignore')
        return df
    except Exception as e:
        print(f"Error deleting columns: {e}")
        return df

# rename columns
def rename_columns(df, new_column_names):
    try:
        df = df.rename(columns=new_column_names)
        return df
    except Exception as e:
        print(f"Error renaming columns: {e}")
        return df
    
# merge dfs    
def merge_dataframes(df1, df2, on_columns):
    try:
        df_merged = pd.merge(df1, df2, on=on_columns, how='inner')
        
        # calculate net immigration
        df_merged["Net_Migration"] = df_merged["Im_Value"] - df_merged["Em_Value"]
        return df_merged
    except Exception as e:
        print(f"Error merging dataframes: {e}")
        return None   

def prepare_migrations_file():
    
    # Read the data from the CSV files into dataframes
    df_eu_immigration = read_csv_file('dataset/estat_tps00176_en.csv') 
    df_eu_emigration = read_csv_file('dataset/estat_tps00177_en.csv') 

    # delete unnecessary columns from dfs and rename
    if df_eu_immigration is not None:
        df_eu_immigration = delete_columns(df_eu_immigration, ['DATAFLOW', 'LAST UPDATE', 'freq', 'citizen', 'agedef', 'age', 'unit', 'sex', 'OBS_FLAG', 'CONF_STATUS'])
        df_eu_immigration = rename_columns(df_eu_immigration, {"geo": "Country", "TIME_PERIOD": "Year", "OBS_VALUE": "Im_Value"})
        
    if df_eu_emigration is not None:
        df_eu_emigration = delete_columns(df_eu_emigration, ['DATAFLOW', 'LAST UPDATE', 'freq', 'citizen', 'agedef', 'age', 'unit', 'sex', 'OBS_FLAG', 'CONF_STATUS'])
        df_eu_emigration = rename_columns(df_eu_emigration, {"geo": "Country", "TIME_PERIOD": "Year", "OBS_VALUE": "Em_Value"})

    # Merge the two dataframes into a single dataframe, handling potential duplicates
    if df_eu_immigration is not None and df_eu_emigration is not None:
        df_eu_migration = merge_dataframes(df_eu_immigration, df_eu_emigration, ["Country", "Year"])
        df_eu_migration = df_eu_migration.drop_duplicates(subset=["Country", "Year"])
        # Remove rows where country_code is 'EU27_2020'
        df_eu_migration = df_eu_migration.loc[df_eu_migration['Country'] != 'EU27_2020']
    
    # ISO-3166-1 alpha-3 formatting
    country_mapping = {
    'AT': 'AUT',
    'BE': 'BEL',
    'BG': 'BGR',
    'CH': 'CHE',
    'CY': 'CYP',
    'CZ': 'CZE',
    'DE': 'DEU',
    'DK': 'DNK',
    'EE': 'EST',
    'EL': 'GRC',  
    'ES': 'ESP',
    'FI': 'FIN',
    'FR': 'FRA',
    'GE': 'GEO',  
    'HR': 'HRV',
    'HU': 'HUN',
    'IE': 'IRL',
    'IS': 'ISL',
    'IT': 'ITA',
    'LI': 'LIE',
    'LT': 'LTU',
    'LU': 'LUX',
    'LV': 'LVA',
    'MD': 'MDA',
    'ME': 'MNE',
    'MK': 'MKD',
    'MT': 'MLT',
    'NL': 'NLD',
    'NO': 'NOR',
    'PL': 'POL',
    'PT': 'PRT',
    'RO': 'ROU',
    'SE': 'SWE',
    'SI': 'SVN',
    'SK': 'SVK',
    'TR': 'TUR',
    'UK': 'GBR'  
    }

    df_eu_migration['Country'] = df_eu_migration['Country'].map(country_mapping)
    
    file_path = 'dataset/estat_migration.csv'

    # Save the DataFrame to the CSV file
    df_eu_migration.to_csv(file_path, index=False)

    print(f"DataFrame saved to {file_path}")
   
    return df_eu_migration
        
def get_dataframe():
    
    df_eu_migration = read_csv_file('dataset/estat_migration.csv') 
   
    return df_eu_migration

