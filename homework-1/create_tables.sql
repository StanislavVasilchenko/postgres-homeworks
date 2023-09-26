-- SQL-команды для создания таблиц
CREATE TABLE employees
(
	employe_id int PRIMARY KEY,
	first_name varchar(30) NOT NULL,
	last_name varchar(30) NOT NULL,
	title varchar(100) NOT NULL,
	birth_day date NOT NULL,
	notes text
);

CREATE TABLE customers
(
	customer_id varchar(5) PRIMARY KEY,
	company_name varchar(30) NOT NULL,
	contact_name varchar(30) NOT NULL
);

CREATE TABLE orders
(
	order_id int PRIMARY KEY,
	customer_id varchar(5) UNIQUE REFERENCES customers(customer_id) NOT NULL,
	employe_id int UNIQUE REFERENCES employees(employe_id) NOT NULL,
	order_date date NOT NULL,
	ship_city varchar(30) NOT NULL
);