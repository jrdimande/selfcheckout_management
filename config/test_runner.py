from django.db import connections
from django.test.runner import DiscoverRunner

DDL = """
CREATE TABLE customer (uuid varchar(100) PRIMARY KEY, name varchar(100) NOT NULL, balance decimal NOT NULL DEFAULT 0);
CREATE TABLE product (uuid varchar(100) PRIMARY KEY, name varchar(150) NOT NULL, price decimal NOT NULL,
  stock integer NOT NULL DEFAULT 0, minimum_stock integer NOT NULL DEFAULT 5);
CREATE TABLE sale (id integer PRIMARY KEY AUTOINCREMENT, customer_uuid varchar(100) NOT NULL,
  sale_date datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, total decimal NOT NULL);
CREATE TABLE sale_item (id integer PRIMARY KEY AUTOINCREMENT, sale_id integer NOT NULL, product_uuid varchar(100) NOT NULL,
  quantity integer NOT NULL DEFAULT 1, unit_price decimal NOT NULL, subtotal decimal NOT NULL);
CREATE TABLE payment (id integer PRIMARY KEY AUTOINCREMENT, sale_id integer NOT NULL, amount decimal NOT NULL,
  payment_method varchar(50) NOT NULL);
"""


class SchemaRunner(DiscoverRunner):
    """Os testes correm em SQLite em memória (nunca no MySQL real): cria as tabelas do schema.sql."""

    def setup_databases(self, **kwargs):
        config = super().setup_databases(**kwargs)
        conn = connections["selfcheckout"]
        conn.ensure_connection()
        conn.connection.executescript(DDL)
        return config
