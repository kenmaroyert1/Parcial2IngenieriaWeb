# Pokemon ETL API 🚀

API REST desarrollada con Flask que procesa datos de Pokemon usando un pipeline ETL (Extract, Transform, Load) y proporciona endpoints para consultar la información procesada.

## 📋 Descripción

Este proyecto implementa una aplicación ETL completa que:

1. **Extrae** datos del archivo Pokemon.csv (primeros 50 registros)
2. **Transforma** y limpia los datos (normalización, validación, campos calculados)
3. **Carga** los datos procesados en memoria y archivo CSV
4. **Expone** los datos a través de una API REST

## 🏗️ Arquitectura del Proyecto

```
Parcial2IngenieriaWeb/
├── Config/             # Configuración de la aplicación
│   ├── __init__.py
│   └── Config.py
├── Extract/            # Módulo de extracción de datos
│   ├── __init__.py
│   └── Extract.py
├── Clean/              # Módulo de limpieza y transformación
│   ├── __init__.py
│   └── Clean.py
├── Load/               # Módulo de carga de datos
│   ├── __init__.py
│   └── Load.py
├── Models/             # Modelos de datos (SQLAlchemy)
│   ├── __init__.py
│   └── Pokemon.py
├── Repositories/       # Capa de acceso a datos
│   ├── __init__.py
│   └── Repositories.py
├── Services/           # Lógica de negocio
│   ├── __init__.py
│   ├── Services.py
│   └── ETLService.py
├── Controllers/        # Controladores de la API
│   ├── __init__.py
│   └── Controllers.py
├── Test/              # Módulo de pruebas
│   ├── __init__.py
│   └── Test.py
├── data/              # Archivos de salida del ETL
├── main.py            # Aplicación principal (con base de datos)
├── app_simple.py      # Aplicación simplificada (en memoria)
├── Pokemon.csv        # Archivo de datos fuente
└── README.md         # Documentación
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**
- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM (opcional)
- **Pandas** - Procesamiento de datos
- **MySQL Connector** - Conexión a base de datos (opcional)

## 📦 Instalación

1. **Clonar el repositorio:**
```bash
git clone <url-del-repositorio>
cd Parcial2IngenieriaWeb
```

2. **Crear entorno virtual:**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Instalar dependencias:**
```bash
pip install flask flask-sqlalchemy mysql-connector-python pandas python-dotenv
```

4. **Verificar el archivo Pokemon.csv:**
   - Asegúrate de que el archivo `Pokemon.csv` esté en el directorio raíz

## 🚀 Ejecución

### Opción 1: Aplicación Simplificada (Recomendada)
```bash
python app_simple.py
```

### Opción 2: Aplicación con Base de Datos
```bash
python main.py
```

La API estará disponible en: `http://127.0.0.1:5000`

## 📊 Proceso ETL

### 1. Extract (Extracción)
- Lee el archivo `Pokemon.csv`
- Extrae los primeros 50 registros
- Valida la estructura de datos

### 2. Transform (Transformación)
- **Renombra columnas** al español
- **Maneja valores faltantes**
- **Limpia nombres** de Pokemon
- **Estandariza tipos**
- **Valida datos numéricos**
- **Añade campos calculados:**
  - `poder_ofensivo` = ataque + ataque_especial
  - `poder_defensivo` = defensa + defensa_especial
  - `ratio_ataque_defensa` = poder_ofensivo / poder_defensivo
  - `categoria_poder` = clasificación por poder total
- **Elimina duplicados**

### 3. Load (Carga)
- Guarda datos limpios en CSV
- Carga datos en memoria para la API
- Opcionalmente carga en base de datos

## 🌐 Endpoints de la API

### Información General
- `GET /` - Página de bienvenida y documentación

### Pokemon
- `GET /api/pokemon` - Obtener todos los Pokemon (con paginación)
- `GET /api/pokemon/<id>` - Obtener Pokemon por ID
- `GET /api/pokemon/name/<nombre>` - Obtener Pokemon por nombre
- `GET /api/pokemon/type/<tipo>` - Obtener Pokemon por tipo
- `GET /api/pokemon/search?q=<termino>` - Buscar Pokemon
- `GET /api/pokemon/legendary` - Obtener Pokemon legendarios
- `GET /api/pokemon/stats` - Obtener estadísticas generales

### ETL
- `POST /api/etl/run` - Re-ejecutar proceso ETL

## 📝 Ejemplos de Uso

### Obtener todos los Pokemon
```bash
curl http://127.0.0.1:5000/api/pokemon
```

### Obtener Pokemon por ID
```bash
curl http://127.0.0.1:5000/api/pokemon/1
```

### Buscar Pokemon por nombre
```bash
curl http://127.0.0.1:5000/api/pokemon/name/Pikachu
```

### Obtener Pokemon por tipo
```bash
curl http://127.0.0.1:5000/api/pokemon/type/Fire
```

### Buscar Pokemon
```bash
curl "http://127.0.0.1:5000/api/pokemon/search?q=char"
```

### Obtener estadísticas
```bash
curl http://127.0.0.1:5000/api/pokemon/stats
```

## 📊 Ejemplo de Respuesta

```json
{
  "pokemon": {
    "id": 1,
    "nombre": "Bulbasaur",
    "tipo_principal": "Grass",
    "tipo_secundario": "Poison",
    "hp": 45,
    "ataque": 49,
    "defensa": 49,
    "ataque_especial": 65,
    "defensa_especial": 65,
    "velocidad": 45,
    "poder_total": 318,
    "generacion": 1,
    "es_legendario": false,
    "es_mega": false,
    "forma_especial": "Forma base",
    "combinacion_tipos": "Grass/Poison",
    "poder_ofensivo": 114,
    "poder_defensivo": 114,
    "ratio_ataque_defensa": 0.991304,
    "categoria_poder": "Bajo"
  }
}
```

## 🧪 Pruebas

### Ejecutar pruebas básicas del ETL:
```bash
python Test\Test.py basic
```

### Ejecutar pruebas completas:
```bash
python Test\Test.py
```

## 📈 Características del ETL

### Calidad de Datos
- ✅ Validación de campos requeridos
- ✅ Normalización de tipos de datos
- ✅ Manejo de valores faltantes
- ✅ Detección y eliminación de duplicados
- ✅ Validación de rangos lógicos

### Transformaciones Aplicadas
- ✅ Renombrado de columnas al español
- ✅ Estandarización de tipos Pokemon
- ✅ Detección de formas especiales (Mega, etc.)
- ✅ Cálculo de métricas derivadas
- ✅ Categorización por poder

### Rendimiento
- ⚡ Procesamiento optimizado con Pandas
- ⚡ Carga de datos en memoria para API rápida
- ⚡ Paginación en endpoints
- ⚡ Procesamiento de solo 50 registros para demo

## 📁 Archivos Generados

- `data/Pokemon_clean_YYYYMMDD_HHMMSS.csv` - Datos limpios con timestamp
- `data/pokemon.db` - Base de datos SQLite (si se usa main.py)

## 🔧 Configuración

El archivo `Config/Config.py` contiene la configuración principal:

```python
class Config:
    # Rutas de archivos
    INPUT_PATH = "Pokemon.csv"
    OUTPUT_PATH = "data/Pokemon_clean.csv"
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = "sqlite:///data/pokemon.db"
```

## 🚨 Solución de Problemas

### Error: Archivo Pokemon.csv no encontrado
- Asegúrate de que el archivo esté en el directorio raíz del proyecto

### Error: Módulo no encontrado
- Verifica que el entorno virtual esté activado
- Instala las dependencias: `pip install -r requirements.txt`

### Error de base de datos
- Usa `app_simple.py` en lugar de `main.py` para evitar problemas de BD

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ve el archivo [LICENSE.md](LICENSE.md) para detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [TuGitHub](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Dataset de Pokemon utilizado para el proyecto
- Comunidad de Flask y Pandas por la documentación

---

## 📋 Checklist de Funcionalidades

- ✅ Proceso ETL completo (Extract, Transform, Load)
- ✅ API REST con múltiples endpoints
- ✅ Procesamiento de primeros 50 registros del CSV
- ✅ Limpieza y transformación de datos
- ✅ Campos calculados y métricas derivadas
- ✅ Manejo de errores y validaciones
- ✅ Documentación completa
- ✅ Pruebas automatizadas
- ✅ Estructura modular y escalable
- ✅ Configuración flexible
