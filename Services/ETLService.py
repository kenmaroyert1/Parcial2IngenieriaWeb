import pandas as pd
from Models.Pokemon import Pokemon
from Config.Config import db

class ETLService:
    """Servicio para cargar datos del ETL a la base de datos"""
    
    @staticmethod
    def load_pokemon_from_csv(csv_path):
        """
        Carga Pokemon desde un archivo CSV limpio a la base de datos
        
        Args:
            csv_path (str): Ruta al archivo CSV limpio
            
        Returns:
            dict: Resultado de la carga
        """
        try:
            # Leer el archivo CSV limpio
            df = pd.read_csv(csv_path)
            
            print(f"📄 Leyendo datos limpios desde: {csv_path}")
            print(f"📊 Registros encontrados: {len(df)}")
            
            # Limpiar la tabla existente
            Pokemon.query.delete()
            db.session.commit()
            
            # Cargar cada Pokemon
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Crear el objeto Pokemon
                    pokemon = Pokemon()
                    
                    # Asignar campos básicos
                    pokemon.id = int(row['id'])
                    pokemon.nombre = str(row['nombre'])
                    pokemon.tipo_principal = str(row['tipo_principal'])
                    pokemon.tipo_secundario = str(row['tipo_secundario'])
                    
                    # Estadísticas
                    pokemon.hp = int(row['hp'])
                    pokemon.ataque = int(row['ataque'])
                    pokemon.defensa = int(row['defensa'])
                    pokemon.ataque_especial = int(row['ataque_especial'])
                    pokemon.defensa_especial = int(row['defensa_especial'])
                    pokemon.velocidad = int(row['velocidad'])
                    pokemon.poder_total = int(row['poder_total'])
                    
                    # Información adicional
                    pokemon.generacion = int(row['generacion'])
                    pokemon.es_legendario = bool(row['es_legendario'])
                    pokemon.es_mega = bool(row['es_mega'])
                    pokemon.forma_especial = str(row['forma_especial'])
                    pokemon.combinacion_tipos = str(row['combinacion_tipos'])
                    
                    # Campos calculados
                    pokemon.poder_ofensivo = int(row['poder_ofensivo'])
                    pokemon.poder_defensivo = int(row['poder_defensivo'])
                    pokemon.ratio_ataque_defensa = float(row['ratio_ataque_defensa'])
                    pokemon.categoria_poder = str(row['categoria_poder'])
                    
                    # Agregar a la sesión
                    db.session.add(pokemon)
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Error en registro {index + 1} ({row.get('nombre', 'sin nombre')}): {str(e)}")
            
            # Commit de todos los cambios
            db.session.commit()
            
            print(f"✅ Datos cargados a la base de datos:")
            print(f"   📊 Pokemon creados: {created_count}")
            if errors:
                print(f"   ❌ Errores: {len(errors)}")
                for error in errors[:5]:  # Mostrar solo los primeros 5 errores
                    print(f"      - {error}")
            
            return {
                'success': True,
                'created_count': created_count,
                'error_count': len(errors),
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error al cargar datos a la base de datos: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }