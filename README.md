# Flight Detector

Пайплайн для сбора данных о самолётах из API [OpenSky Network](https://opensky-network.org/). Раз в 5 минут Airflow забирает текущие данные, PySpark их очищает и нормализует, после чего они сохраняются в PostgreSQL.

Пайплайн состоит из трёх этапов (Airflow DAG `flight_detector`):

1. **extract** — получение данных из API и сохранение сырого JSON
2. **transform** — очистка и приведение типов в Spark, результат сохраняется в parquet
3. **load** — запись данных в PostgreSQL

В базе хранятся срезы API, самолёты, squawk-коды (7500, 7600, 7700 — аварийные) и состояния самолётов.

Для удобства есть две витрины: `plane_on_ground` (самолёты на земле в последнем срезе) и `emergency_situation` (аварийные ситуации) (в файле views.sql).

## Что используется

- Python
- Apache Airflow — оркестрация
- PySpark — обработка данных
- PostgreSQL 18 — хранилище
- Docker Compose
- OpenSky Network API — источник данных

## Структура проекта

```
.
├── main.py                      # создание схемы БД
├── docker-compose.yaml          # PostgreSQL
├── .env                         # db_password
├── views.sql                    # запросы для витрин
├── dags/
│   └── airf.py                  # Airflow DAG
├── tmp/                         # промежуточные файлы (raw json, parquet)
└── src/
    ├── api/
    │   └── api_client.py        # запрос к OpenSky API
    ├── data_services/
    │   ├── insert_data.py       # получение, нормализация и запись данных
    │   ├── papeline.py          # функции extract / transform / load для DAG
    │   └── sparkutil.py         # SparkSession
    └── db_settings/
        ├── connection.py        # подключение к БД
        └── schemas/
            └── schemas.sql      # схема БД
```

## Установка библиотек

```bash
pip install apache-airflow pyspark psycopg2-binary requests python-dotenv
```

## Запуск

1. Создать файл `.env` в корне проекта:

   ```
   db_password=your_password
   ```

2. Поднять PostgreSQL:

   ```bash
   docker compose up -d
   ```

3. Создать схему базы данных:

   ```bash
   python main.py
   ```

4. Запустить Airflow:

   ```bash
   airflow standalone
   ```

5. Открыть веб-интерфейс Airflow (`http://localhost:8080`) и включить DAG `flight_detector`.

Ограничения:
- Используется анонимный доступ к OpenSky API, у которого есть лимиты на частоту запросов.
