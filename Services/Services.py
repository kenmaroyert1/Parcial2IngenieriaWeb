from Repositories.Repositories import PokemonRepository
import pandas as pd

class PokemonService:
    """Servicio de lógica de negocio para Pokemon"""
    
    @staticmethod
    def get_all_pokemon(page=1, per_page=20):
        """
        Obtiene todos los Pokemon con paginación
        
        Args:
            page (int): Número de página
            per_page (int): Registros por página
            
        Returns:
            dict: Datos paginados y metadatos
        """
        try:
            offset = (page - 1) * per_page
            pokemon_list = PokemonRepository.get_all(limit=per_page, offset=offset)
            total_count = PokemonRepository.count()
            
            return {
                'pokemon': [pokemon.to_dict() for pokemon in pokemon_list],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page,
                    'has_next': page * per_page < total_count,
                    'has_prev': page > 1
                }
            }
        except Exception as e:
            return {'error': f'Error al obtener Pokemon: {str(e)}'}
    
    @staticmethod
    def get_pokemon_by_id(pokemon_id):
        """
        Obtiene un Pokemon específico por ID
        
        Args:
            pokemon_id (int): ID del Pokemon
            
        Returns:
            dict: Datos del Pokemon o mensaje de error
        """
        try:
            pokemon = PokemonRepository.get_by_id(pokemon_id)
            if pokemon:
                return {'pokemon': pokemon.to_dict()}
            else:
                return {'error': f'Pokemon con ID {pokemon_id} no encontrado'}
        except Exception as e:
            return {'error': f'Error al obtener Pokemon: {str(e)}'}
    
    @staticmethod
    def create_pokemon(pokemon_data):
        """
        Crea un nuevo Pokemon
        
        Args:
            pokemon_data (dict): Datos del Pokemon
            
        Returns:
            dict: Pokemon creado o mensaje de error
        """
        try:
            # Validar datos requeridos
            required_fields = ['nombre', 'tipo_principal', 'hp', 'ataque', 'defensa']
            missing_fields = [field for field in required_fields if field not in pokemon_data]
            
            if missing_fields:
                return {'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}
            
            # Verificar que no exista un Pokemon con el mismo nombre
            existing_pokemon = PokemonRepository.get_by_name(pokemon_data['nombre'])
            if existing_pokemon:
                return {'error': f'Ya existe un Pokemon con el nombre "{pokemon_data["nombre"]}"'}
            
            pokemon = PokemonRepository.create(pokemon_data)
            if pokemon:
                return {'pokemon': pokemon.to_dict(), 'message': 'Pokemon creado exitosamente'}
            else:
                return {'error': 'Error al crear el Pokemon'}
                
        except Exception as e:
            return {'error': f'Error al crear Pokemon: {str(e)}'}
    
    @staticmethod
    def update_pokemon(pokemon_id, pokemon_data):
        """
        Actualiza un Pokemon existente
        
        Args:
            pokemon_id (int): ID del Pokemon
            pokemon_data (dict): Nuevos datos del Pokemon
            
        Returns:
            dict: Pokemon actualizado o mensaje de error
        """
        try:
            # Verificar que el Pokemon existe
            existing_pokemon = PokemonRepository.get_by_id(pokemon_id)
            if not existing_pokemon:
                return {'error': f'Pokemon con ID {pokemon_id} no encontrado'}
            
            # Si se está cambiando el nombre, verificar que no exista otro con el mismo nombre
            if 'nombre' in pokemon_data and pokemon_data['nombre'] != existing_pokemon.nombre:
                duplicate_pokemon = PokemonRepository.get_by_name(pokemon_data['nombre'])
                if duplicate_pokemon:
                    return {'error': f'Ya existe un Pokemon con el nombre "{pokemon_data["nombre"]}"'}
            
            pokemon = PokemonRepository.update(pokemon_id, pokemon_data)
            if pokemon:
                return {'pokemon': pokemon.to_dict(), 'message': 'Pokemon actualizado exitosamente'}
            else:
                return {'error': 'Error al actualizar el Pokemon'}
                
        except Exception as e:
            return {'error': f'Error al actualizar Pokemon: {str(e)}'}
    
    @staticmethod
    def delete_pokemon(pokemon_id):
        """
        Elimina un Pokemon
        
        Args:
            pokemon_id (int): ID del Pokemon
            
        Returns:
            dict: Mensaje de éxito o error
        """
        try:
            # Verificar que el Pokemon existe
            existing_pokemon = PokemonRepository.get_by_id(pokemon_id)
            if not existing_pokemon:
                return {'error': f'Pokemon con ID {pokemon_id} no encontrado'}
            
            success = PokemonRepository.delete(pokemon_id)
            if success:
                return {'message': f'Pokemon "{existing_pokemon.nombre}" eliminado exitosamente'}
            else:
                return {'error': 'Error al eliminar el Pokemon'}
                
        except Exception as e:
            return {'error': f'Error al eliminar Pokemon: {str(e)}'}
    
    @staticmethod
    def search_pokemon(query, search_type='all'):
        """
        Busca Pokemon según diferentes criterios
        
        Args:
            query (str): Término de búsqueda
            search_type (str): Tipo de búsqueda ('all', 'name', 'type', 'generation')
            
        Returns:
            dict: Resultados de la búsqueda
        """
        try:
            pokemon_list = []
            
            if search_type == 'all' or search_type == 'name':
                pokemon_list.extend(PokemonRepository.search(query, ['nombre']))
            
            if search_type == 'all' or search_type == 'type':
                pokemon_list.extend(PokemonRepository.get_by_type(query))
            
            if search_type == 'generation' and query.isdigit():
                pokemon_list.extend(PokemonRepository.get_by_generation(int(query)))
            
            # Eliminar duplicados manteniendo el orden
            unique_pokemon = []
            seen_ids = set()
            for pokemon in pokemon_list:
                if pokemon.id not in seen_ids:
                    unique_pokemon.append(pokemon)
                    seen_ids.add(pokemon.id)
            
            return {
                'pokemon': [pokemon.to_dict() for pokemon in unique_pokemon],
                'total_found': len(unique_pokemon),
                'search_query': query,
                'search_type': search_type
            }
            
        except Exception as e:
            return {'error': f'Error en la búsqueda: {str(e)}'}
    
    @staticmethod
    def get_pokemon_by_type(tipo):
        """
        Obtiene Pokemon por tipo
        
        Args:
            tipo (str): Tipo de Pokemon
            
        Returns:
            dict: Lista de Pokemon del tipo especificado
        """
        try:
            pokemon_list = PokemonRepository.get_by_type(tipo)
            return {
                'pokemon': [pokemon.to_dict() for pokemon in pokemon_list],
                'total': len(pokemon_list),
                'type': tipo
            }
        except Exception as e:
            return {'error': f'Error al obtener Pokemon por tipo: {str(e)}'}
    
    @staticmethod
    def get_legendary_pokemon():
        """
        Obtiene todos los Pokemon legendarios
        
        Returns:
            dict: Lista de Pokemon legendarios
        """
        try:
            pokemon_list = PokemonRepository.get_legendary()
            return {
                'pokemon': [pokemon.to_dict() for pokemon in pokemon_list],
                'total': len(pokemon_list)
            }
        except Exception as e:
            return {'error': f'Error al obtener Pokemon legendarios: {str(e)}'}
    
    @staticmethod
    def get_pokemon_statistics():
        """
        Obtiene estadísticas generales de los Pokemon
        
        Returns:
            dict: Estadísticas completas
        """
        try:
            basic_stats = PokemonRepository.get_statistics()
            
            # Obtener estadísticas adicionales
            all_pokemon = PokemonRepository.get_all()
            
            if all_pokemon:
                df = pd.DataFrame([pokemon.to_dict() for pokemon in all_pokemon])
                
                additional_stats = {
                    'tipos_principales': df['tipo_principal'].value_counts().to_dict(),
                    'distribución_por_generacion': df['generacion'].value_counts().sort_index().to_dict(),
                    'distribución_por_categoria_poder': df['categoria_poder'].value_counts().to_dict(),
                    'estadisticas_poder': {
                        'promedio': df['poder_total'].mean(),
                        'mediana': df['poder_total'].median(),
                        'maximo': df['poder_total'].max(),
                        'minimo': df['poder_total'].min(),
                        'desviacion_estandar': df['poder_total'].std()
                    },
                    'top_5_mas_poderosos': df.nlargest(5, 'poder_total')[['nombre', 'poder_total']].to_dict('records'),
                    'pokemon_mas_rapido': df.loc[df['velocidad'].idxmax(), ['nombre', 'velocidad']].to_dict(),
                    'pokemon_mas_resistente': df.loc[df['hp'].idxmax(), ['nombre', 'hp']].to_dict()
                }
                
                # Redondear valores numéricos
                additional_stats['estadisticas_poder'] = {
                    k: round(v, 2) if isinstance(v, float) else v
                    for k, v in additional_stats['estadisticas_poder'].items()
                }
                
                basic_stats.update(additional_stats)
            
            return basic_stats
            
        except Exception as e:
            return {'error': f'Error al obtener estadísticas: {str(e)}'}
    
    @staticmethod
    def get_pokemon_by_power_range(min_power=None, max_power=None):
        """
        Obtiene Pokemon por rango de poder
        
        Args:
            min_power (int): Poder mínimo
            max_power (int): Poder máximo
            
        Returns:
            dict: Lista de Pokemon en el rango especificado
        """
        try:
            pokemon_list = PokemonRepository.get_by_power_range(min_power, max_power)
            return {
                'pokemon': [pokemon.to_dict() for pokemon in pokemon_list],
                'total': len(pokemon_list),
                'filters': {
                    'min_power': min_power,
                    'max_power': max_power
                }
            }
        except Exception as e:
            return {'error': f'Error al obtener Pokemon por rango de poder: {str(e)}'}
    
    @staticmethod
    def load_pokemon_from_csv(csv_data):
        """
        Carga Pokemon desde datos CSV (para el ETL)
        
        Args:
            csv_data (list): Lista de diccionarios con datos de Pokemon
            
        Returns:
            dict: Resultado de la carga masiva
        """
        try:
            created_pokemon, errors = PokemonRepository.bulk_create(csv_data)
            
            return {
                'created_count': len(created_pokemon),
                'error_count': len(errors),
                'errors': errors,
                'message': f'Se crearon {len(created_pokemon)} Pokemon exitosamente'
            }
            
        except Exception as e:
            return {'error': f'Error en la carga masiva: {str(e)}'}
    
    @staticmethod
    def validate_pokemon_data(pokemon_data):
        """
        Valida los datos de un Pokemon antes de crear/actualizar
        
        Args:
            pokemon_data (dict): Datos del Pokemon
            
        Returns:
            dict: Resultado de la validación
        """
        try:
            errors = []
            warnings = []
            
            # Validar campos requeridos
            required_fields = ['nombre', 'tipo_principal', 'hp', 'ataque', 'defensa']
            for field in required_fields:
                if field not in pokemon_data or pokemon_data[field] is None:
                    errors.append(f'Campo requerido faltante: {field}')
                elif field == 'nombre' and len(str(pokemon_data[field]).strip()) == 0:
                    errors.append('El nombre no puede estar vacío')
            
            # Validar tipos de datos
            numeric_fields = ['hp', 'ataque', 'defensa', 'ataque_especial', 'defensa_especial', 'velocidad']
            for field in numeric_fields:
                if field in pokemon_data:
                    try:
                        value = int(pokemon_data[field])
                        if value < 0:
                            errors.append(f'{field} no puede ser negativo')
                        elif value > 255:
                            warnings.append(f'{field} es muy alto ({value}), el máximo típico es 255')
                    except (ValueError, TypeError):
                        errors.append(f'{field} debe ser un número entero')
            
            # Validar generación
            if 'generacion' in pokemon_data:
                try:
                    gen = int(pokemon_data['generacion'])
                    if gen < 1 or gen > 9:
                        warnings.append(f'Generación {gen} está fuera del rango típico (1-9)')
                except (ValueError, TypeError):
                    errors.append('La generación debe ser un número entero')
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'Error en la validación: {str(e)}'],
                'warnings': []
            }
