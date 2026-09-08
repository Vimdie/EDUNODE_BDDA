import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'd8f4b2a9e3c79015bd6a8f11c52b49e8a71d8f3b2a9e3c'
    
    # SQL Server Database settings
    # Adapt with your actual SQL Server details
    SQL_SERVER = os.environ.get('SQL_SERVER') or '.\\BDD2_PROJET'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'BDD2_Projet'
    # Use Windows Authentication by default if UID/PWD are not set, otherwise SQL Authentication
    SQL_UID = os.environ.get('SQL_UID') or 'UserFlask'
    SQL_PWD = os.environ.get('SQL_PWD') or 'ISE2_2026'
    
    @staticmethod
    def get_connection_string():
        if Config.SQL_UID and Config.SQL_PWD:
            # SQL Authentication
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={Config.SQL_SERVER};DATABASE={Config.SQL_DATABASE};UID={Config.SQL_UID};PWD={Config.SQL_PWD}"
        else:
            # Windows Authentication
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={Config.SQL_SERVER};DATABASE={Config.SQL_DATABASE};Trusted_Connection=yes;"
