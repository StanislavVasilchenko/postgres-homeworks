import json

import psycopg2

from config import config


def main():
    script_file = 'fill_db.sql'
    json_file = 'suppliers.json'
    db_name = 'my_new_db'

    params = config()
    conn = None

    create_database(params, db_name)
    print(f"БД {db_name} успешно создана")

    params.update({'dbname': db_name})
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                execute_sql_script(cur, script_file)
                print(f"БД {db_name} успешно заполнена")

                create_suppliers_table(cur)
                print("Таблица suppliers успешно создана")

                suppliers = get_suppliers_data(json_file)
                # print(suppliers)
                insert_suppliers_data(cur, suppliers)
                print("Данные в suppliers успешно добавлены")

                add_foreign_keys(cur, json_file)
                print(f"FOREIGN KEY успешно добавлены")

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_database(params, db_name) -> None:
    """Создает новую базу данных."""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    with conn.cursor() as cur:
        # conn.autocommit()
        cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cur.execute(f"CREATE DATABASE {db_name}")
    conn.close()


def execute_sql_script(cur, script_file) -> None:
    """Выполняет скрипт из файла для заполнения БД данными."""
    with open(script_file, "r", encoding="utf-8") as script:
        result = script.read()
    cur.execute(result)


def create_suppliers_table(cur) -> None:
    """Создает таблицу suppliers."""
    cur.execute('''CREATE TABLE suppliers(
                    supplier_id SERIAL PRIMARY KEY,
                    company_name varchar(100),
                    contact_name varchar(50),
                    contact_title varchar(50),
                    country varchar(15),
                    region varchar(20),
                    city varchar(50),
                    postal_code varchar(15),
                    address varchar(100),
                    phone varchar(20),
                    fax varchar(20),
                    homepage text
                    )
                ''')


def get_suppliers_data(json_file: str) -> list[dict]:
    """Извлекает данные о поставщиках из JSON-файла и возвращает список словарей с соответствующей информацией."""
    new_data_suppliers = []
    with open(json_file, "r", encoding="utf-8") as file:
        result = json.load(file)
    for data in result:
        sup_dict = {
            "company_name": data["company_name"],
            "contact_name": data.get("contact").split(",")[0],
            "contact_title": data.get("contact").split(",")[1].strip(),
            "country": data.get("address").split(";")[0],
            "region": data.get("address").split(";")[1].strip() if data.get("address").split(";")[1].strip() else None,
            "city": data.get("address").split(";")[3].strip(),
            "postal_code": data.get("address").split(";")[2].strip(),
            "address ": data.get("address").split(";")[-1].strip(),
            "phone": data["phone"],
            "fax": data["fax"] if data["fax"] else None,
            "homepage": data["homepage"] if data["homepage"] else None
        }
        new_data_suppliers.append(sup_dict)
    return new_data_suppliers


def insert_suppliers_data(cur, suppliers: list[dict]) -> None:
    """Добавляет данные из suppliers в таблицу suppliers."""
    values_in_dump = []
    for supplier in suppliers:
        values_in_dump = []
        for values in supplier.values():
            values_in_dump.append(values)

        cur.execute("""INSERT INTO suppliers (company_name, contact_name, contact_title,
                                            country, region, city, postal_code, address,
                                            phone, fax, homepage)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", values_in_dump)


def add_foreign_keys(cur, json_file) -> None:
    """Добавляет foreign key со ссылкой на supplier_id в таблицу products."""
    cur.execute("""ALTER TABLE products ADD COLUMN supplier_id int REFERENCES
                    suppliers(supplier_id)""")

    cur.execute("""SELECT product_name FROM products""")
    with open(json_file, "r", encoding="utf-8") as file:
        suppliers_data = json.load(file)

    for product in cur.fetchall():
        suppliers_name = get_supplier_by_product(suppliers_data, product[0])

        cur.execute("""SELECT supplier_id FROM suppliers
                    WHERE company_name=%s""", (suppliers_name,))

        supplier_id = cur.fetchone()
        update_query = "UPDATE products SET supplier_id=%s WHERE product_name=%s;"
        values = (supplier_id[0], product[0])
        cur.execute(update_query, values)


def get_supplier_by_product(suppliers_data: list[dict], product: str) -> str:
    for i in suppliers_data:
        if product in i["products"]:
            return i["company_name"]


if __name__ == '__main__':
    main()
