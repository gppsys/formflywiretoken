import pyodbc
from flask import current_app, g

def get_db_connection():
    """
    Obtiene una conexión a la base de datos SQL Server.
    """
    if 'db' not in g:
        connection_string = (
            f"DRIVER={current_app.config['DB_DRIVER']};"
            f"SERVER={current_app.config['DB_SERVER']};"
            f"DATABASE={current_app.config['DB_DATABASE']};"
            f"UID={current_app.config['DB_USERNAME']};"
            f"PWD={current_app.config['DB_PASSWORD']}"
        )
        g.db = pyodbc.connect(connection_string)
    return g.db

def close_db_connection(e=None):
    """
    Cierra la conexión a la base de datos SQL Server si está abierta.
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except pyodbc.ProgrammingError:
            # La conexión ya está cerrada, no es necesario hacer nada
            pass

def init_db():
    """
    Inicializa la base de datos creando las tablas necesarias si no existen.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='transactions' AND xtype='U')
        CREATE TABLE transactions (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id NVARCHAR(255) NOT NULL,
            payor_id NVARCHAR(255) NOT NULL,
            token NVARCHAR(255),
            mandate NVARCHAR(MAX)
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")
