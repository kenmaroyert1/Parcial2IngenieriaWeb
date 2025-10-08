from Models.Pokemon import Pokemon
from Config.Config import db
from sqlalchemy import or_, and_

class PokemonRepository:
    """Repositorio para operaciones de acceso a datos de Pokemon"""
    
    @staticmethod
    def get_all(limit=None, offset=None):
        """
        Obtiene todos los Pokemon con paginación opcional
        
        Args:
            limit (int): Número máximo de registros a retornar
            offset (int): Número de registros a saltar
            
        Returns:
            list: Lista de Pokemon
        """
        try:
            query = Pokemon.query
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            return query.all()
        except Exception as e:
            print(f"Error al obtener todos los Pokemon: {str(e)}")
            return []
    
    @staticmethod
    def get_by_id(pokemon_id):
        """
        Obtiene un Pokemon por su ID
        
        Args:
            pokemon_id (int): ID del Pokemon
            
        Returns:
            Pokemon: Objeto Pokemon o None si no se encuentra
        """
        try:
            return Pokemon.query.get(pokemon_id)
        except Exception as e:
            print(f"Error al obtener Pokemon por ID {pokemon_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_by_name(name):
        """
        Obtiene un Pokemon por su nombre
        
        Args:
            name (str): Nombre del Pokemon
            
        Returns:
            Pokemon: Objeto Pokemon o None si no se encuentra
        """
        try:
            return Pokemon.query.filter_by(nombre=name).first()
        except Exception as e:
            print(f"Error al obtener Pokemon por nombre {name}: {str(e)}")
            return None
    
    @staticmethod
    def get_by_type(tipo, is_secondary=False):
        """
        Obtiene Pokemon por tipo
        
        Args:
            tipo (str): Tipo de Pokemon
            is_secondary (bool): Si buscar en tipo secundario
            
        Returns:
            list: Lista de Pokemon del tipo especificado
        """
        try:
            if is_secondary:
                return Pokemon.query.filter_by(tipo_secundario=tipo).all()
            else:
                return Pokemon.query.filter(
                    or_(Pokemon.tipo_principal == tipo, Pokemon.tipo_secundario == tipo)
                ).all()
        except Exception as e:
            print(f"Error al obtener Pokemon por tipo {tipo}: {str(e)}")
            return []
    
    @staticmethod
    def get_legendary(limit=None):
        """
        Obtiene Pokemon legendarios
        
        Args:
            limit (int): Número máximo de registros
            
        Returns:
            list: Lista de Pokemon legendarios
        """
        try:
            query = Pokemon.query.filter_by(es_legendario=True)
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            print(f"Error al obtener Pokemon legendarios: {str(e)}")
            return []
    
    @staticmethod
    def get_by_generation(generation):
        """
        Obtiene Pokemon por generación
        
        Args:
            generation (int): Número de generación
            
        Returns:
            list: Lista de Pokemon de la generación especificada
        """
        try:
            return Pokemon.query.filter_by(generacion=generation).all()
        except Exception as e:
            print(f"Error al obtener Pokemon de generación {generation}: {str(e)}")
            return []
    
    @staticmethod
    def search(query_text, fields=None):
        """
        Busca Pokemon por texto en múltiples campos
        
        Args:
            query_text (str): Texto a buscar
            fields (list): Lista de campos donde buscar. Por defecto busca en nombre y tipos
            
        Returns:
            list: Lista de Pokemon que coinciden con la búsqueda
        """
        try:
            if fields is None:
                fields = ['nombre', 'tipo_principal', 'tipo_secundario']
            
            search_filters = []
            query_text = f"%{query_text}%"
            
            if 'nombre' in fields:
                search_filters.append(Pokemon.nombre.like(query_text))
            if 'tipo_principal' in fields:
                search_filters.append(Pokemon.tipo_principal.like(query_text))
            if 'tipo_secundario' in fields:
                search_filters.append(Pokemon.tipo_secundario.like(query_text))
            
            return Pokemon.query.filter(or_(*search_filters)).all()
        except Exception as e:
            print(f"Error en búsqueda de Pokemon: {str(e)}")
            return []
    
    @staticmethod
    def get_by_power_range(min_power=None, max_power=None):
        """
        Obtiene Pokemon por rango de poder total
        
        Args:
            min_power (int): Poder mínimo
            max_power (int): Poder máximo
            
        Returns:
            list: Lista de Pokemon en el rango de poder especificado
        """
        try:
            query = Pokemon.query
            
            if min_power is not None:
                query = query.filter(Pokemon.poder_total >= min_power)
            if max_power is not None:
                query = query.filter(Pokemon.poder_total <= max_power)
                
            return query.all()
        except Exception as e:
            print(f"Error al obtener Pokemon por rango de poder: {str(e)}")
            return []
    
    @staticmethod
    def create(pokemon_data):
        """
        Crea un nuevo Pokemon
        
        Args:
            pokemon_data (dict): Datos del Pokemon
            
        Returns:
            Pokemon: Objeto Pokemon creado o None si hay error
        """
        try:
            pokemon = Pokemon.from_dict(pokemon_data)
            
            # Calcular campos derivados
            pokemon.calculate_fields()
            
            # Validar datos
            errors = pokemon.validate()
            if errors:
                print(f"Errores de validación: {errors}")
                return None
            
            db.session.add(pokemon)
            db.session.commit()
            
            return pokemon
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear Pokemon: {str(e)}")
            return None
    
    @staticmethod
    def update(pokemon_id, pokemon_data):
        """
        Actualiza un Pokemon existente
        
        Args:
            pokemon_id (int): ID del Pokemon a actualizar
            pokemon_data (dict): Nuevos datos del Pokemon
            
        Returns:
            Pokemon: Objeto Pokemon actualizado o None si hay error
        """
        try:
            pokemon = Pokemon.query.get(pokemon_id)
            if not pokemon:
                return None
            
            # Actualizar campos
            for key, value in pokemon_data.items():
                if hasattr(pokemon, key) and key != 'id':
                    setattr(pokemon, key, value)
            
            # Recalcular campos derivados
            pokemon.calculate_fields()
            
            # Validar datos
            errors = pokemon.validate()
            if errors:
                print(f"Errores de validación: {errors}")
                return None
            
            db.session.commit()
            return pokemon
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar Pokemon {pokemon_id}: {str(e)}")
            return None
    
    @staticmethod
    def delete(pokemon_id):
        """
        Elimina un Pokemon
        
        Args:
            pokemon_id (int): ID del Pokemon a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            pokemon = Pokemon.query.get(pokemon_id)
            if not pokemon:
                return False
            
            db.session.delete(pokemon)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar Pokemon {pokemon_id}: {str(e)}")
            return False
    
    @staticmethod
    def count():
        """
        Cuenta el total de Pokemon en la base de datos
        
        Returns:
            int: Número total de Pokemon
        """
        try:
            return Pokemon.query.count()
        except Exception as e:
            print(f"Error al contar Pokemon: {str(e)}")
            return 0
    
    @staticmethod
    def get_statistics():
        """
        Obtiene estadísticas generales de los Pokemon
        
        Returns:
            dict: Estadísticas de la base de datos
        """
        try:
            stats = {
                'total_pokemon': Pokemon.query.count(),
                'pokemon_legendarios': Pokemon.query.filter_by(es_legendario=True).count(),
                'pokemon_mega': Pokemon.query.filter_by(es_mega=True).count(),
                'generaciones': db.session.query(Pokemon.generacion).distinct().count(),
                'tipos_principales': db.session.query(Pokemon.tipo_principal).distinct().count(),
                'poder_promedio': db.session.query(db.func.avg(Pokemon.poder_total)).scalar() or 0
            }
            
            # Redondear el poder promedio
            stats['poder_promedio'] = round(stats['poder_promedio'], 2)
            
            return stats
        except Exception as e:
            print(f"Error al obtener estadísticas: {str(e)}")
            return {}
    
    @staticmethod
    def bulk_create(pokemon_list):
        """
        Crea múltiples Pokemon de una vez
        
        Args:
            pokemon_list (list): Lista de diccionarios con datos de Pokemon
            
        Returns:
            tuple: (Lista de Pokemon creados, Lista de errores)
        """
        created_pokemon = []
        errors = []
        
        try:
            for pokemon_data in pokemon_list:
                try:
                    pokemon = Pokemon.from_dict(pokemon_data)
                    pokemon.calculate_fields()
                    
                    validation_errors = pokemon.validate()
                    if validation_errors:
                        errors.append(f"Pokemon {pokemon_data.get('nombre', 'sin nombre')}: {validation_errors}")
                        continue
                    
                    db.session.add(pokemon)
                    created_pokemon.append(pokemon)
                    
                except Exception as e:
                    errors.append(f"Error con Pokemon {pokemon_data.get('nombre', 'sin nombre')}: {str(e)}")
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            errors.append(f"Error en la transacción: {str(e)}")
            created_pokemon = []
        
        return created_pokemon, errors
