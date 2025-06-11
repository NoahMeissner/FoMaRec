#@Noah Meissner 14.05.2025
import mysql.connector
from tqdm import tqdm
import pandas as pd
from dotenv import load_dotenv
import os

def get_raw():
    load_dotenv()
    cnx = mysql.connector.connect(host=os.getenv('HOST'),
                                  port=3306,
                                  user=os.getenv('USER'),
                                  password=os.getenv('PWD'))
    
    cursor = cnx.cursor()
    cursor.execute("USE kochbar")
    
    cursor.execute("SELECT COUNT(*) FROM kochbar_recipes")
    total_rows = cursor.fetchone()[0]
    
    batch_size = 1000
    data = []
    
    with tqdm(total=total_rows, desc="Fetching data") as pbar:
        for offset in range(0, total_rows, batch_size):
            cursor.execute(
                f"SELECT * FROM kochbar_recipes LIMIT {batch_size} OFFSET {offset}"
            )
            batch = cursor.fetchall()
            data.extend(batch)
            pbar.update(len(batch))  
    
    col_names = [i[0] for i in cursor.description]
    df = pd.DataFrame(data, columns=col_names)
    
    cursor.close()
    cnx.close()
    return df
