from src.db_settings.connection import WorkwithDB


if __name__ == '__main__':
    db = WorkwithDB()
    db.run_schemas()
    print('-'*10)
    print('\n'*3)
    print('Отлично! Схема базы данных готова\n' \
    'Следующий этап - запустите команду <<   airflow standalone   >>')
    print('\n'*3)
    print('-'*10)
