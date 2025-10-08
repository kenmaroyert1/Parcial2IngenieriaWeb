from Config.Config import Config
from Extract.Extract import Extract
from Clean.Clean import Clean
from Load.Load import Load
import time
from flask import Flask, jsonify, request
import pandas as pd
import os

# Variable global para almacenar los datos procesados
pokemon_data = None

def run_etl():
    """Ejecuta el proceso ETL y devuelve los datos procesados"""
    global pokemon_data
    
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
            
            # Almacenar los datos procesados en memoria
            pokemon_data = df_clean.to_dict('records')
            
            return True

        else:
            print("❌ Error: No se pudieron extraer los datos")
            return False

    except Exception as e:
        print(f"\n❌ Error en el proceso ETL: {str(e)}")
        return False

def create_app():
    """Crea la aplicación Flask"""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # Ruta de bienvenida
    @app.route('/')
    def welcome():
        return jsonify({
            "mensaje": "¡Bienvenido a la API de Pokémon ETL!",
            "versión": "1.0",
            "descripción": "API REST para consultar datos de Pokemon procesados mediante ETL",
            "datos_fuente": "Pokemon.csv (primeros 50 registros)",
            "rutas_disponibles": {
                "GET /": "Página de bienvenida",
                "GET /api/pokemon": "Obtener todos los pokémons",
                "GET /api/pokemon/<id>": "Obtener un pokémon específico por ID",
                "GET /api/pokemon/name/<nombre>": "Obtener un pokémon por nombre",
                "GET /api/pokemon/type/<tipo>": "Obtener pokémons por tipo",
                "GET /api/pokemon/search?q=<termino>": "Buscar pokémons",
                "GET /api/pokemon/stats": "Obtener estadísticas generales",
                "GET /api/pokemon/legendary": "Obtener pokémons legendarios"
            },
            "estadísticas": {
                "total_pokemon": len(pokemon_data) if pokemon_data else 0,
                "etl_ejecutado": pokemon_data is not None
            }
        }), 200

    # Rutas de la API
    @app.route('/api/pokemon')
    def get_all_pokemon():
        """Obtiene todos los Pokemon"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles. Ejecute el ETL primero."}), 500
        
        # Paginación
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_data = pokemon_data[start_idx:end_idx]
        
        return jsonify({
            "pokemon": paginated_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": len(pokemon_data),
                "pages": (len(pokemon_data) + per_page - 1) // per_page,
                "has_next": end_idx < len(pokemon_data),
                "has_prev": page > 1
            }
        }), 200

    @app.route('/api/pokemon/<int:pokemon_id>')
    def get_pokemon_by_id(pokemon_id):
        """Obtiene un Pokemon por ID"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles"}), 500
        
        pokemon = next((p for p in pokemon_data if p['id'] == pokemon_id), None)
        if pokemon:
            return jsonify({"pokemon": pokemon}), 200
        else:
            return jsonify({"error": f"Pokemon con ID {pokemon_id} no encontrado"}), 404

    @app.route('/api/pokemon/name/<string:nombre>')
    def get_pokemon_by_name(nombre):
        """Obtiene un Pokemon por nombre"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles"}), 500
        
        pokemon = next((p for p in pokemon_data if p['nombre'].lower() == nombre.lower()), None)
        if pokemon:
            return jsonify({"pokemon": pokemon}), 200
        else:
            return jsonify({"error": f"Pokemon '{nombre}' no encontrado"}), 404

    @app.route('/api/pokemon/type/<string:tipo>')
    def get_pokemon_by_type(tipo):
        """Obtiene Pokemon por tipo"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles"}), 500
        
        tipo = tipo.title()
        filtered_pokemon = [
            p for p in pokemon_data 
            if p['tipo_principal'] == tipo or p['tipo_secundario'] == tipo
        ]
        
        return jsonify({
            "pokemon": filtered_pokemon,
            "total": len(filtered_pokemon),
            "tipo_buscado": tipo
        }), 200

    @app.route('/api/pokemon/search')
    def search_pokemon():
        """Busca Pokemon por término"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles"}), 500
        
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({"error": "Parámetro 'q' requerido"}), 400
        
        filtered_pokemon = [
            p for p in pokemon_data 
            if query in p['nombre'].lower() or 
               query in p['tipo_principal'].lower() or 
               query in str(p['tipo_secundario']).lower()
        ]
        
        return jsonify({
            "pokemon": filtered_pokemon,
            "total": len(filtered_pokemon),
            "termino_busqueda": query
        }), 200

    @app.route('/api/pokemon/legendary')
    def get_legendary_pokemon():
        """Obtiene Pokemon legendarios"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles"}), 500
        
        legendary_pokemon = [p for p in pokemon_data if p['es_legendario']]
        
        return jsonify({
            "pokemon": legendary_pokemon,
            "total": len(legendary_pokemon)
        }), 200

    @app.route('/api/pokemon/stats')
    def get_pokemon_stats():
        """Obtiene estadísticas generales"""
        if not pokemon_data:
            return jsonify({"error": "No hay datos disponibles"}), 500
        
        df = pd.DataFrame(pokemon_data)
        
        # Calcular estadísticas
        stats = {
            "total_pokemon": len(pokemon_data),
            "pokemon_legendarios": df['es_legendario'].sum(),
            "pokemon_mega": df['es_mega'].sum(),
            "tipos_principales": df['tipo_principal'].value_counts().to_dict(),
            "distribución_por_generacion": df['generacion'].value_counts().sort_index().to_dict(),
            "distribución_por_categoria_poder": df['categoria_poder'].value_counts().to_dict(),
            "estadisticas_poder": {
                "promedio": round(df['poder_total'].mean(), 2),
                "mediana": df['poder_total'].median(),
                "maximo": df['poder_total'].max(),
                "minimo": df['poder_total'].min(),
                "desviacion_estandar": round(df['poder_total'].std(), 2)
            },
            "top_5_mas_poderosos": df.nlargest(5, 'poder_total')[['nombre', 'poder_total']].to_dict('records'),
            "pokemon_mas_rapido": {
                "nombre": df.loc[df['velocidad'].idxmax(), 'nombre'],
                "velocidad": int(df['velocidad'].max())
            },
            "pokemon_mas_resistente": {
                "nombre": df.loc[df['hp'].idxmax(), 'nombre'],
                "hp": int(df['hp'].max())
            }
        }
        
        return jsonify(stats), 200

    # Ruta para re-ejecutar ETL
    @app.route('/api/etl/run', methods=['POST'])
    def run_etl_endpoint():
        """Re-ejecuta el proceso ETL"""
        success = run_etl()
        if success:
            return jsonify({
                "mensaje": "ETL ejecutado exitosamente",
                "total_pokemon": len(pokemon_data) if pokemon_data else 0
            }), 200
        else:
            return jsonify({"error": "Error al ejecutar ETL"}), 500

    # Manejadores de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500

    return app

if __name__ == '__main__':
    print("🚀 Iniciando aplicación Pokemon ETL API...")
    
    # Ejecutar el proceso ETL al inicio
    etl_success = run_etl()
    
    if etl_success:
        print(f"\n✅ ETL completado. Datos de {len(pokemon_data)} Pokemon cargados en memoria.")
    else:
        print("\n❌ Error en ETL. La API funcionará con datos limitados.")
    
    # Crear y ejecutar la aplicación Flask
    app = create_app()
    print("\n🌐 Iniciando servidor API en http://127.0.0.1:5000")
    print("📋 Visita http://127.0.0.1:5000 para ver la documentación de la API")
    
    app.run(debug=True, host='127.0.0.1', port=5000)