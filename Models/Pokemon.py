from Config.Config import db
from datetime import datetime

class Pokemon(db.Model):
    """Modelo de datos para Pokemon"""
    
    __tablename__ = 'pokemon'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    tipo_principal = db.Column(db.String(50), nullable=False)
    tipo_secundario = db.Column(db.String(50), default='Sin tipo secundario')
    
    # Estadísticas básicas
    hp = db.Column(db.Integer, nullable=False)
    ataque = db.Column(db.Integer, nullable=False)
    defensa = db.Column(db.Integer, nullable=False)
    ataque_especial = db.Column(db.Integer, nullable=False)
    defensa_especial = db.Column(db.Integer, nullable=False)
    velocidad = db.Column(db.Integer, nullable=False)
    poder_total = db.Column(db.Integer, nullable=False)
    
    # Información adicional
    generacion = db.Column(db.Integer, nullable=False)
    es_legendario = db.Column(db.Boolean, default=False)
    es_mega = db.Column(db.Boolean, default=False)
    forma_especial = db.Column(db.String(100), default='Forma base')
    combinacion_tipos = db.Column(db.String(100))
    
    # Campos calculados
    poder_ofensivo = db.Column(db.Integer)
    poder_defensivo = db.Column(db.Integer)
    ratio_ataque_defensa = db.Column(db.Float)
    categoria_poder = db.Column(db.String(20))
    
    # Metadatos
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pokemon {self.nombre} - {self.tipo_principal}>'
    
    def to_dict(self):
        """Convierte el objeto Pokemon a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo_principal': self.tipo_principal,
            'tipo_secundario': self.tipo_secundario,
            'hp': self.hp,
            'ataque': self.ataque,
            'defensa': self.defensa,
            'ataque_especial': self.ataque_especial,
            'defensa_especial': self.defensa_especial,
            'velocidad': self.velocidad,
            'poder_total': self.poder_total,
            'generacion': self.generacion,
            'es_legendario': self.es_legendario,
            'es_mega': self.es_mega,
            'forma_especial': self.forma_especial,
            'combinacion_tipos': self.combinacion_tipos,
            'poder_ofensivo': self.poder_ofensivo,
            'poder_defensivo': self.poder_defensivo,
            'ratio_ataque_defensa': self.ratio_ataque_defensa,
            'categoria_poder': self.categoria_poder,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Pokemon desde un diccionario"""
        pokemon = Pokemon()
        
        # Campos básicos
        pokemon.id = data.get('id')
        pokemon.nombre = data.get('nombre')
        pokemon.tipo_principal = data.get('tipo_principal')
        pokemon.tipo_secundario = data.get('tipo_secundario', 'Sin tipo secundario')
        
        # Estadísticas
        pokemon.hp = data.get('hp', 0)
        pokemon.ataque = data.get('ataque', 0)
        pokemon.defensa = data.get('defensa', 0)
        pokemon.ataque_especial = data.get('ataque_especial', 0)
        pokemon.defensa_especial = data.get('defensa_especial', 0)
        pokemon.velocidad = data.get('velocidad', 0)
        pokemon.poder_total = data.get('poder_total', 0)
        
        # Información adicional
        pokemon.generacion = data.get('generacion', 1)
        pokemon.es_legendario = data.get('es_legendario', False)
        pokemon.es_mega = data.get('es_mega', False)
        pokemon.forma_especial = data.get('forma_especial', 'Forma base')
        pokemon.combinacion_tipos = data.get('combinacion_tipos')
        
        # Campos calculados
        pokemon.poder_ofensivo = data.get('poder_ofensivo')
        pokemon.poder_defensivo = data.get('poder_defensivo')
        pokemon.ratio_ataque_defensa = data.get('ratio_ataque_defensa')
        pokemon.categoria_poder = data.get('categoria_poder')
        
        return pokemon
    
    def calculate_fields(self):
        """Calcula los campos derivados"""
        self.poder_ofensivo = self.ataque + self.ataque_especial
        self.poder_defensivo = self.defensa + self.defensa_especial
        self.ratio_ataque_defensa = self.poder_ofensivo / (self.poder_defensivo + 1)
        
        # Categorizar por poder total
        if self.poder_total >= 600:
            self.categoria_poder = 'Muy Alto'
        elif self.poder_total >= 500:
            self.categoria_poder = 'Alto'
        elif self.poder_total >= 400:
            self.categoria_poder = 'Medio'
        elif self.poder_total >= 300:
            self.categoria_poder = 'Bajo'
        else:
            self.categoria_poder = 'Muy Bajo'
        
        # Combinación de tipos
        if self.tipo_secundario and self.tipo_secundario != 'Sin tipo secundario':
            self.combinacion_tipos = f"{self.tipo_principal}/{self.tipo_secundario}"
        else:
            self.combinacion_tipos = self.tipo_principal
    
    def validate(self):
        """Valida los datos del Pokemon"""
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            errors.append("El nombre es requerido")
        
        if not self.tipo_principal or len(self.tipo_principal.strip()) == 0:
            errors.append("El tipo principal es requerido")
        
        if self.hp < 0:
            errors.append("HP no puede ser negativo")
        
        if self.ataque < 0:
            errors.append("Ataque no puede ser negativo")
        
        if self.defensa < 0:
            errors.append("Defensa no puede ser negativo")
        
        if self.generacion < 1:
            errors.append("La generación debe ser mayor a 0")
        
        return errors