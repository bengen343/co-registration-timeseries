import gcsfs
import numpy as np
import pandas as pd
import requests

from config import *
from load_timeseries import load_sheet
from save_to_bq import create_bq_schema, set_dtypes_on

response = requests.get(statistics_url)

with open(statistics_file_str, 'wb') as xlsx_file:
    xlsx_file.write(response.content)

# Set a list of major parties to calculate grand totals for.
major_parties_lst = ['REP', 'DEM', 'UAF', 'OTH']

# Load the individual sheets for the different district types
county_df = load_sheet('Party & Status', statistics_file_str)
congressional_df = load_sheet('Congressional Districts', statistics_file_str)
state_senate_df = load_sheet('State Senate Districts', statistics_file_str)
state_house_df = load_sheet('State House Districts', statistics_file_str)

# Set column lists for columns containing numbers and certain parties.
col_lst = []
col_lst = [col for col in list(congressional_df) if col != 'County']
numeric_col_lst = [col for col in list(congressional_df) if '_' in col]
rep_col_lst = [col for col in list(congressional_df) if 'rep' in col.lower()]
dem_col_lst = [col for col in list(congressional_df) if 'dem' in col.lower()]
uaf_col_lst = [col for col in list(congressional_df) if 'uaf' in col.lower()]

# Rename the districts to align with the voter file.
county_df['District'] = county_df['County']
del county_df['County']
congressional_df['District'] = 'Congressional ' + congressional_df['District'].str[-1:].astype('int').astype('str').str.zfill(2)
state_senate_df['District'] = 'State Senate ' + state_senate_df['District'].str[-2:].astype('int').astype('str').str.zfill(2)
state_house_df['District'] = 'State House ' + state_house_df['District'].str[-2:].astype('int').astype('str').str.zfill(2)

# Calculate district totals for those districts disaggregated into counties.
congressional_df = congressional_df.groupby('District').sum().reset_index()[col_lst]
state_senate_df = state_senate_df.groupby('District').sum().reset_index()[col_lst]
state_house_df = state_house_df.groupby('District').sum().reset_index()[col_lst]

# Add a row with the statewide totals
congressional_df.loc[len(congressional_df)] = (['Colorado'] + list(congressional_df[numeric_col_lst].sum(axis=0)))

# Check to make sure we have the correct number of districts

check_tup = (
    len(congressional_df) == 9,
    len(state_senate_df) == 35,
    len(state_house_df) == 65,
    len(county_df) == 64
)
if all(check_tup):
    # Join all the different districts into one dataframe.
    registration_df = pd.concat([county_df, congressional_df, state_senate_df, state_house_df])
    
    # Calculate totals for overall, for each major party, and for minor parties.
    registration_df['TOT'] = registration_df[numeric_col_lst].sum(axis=1)
    registration_df['REP_TOT'] = registration_df[rep_col_lst].sum(axis=1)
    registration_df['DEM_TOT'] = registration_df[dem_col_lst].sum(axis=1)
    registration_df['UAF_TOT'] = registration_df[uaf_col_lst].sum(axis=1)
    registration_df['OTH_TOT'] = registration_df['TOT'] - registration_df['REP_TOT'] - registration_df['DEM_TOT'] - registration_df['UAF_TOT']
    
    # Add a column for the date
    registration_df.insert(loc=0, column='Date', value=date(int(year_str), int(last_month_str), 1))

    # Load past turnout data to calculate RTLA
    fs = gcsfs.GCSFileSystem(project=bq_project_name)

    turnout_df = pd.DataFrame()
    with fs.open(turnout_file_str) as _file:
        turnout_df = pd.read_csv(_file)

    non_flt_col_lst = [
        'Date',
        'District',
        'District_Type',
        'Year'
        'RTLA'
    ]
    for col in list(turnout_df):
        if col not in non_flt_col_lst:
            turnout_df[col] = pd.to_numeric(turnout_df[col], errors='coerce')
            turnout_df[col] = turnout_df[col].astype('float64')

    # Calculate RTLA values
    for i in registration_df.index:
        row_year_int = registration_df.loc[i, 'Date'].year
        turnout_year_int = (row_year_int - 4) + (row_year_int % 2)
    
        year_int, district_str, rep_flt, dem_flt, uaf_flt, oth_flt, tot_flt = turnout_df[(turnout_df['Year'] == turnout_year_int) & (turnout_df['District'] == registration_df.loc[i, 'District'])].iloc[0]

        cast_tot_flt = (registration_df.loc[i, 'REP_TOT'] * rep_flt) + (registration_df.loc[i, 'DEM_TOT'] * dem_flt) + (registration_df.loc[i, 'UAF_TOT'] * uaf_flt) + (registration_df.loc[i, 'OTH_TOT'] * oth_flt)
        win_tot_flt = cast_tot_flt * 0.51
        uaf_votes_flt = win_tot_flt - (registration_df.loc[i, 'REP_TOT'] * rep_flt)
        rtla_flt = uaf_votes_flt / ((registration_df.loc[i, 'UAF_TOT'] * uaf_flt) + (registration_df.loc[i, 'OTH_TOT'] * oth_flt))

        registration_df.loc[i, 'RTLA'] = rtla_flt

    # Upload the data to BigQuery.
    registration_integer_cols_lst = [col for col in list(registration_df) if col != 'District']
    registration_df = set_dtypes_on(registration_df, registration_integer_cols_lst)
    bq_schema_lst = create_bq_schema(registration_df, registration_integer_cols_lst)
    registration_df.to_gbq(destination_table=bq_timeseries_table_id, project_id=bq_project_name, if_exists='append', table_schema=bq_schema_lst, credentials=bq_credentials)

    os.remove(statistics_file_str)
