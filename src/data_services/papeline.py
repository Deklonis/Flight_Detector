
import json
from pathlib import Path

TMP_DIR = Path(__file__).resolve().parents[2] / "tmp"
RAW_PATH = TMP_DIR / "raw_json.json"
TIME_PATH = TMP_DIR / "time_json.json"
CLEAN_PATH = TMP_DIR / "flights_parquet"

def extract():
    from src.data_services.insert_data import InsertData
    TMP_DIR.mkdir(exist_ok=True)
    data = InsertData().extract_data()
    with open(RAW_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def transform():
    from src.data_services.insert_data import InsertData
    with open(RAW_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(TIME_PATH, 'w', encoding='utf-8') as t:
        json.dump(data['time'], t)
    InsertData().data_frame_normalize(data, str(CLEAN_PATH))

def load():
    from src.data_services.insert_data import InsertData
    with open(TIME_PATH, 'r', encoding='utf-8') as t:
            time = json.load(t)
    InsertData().inserttodb(path=str(CLEAN_PATH), time=time)
