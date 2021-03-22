"""
DB connection manager for PostgreSQL
"""
import time
import threading
import psycopg2

DB_HOST = '127.0.0.1'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'postgres'

MAX_CONNECTIONS = 2
MAX_TIME = 2


class DBPool:
    """
    DB connection pool class.
    """

    conn_pool = []

    def __init__(self):
        self.credentials = {'dbname': DB_NAME,
                            'user': DB_USER,
                            'password': DB_PASS,
                            'host': DB_HOST}
        self.max_conn = MAX_CONNECTIONS

        thread = threading.Thread(target=self.manager, args=())
        thread.daemon = True
        thread.start()

    def create_conn(self):
        """
        Creating new DB connection
        :return:
        """
        if (len(self.conn_pool) + 1) > self.max_conn:
            print("Can't create new connection: max limit have been reached.")
            return None
        try:
            conn = psycopg2.connect(**self.credentials)
            conn_obj = {'connection': conn, 'created': time.time()}
            self.conn_pool.append(conn_obj)
            print(f'Created connection object: {conn}')
            return conn_obj
        except psycopg2.OperationalError:
            print("Can't create new connection: make sure that valid credentials provided")
            return None

    def close_conn(self, conn):
        """
        Closing connection
        :param conn:
        :return:
        """
        try:
            self.conn_pool.remove(conn)
        except ValueError:
            pass
        conn['connection'].close()
        print(f'Closed connection: {conn}')

    def manager(self):
        """
        Managing connection time span
        :return:
        """
        while True:
            for conn in self.conn_pool:
                if (time.time() - conn['created']) > MAX_TIME:
                    self.close_conn(conn)
