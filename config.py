import calendar
import json
import os
from datetime import date, timedelta

from google.oauth2 import service_account

# Time variables
today_dt = date.today()
year_str = str((today_dt + timedelta(-30)).year)
last_month_str = f'{((today_dt + timedelta(-30)).month):02d}'
current_month_str = f'{today_dt.month:02d}'
last_month_name_str = calendar.month_name[int(last_month_str)]

# File name variables
statistics_file_str = f'statistics.xlsx'
statistics_url = f'https://www.sos.state.co.us/pubs/elections/VoterRegNumbers/{year_str}/{last_month_name_str}/{statistics_file_str}'
turnout_file_str = r'gs://co-turnout-artifacts/co-turnout-rates.csv'

# BQ Variables
bq_project_name = os.environ.get('BQ_PROJECT_ID')
bq_project_location = 'us-west1'
bq_dataset_name = 'co_voterfile'
bq_timeseries_table_name = 'registration-timeseries'
bq_timeseries_table_id = f'{bq_project_name}.{bq_dataset_name}.{bq_timeseries_table_name}'

# Establish BigQuery credentials
bq_account_creds = json.loads(os.environ.get('BQ_ACCOUNT_CREDS'))
bq_credentials = service_account.Credentials.from_service_account_info(bq_account_creds)
