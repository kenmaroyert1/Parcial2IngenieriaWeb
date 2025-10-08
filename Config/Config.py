import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Inicialización de la base de datos
db = SQLAlchemy()

class Config:
    """Configuración para el proceso ETL y la API"""
    
    # Rutas de archivos
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_PATH = os.path.join(BASE_DIR, "Pokemon.csv")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "Pokemon_clean.csv")
    
    # Configuración de la base de datos MySQL (opcional)
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DATABASE = "pokemon_db"
    MYSQL_TABLE = "pokemon"
    
    # Configuración de Flask y SQLAlchemy (usando SQLite para simplicidad)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pokemon-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "data", "pokemon.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la API
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

def init_db(app):
    """Inicializa la base de datos con la aplicación Flask"""
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {str(e)}")
