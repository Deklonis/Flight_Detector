import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
from airflow.sdk import DAG, task
from src.data_services import papeline


with DAG(
    dag_id='flight_detector',
    schedule='*/5 * * * *',
    start_date=datetime(2026, 9, 28),
    catchup=False,
    tags=['flights'],
    max_active_runs=1,) as dag:


    @task
    def extract():
        papeline.extract()
        return


    @task
    def transform():
        papeline.transform()
        return

    @task
    def load():
        papeline.load()
        return


    extract() >> transform() >> load()

