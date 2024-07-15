import psycopg2
import os



class PostgreSQL:
    def __init__(self, dbname, user, password, host, port,schema=None):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.schema = schema
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host, port=self.port)
            self.cursor = self.connection.cursor()
            print("Successfully connected to PostgreSQL")
        except (Exception, psycopg2.Error) as error:
            print("Error connecting to PostgreSQL:", error)

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error executing query:", error)

    def execute_query_with_params(self, query,params):
        try:
            self.cursor.execute(query,params)
            self.connection.commit()
            print("Query executed successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error executing query:", error)
            
    def execute_query_with_return(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            print("Query executed successfully")
            return result
        except (Exception, psycopg2.Error) as error:
            print("Error executing query:", error)

# Create an instance of the PostgreSQL class
postgres = PostgreSQL(dbname=os.environ.get('DJANGO_DATABASE_NAME'), user=os.environ.get('DJANGO_DATABASE_USER'), password=os.environ.get('DJANGO_DATABASE_PASSWORD'), host=os.environ.get('DJANGO_DATABASE_HOST'), port=os.environ.get('DJANGO_DATABASE_PORT'),schema=os.environ.get('DJANGO_DATABASE_SCHEMA'))

