import pyodbc
from config import Config

def get_db_connection():
    """
    Etablit et retourne une connexion à la base de données SQL Server.
    """
    try:
        conn = pyodbc.connect(Config.get_connection_string())
        return conn
    except pyodbc.Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None
