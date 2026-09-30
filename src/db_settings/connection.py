import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

class WorkwithDB:
    def __init__(self):
        self.con = psycopg2.connect(
                    host = 'localhost',
                    port = 5435,
                    dbname = 'test_db',
                    user = 'user',
                    password = os.getenv('db_password'))
    

    def run_schemas(self):
        '''
        устанавливаем схему бд
        '''
        with open('src/db_settings/schemas/schemas.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with self.con:
            with self.con.cursor() as cur:
                cur.execute(sql)
