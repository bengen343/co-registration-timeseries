import pandas as pd

def load_sheet(sheet_str: str, file_name_str: str) -> pd.DataFrame:
    print("Loading xlsx file...")
    xlsx = pd.ExcelFile(file_name_str)
    
    df = pd.DataFrame()
    df = pd.read_excel(xlsx, sheet_str)
    df = df.fillna('None')
    
    # Drop the total row at the bottom of the sheet.
    df = df.drop(df.tail(1).index)

    # Look for rows that contain totals and delete the rows holding those totals.
    for col in list(df)[:5]:
        if df[col].str.lower().str.contains('total').any():
            df = df[~(df[col].str.lower().str.contains('total'))]

    # Look for columns that contain totals and delete them.
    for col in list(df)[4:]:  
        if df[col].str.lower().str.contains('total|county|district').any():
            del df[col]

    # Look for a column containing a known party and find the row it resides in.
    for col in list(df):
        if (df[col] == 'REP').any():
            title_indx = df[df[col] == 'REP'].index
    
    # There's two rows of headings. Fill the gaps in the upper heading row with values from that below.
    df.loc[title_indx[0] - 1] = df.loc[title_indx[0] - 1].fillna(df.loc[title_indx[0]])

    # Create a list of unique parties currently in existence.
    seen_st = set(df.loc[title_indx].values[0])
    party_lst = sorted([str(col) for col in seen_st if len(str(col)) == 3])

    if sheet_str == 'Party & Status':
        df.insert(loc=0, column='District', value=None)

    # Rename the columns in the sheet.
    col_lst = [f'{col}_Active' for col in party_lst] + [f'{col}_Inactive' for col in party_lst] + [f'{col}_Prereg' for col in party_lst]
    col_lst.insert(0, 'County')
    col_lst.insert(0, 'District')
    df.columns = col_lst
    
    # Drop the bad header row.
    df = df.drop(df.head(title_indx[0] + 1).index)

    # Remove any errant total rows.
    df = df[df['County'].notnull()]

    return df
