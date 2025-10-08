from flask import Blueprint, request, jsonify
from Services.Services import PokemonService

# Crear el blueprint para las rutas de Pokemon
pokemon_blueprint = Blueprint('pokemon', __name__)

@pokemon_blueprint.route('/pokemon', methods=['GET'])
def get_all_pokemon():
    """
    Obtiene todos los Pokemon con paginación y filtros opcionales
    
    Query parameters:
    - page: número de página (default: 1)
    - per_page: registros por página (default: 20, max: 100)
    - type: filtrar por tipo
    - generation: filtrar por generación
    - legendary: filtrar legendarios (true/false)
    - search: búsqueda por nombre
    """
    try:
        # Obtener parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Filtros
        tipo = request.args.get('type')
        generacion = request.args.get('generation')
        legendario = request.args.get('legendary')
        busqueda = request.args.get('search')
        
        # Si hay filtros específicos, usar servicios especializados
        if busqueda:
            result = PokemonService.search_pokemon(busqueda)
            return jsonify(result), 200
        
        if tipo:
            result = PokemonService.get_pokemon_by_type(tipo)
            return jsonify(result), 200
        
        if legendario and legendario.lower() == 'true':
            result = PokemonService.get_legendary_pokemon()
            return jsonify(result), 200
        
        # Obtener todos con paginación
        result = PokemonService.get_all_pokemon(page, per_page)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': 'Parámetros de paginación inválidos'}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/<int:pokemon_id>', methods=['GET'])
def get_pokemon_by_id(pokemon_id):
    """
    Obtiene un Pokemon específico por su ID
    
    Args:
        pokemon_id (int): ID del Pokemon
    """
    try:
        result = PokemonService.get_pokemon_by_id(pokemon_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon', methods=['POST'])
def create_pokemon():
    """
    Crea un nuevo Pokemon
    
    Body JSON requerido:
    {
        "nombre": "string (requerido)",
        "tipo_principal": "string (requerido)",
        "tipo_secundario": "string (opcional)",
        "hp": "integer (requerido)",
        "ataque": "integer (requerido)",
        "defensa": "integer (requerido)",
        "ataque_especial": "integer (opcional)",
        "defensa_especial": "integer (opcional)",
        "velocidad": "integer (opcional)",
        "generacion": "integer (opcional, default: 1)",
        "es_legendario": "boolean (opcional, default: false)"
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        pokemon_data = request.get_json()
        
        if not pokemon_data:
            return jsonify({'error': 'Body JSON requerido'}), 400
        
        # Validar datos antes de crear
        validation = PokemonService.validate_pokemon_data(pokemon_data)
        if not validation['is_valid']:
            return jsonify({
                'error': 'Datos inválidos',
                'validation_errors': validation['errors'],
                'warnings': validation['warnings']
            }), 400
        
        result = PokemonService.create_pokemon(pokemon_data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/<int:pokemon_id>', methods=['PUT'])
def update_pokemon(pokemon_id):
    """
    Actualiza un Pokemon existente
    
    Args:
        pokemon_id (int): ID del Pokemon a actualizar
        
    Body JSON con los campos a actualizar
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        pokemon_data = request.get_json()
        
        if not pokemon_data:
            return jsonify({'error': 'Body JSON requerido'}), 400
        
        # Validar datos antes de actualizar
        validation = PokemonService.validate_pokemon_data(pokemon_data)
        if validation['errors']:  # Solo errores, las advertencias son permitidas en actualizaciones
            return jsonify({
                'error': 'Datos inválidos',
                'validation_errors': validation['errors']
            }), 400
        
        result = PokemonService.update_pokemon(pokemon_id, pokemon_data)
        
        if 'error' in result:
            return jsonify(result), 404 if 'no encontrado' in result['error'] else 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/<int:pokemon_id>', methods=['DELETE'])
def delete_pokemon(pokemon_id):
    """
    Elimina un Pokemon
    
    Args:
        pokemon_id (int): ID del Pokemon a eliminar
    """
    try:
        result = PokemonService.delete_pokemon(pokemon_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/search', methods=['GET'])
def search_pokemon():
    """
    Busca Pokemon por diferentes criterios
    
    Query parameters:
    - q: término de búsqueda (requerido)
    - type: tipo de búsqueda ('all', 'name', 'type', 'generation')
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        
        if not query:
            return jsonify({'error': 'Parámetro de búsqueda "q" requerido'}), 400
        
        valid_search_types = ['all', 'name', 'type', 'generation']
        if search_type not in valid_search_types:
            return jsonify({
                'error': f'Tipo de búsqueda inválido. Valores válidos: {", ".join(valid_search_types)}'
            }), 400
        
        result = PokemonService.search_pokemon(query, search_type)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/types/<string:tipo>', methods=['GET'])
def get_pokemon_by_type(tipo):
    """
    Obtiene Pokemon por tipo específico
    
    Args:
        tipo (str): Tipo de Pokemon (ej: Fire, Water, Grass)
    """
    try:
        result = PokemonService.get_pokemon_by_type(tipo.title())
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/legendary', methods=['GET'])
def get_legendary_pokemon():
    """
    Obtiene todos los Pokemon legendarios
    """
    try:
        result = PokemonService.get_legendary_pokemon()
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/power', methods=['GET'])
def get_pokemon_by_power():
    """
    Obtiene Pokemon por rango de poder
    
    Query parameters:
    - min: poder mínimo
    - max: poder máximo
    """
    try:
        min_power = request.args.get('min')
        max_power = request.args.get('max')
        
        # Convertir a enteros si están presentes
        if min_power:
            try:
                min_power = int(min_power)
            except ValueError:
                return jsonify({'error': 'El parámetro "min" debe ser un número entero'}), 400
        
        if max_power:
            try:
                max_power = int(max_power)
            except ValueError:
                return jsonify({'error': 'El parámetro "max" debe ser un número entero'}), 400
        
        if min_power is not None and max_power is not None and min_power > max_power:
            return jsonify({'error': 'El poder mínimo no puede ser mayor al máximo'}), 400
        
        result = PokemonService.get_pokemon_by_power_range(min_power, max_power)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/statistics', methods=['GET'])
def get_pokemon_statistics():
    """
    Obtiene estadísticas generales de los Pokemon
    """
    try:
        result = PokemonService.get_pokemon_statistics()
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@pokemon_blueprint.route('/pokemon/validate', methods=['POST'])
def validate_pokemon_data():
    """
    Valida datos de Pokemon sin crear el registro
    
    Body JSON con los datos a validar
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        pokemon_data = request.get_json()
        
        if not pokemon_data:
            return jsonify({'error': 'Body JSON requerido'}), 400
        
        result = PokemonService.validate_pokemon_data(pokemon_data)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

# Manejadores de errores específicos para el blueprint
@pokemon_blueprint.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@pokemon_blueprint.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Método no permitido'}), 405

@pokemon_blueprint.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500
