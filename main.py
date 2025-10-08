from Config.Config import Config, init_db
from Extract.Extract import Extract
from Clean.Clean import Clean
from Load.Load import Load
from Services.ETLService import ETLService
import time
from flask import Flask, jsonify
from Controllers.Controllers import pokemon_blueprint

def run_etl():
    try:
        print("\n🚀 Iniciando proceso ETL para datos Pokemon...")
        start_time = time.time()

        # Extract
        print("\n📥 Fase de Extracción:")
        print(f"Leyendo datos desde: {Config.INPUT_PATH}")
        extractor = Extract(Config.INPUT_PATH)
        df = extractor.extract_first_n_rows(50)  # Solo los primeros 50 registros

        if df is not None:
            print(f"✅ Datos extraídos exitosamente. Registros encontrados: {len(df)}")

            # Transform/Clean
            print("\n🔄 Fase de Limpieza y Transformación:")
            print("Limpiando y preparando los datos...")
            cleaner = Clean(df)
            df_clean = cleaner.clean_data()
            
            print("\n📊 Resumen de datos limpios:")
            print(f"- Total de registros: {len(df_clean)}")
            print(f"- Columnas: {', '.join(df_clean.columns)}")
            print("\nPrimeros 5 registros:")
            print(df_clean.head())

            # Load
            print("\n📤 Fase de Carga:")
            loader = Load(df_clean)
            
            # Guardar en CSV
            print("\n💾 Guardando datos en CSV...")
            csv_path = loader.to_csv(Config.OUTPUT_PATH)
            
            # Resumen final
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            print(f"\n✨ Proceso ETL completado exitosamente en {duration} segundos")
            print(f"📁 CSV guardado en: {csv_path}")
            
            return csv_path

        else:
            print("❌ Error: No se pudieron extraer los datos")
            return None

    except Exception as e:
        print(f"\n❌ Error en el proceso ETL: {str(e)}")
        return None

def create_app():
    app = Flask(__name__)

    # Inicializar la base de datos
    init_db(app)

    # Ruta de bienvenida
    @app.route('/')
    def welcome():
        return jsonify({
            "mensaje": "¡Bienvenido a la API de Pokémon!",
            "versión": "1.0",
            "rutas_disponibles": {
                "GET /": "Página de bienvenida",
                "GET /api/pokemon": "Obtener todos los pokémons",
                "GET /api/pokemon/<id>": "Obtener un pokémon específico",
                "POST /api/pokemon": "Crear un nuevo pokémon",
                "PUT /api/pokemon/<id>": "Actualizar un pokémon existente",
                "DELETE /api/pokemon/<id>": "Eliminar un pokémon"
            },
            "formato_json": {
                "crear_actualizar": {
                    "nombre": "string (requerido)",
                    "tipo": "string (requerido)",
                    "nivel": "integer (requerido, positivo)",
                    "poder_ataque": "float (requerido)",
                    "poder_defensa": "float (requerido)",
                    "hp": "integer (requerido, positivo)",
                    "descripcion": "string (opcional)"
                }
            }
        }), 200

    # Registrar los blueprints
    app.register_blueprint(pokemon_blueprint, url_prefix='/api')

    return app

if __name__ == '__main__':
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        # Ejecutar el proceso ETL primero
        csv_path = run_etl()
        
        if csv_path:
            # Cargar datos a la base de datos
            print("\n🗄️ Cargando datos a la base de datos...")
            result = ETLService.load_pokemon_from_csv(csv_path)
            
            if result['success']:
                print(f"✅ Base de datos cargada con {result['created_count']} Pokemon")
            else:
                print(f"❌ Error al cargar base de datos: {result.get('error', 'Error desconocido')}")
        
        print("\n🚀 Iniciando servidor de la API...")
    
    # Iniciar la API Flask
    app.run(debug=True)
