#import needed libraries
import os
from sqlalchemy import create_engine
import pyodbc
import pandas as pd

#get password from environment variables
pwd = '4050'  # Set this directly for demonstration purposes
uid = 'postgres'  # Set this directly for demonstration purposes
server = "localhost"
db = "Online_Retail"
port = "5432"
dir = r'C:\Users\jayja\Downloads\online+retail\file'

#extract data from sql server
def extract():
    try:
        # starting directory
        directory = dir
        # iterate over files in the directory
        for filename in os.listdir(directory):
            #get filename without ext
            file_wo_ext = os.path.splitext(filename)[0]
            # only process excel files
            if filename.endswith(".xlsx"):
                f = os.path.join(directory, filename)
                # checking if it is a file
                if os.path.isfile(f):
                    df = pd.read_excel(f)
                    # call to load
                    load(df, file_wo_ext)
    except Exception as e:
        print(f"Data extract error: {str(e)}")

#load data to postgres
def load(df, tbl):
    try:
        rows_imported = 0
        engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:{port}/{db}')
        print(f'importing rows {rows_imported} to {rows_imported + len(df)}... ')
        # save df to postgres
        df.to_sql(f"stg_{tbl}", engine, if_exists='replace', index=False)
        rows_imported += len(df)
        # add elapsed time to final print out
        print("Data imported successfully")
    except Exception as e:
        print(f"Data load error: {str(e)}")

try:
    #call extract function
    extract()
except Exception as e:
    print(f"Error while extracting data: {str(e)}")
