"""Скрипт для заполнения данными таблиц в БД Postgres."""
import csv
import psycopg2
import os

password = os.getenv("PASSWORD")


class ReadFromFileCSV:

    def __init__(self, file_name):
        self.file_name = file_name
        self.data = self.csv_reader()

    def csv_reader(self):
        with open(self.file_name, "r") as csv_file:
            data = csv.reader(csv_file)
            next(data)
            data_list = [data_row for data_row in data]
        return data_list


employee = ReadFromFileCSV("north_data/employees_data.csv")
customers = ReadFromFileCSV("north_data/customers_data.csv")
orders = ReadFromFileCSV("north_data/orders_data.csv")

conn_params = {
    "host": "localhost",
    "database": "north",
    "user": "postgres",
    "password": password
}
try:
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            for data_employee in employee.data:
                cur.execute("INSERT INTO employees VALUES (%s, %s, %s, %s, %s, %s)", data_employee)

            for data_customer in customers.data:
                cur.execute("INSERT INTO customers VALUES (%s, %s, %s)", data_customer)

            for data_order in orders.data:
                cur.execute("INSERT INTO orders VALUES (%s, %s, %s, %s, %s)", data_order)
finally:
    conn.close()
