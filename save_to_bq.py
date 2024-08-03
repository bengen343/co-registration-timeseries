import numpy as np
import pandas as pd
from google.cloud import storage


def create_bq_schema(df: pd.DataFrame, integer_col_lst: list) -> list:
    schema_list = []
    for column in list(df):
        if 'date' in column.lower():
            sql_type = 'DATE'
        elif column in integer_col_lst:
            sql_type = 'INT64'
        elif column == 'RTLA':
            sql_type = 'FLOAT'
        else:
            sql_type = 'STRING'
                
        if column in ['District', 'Date']:
            sql_mode = 'REQUIRED'
        else:
            sql_mode = 'NULLABLE'
            
        schema_list.append({'name':  column, 'type': sql_type, 'mode': sql_mode})
    
    return schema_list


def set_dtypes_on(df: pd.DataFrame, integer_col_lst: list) -> pd.DataFrame:
    print("Setting data types...")
    for column in list(df):
        if 'date' in column.lower():
            df[column] = pd.to_datetime(df[column], errors='coerce')
        elif column == 'RTLA':
            df[column] = pd.to_numeric(df[column], errors='coerce')
            df[column] = df[column].astype('float64')
        elif column in integer_col_lst:
            df[column] = pd.to_numeric(df[column], errors='coerce')
            df[column] = df[column].astype('float64').astype('Int64')
        else:
            df[column] = df[column].astype('str')
            
    df = df.replace('nan', np.nan)

    return df


def gcs_put(file: str, bucket_name: str, bq_project_name: str) -> str:
    client = storage.Client(project=bq_project_name)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file)
    blob.upload_from_filename(file)

    return(f"Successfully uploaded {file} to GCS Bucket {bucket_name}.")