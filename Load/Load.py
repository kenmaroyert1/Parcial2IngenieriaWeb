import pandas as pd
import os
from datetime import datetime

class Load:
    """Clase para cargar los datos limpios a diferentes destinos"""
    
    def __init__(self, dataframe):
        """
        Inicializa el cargador con un DataFrame limpio
        
        Args:
            dataframe (pd.DataFrame): DataFrame con los datos limpios
        """
        self.df = dataframe.copy()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def to_csv(self, output_path, include_timestamp=True):
        """
        Guarda los datos en un archivo CSV
        
        Args:
            output_path (str): Ruta donde guardar el archivo
            include_timestamp (bool): Si incluir timestamp en el nombre del archivo
            
        Returns:
            str: Ruta del archivo guardado
        """
        try:
            # Modificar el nombre del archivo si se incluye timestamp
            if include_timestamp:
                base_name = os.path.splitext(output_path)[0]
                extension = os.path.splitext(output_path)[1]
                output_path = f"{base_name}_{self.timestamp}{extension}"
            
            # Crear el directorio si no existe
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Guardar el CSV
            self.df.to_csv(output_path, index=False, encoding='utf-8')
            
            file_size = os.path.getsize(output_path)
            print(f"✅ CSV guardado exitosamente:")
            print(f"   📁 Archivo: {output_path}")
            print(f"   📊 Registros: {len(self.df)}")
            print(f"   💾 Tamaño: {file_size} bytes")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error al guardar CSV: {str(e)}")
            return None
    
    def to_json(self, output_path, include_timestamp=True):
        """
        Guarda los datos en un archivo JSON
        
        Args:
            output_path (str): Ruta donde guardar el archivo
            include_timestamp (bool): Si incluir timestamp en el nombre del archivo
            
        Returns:
            str: Ruta del archivo guardado
        """
        try:
            # Modificar el nombre del archivo si se incluye timestamp
            if include_timestamp:
                base_name = os.path.splitext(output_path)[0]
                extension = os.path.splitext(output_path)[1]
                output_path = f"{base_name}_{self.timestamp}{extension}"
            
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Guardar el JSON
            self.df.to_json(output_path, orient='records', indent=2, force_ascii=False)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ JSON guardado exitosamente:")
            print(f"   📁 Archivo: {output_path}")
            print(f"   📊 Registros: {len(self.df)}")
            print(f"   💾 Tamaño: {file_size} bytes")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error al guardar JSON: {str(e)}")
            return None
    
    def to_excel(self, output_path, include_timestamp=True, sheet_name='Pokemon'):
        """
        Guarda los datos en un archivo Excel
        
        Args:
            output_path (str): Ruta donde guardar el archivo
            include_timestamp (bool): Si incluir timestamp en el nombre del archivo
            sheet_name (str): Nombre de la hoja de Excel
            
        Returns:
            str: Ruta del archivo guardado
        """
        try:
            # Modificar el nombre del archivo si se incluye timestamp
            if include_timestamp:
                base_name = os.path.splitext(output_path)[0]
                extension = os.path.splitext(output_path)[1]
                output_path = f"{base_name}_{self.timestamp}{extension}"
            
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Guardar el Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                self.df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ Excel guardado exitosamente:")
            print(f"   📁 Archivo: {output_path}")
            print(f"   📊 Registros: {len(self.df)}")
            print(f"   📋 Hoja: {sheet_name}")
            print(f"   💾 Tamaño: {file_size} bytes")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error al guardar Excel: {str(e)}")
            return None
    
    def to_mysql(self, connection_config=None):
        """
        Carga los datos a una base de datos MySQL
        
        Args:
            connection_config (dict): Configuración de conexión a MySQL
            
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario
        """
        try:
            import mysql.connector
            from sqlalchemy import create_engine
            
            if connection_config is None:
                from Config.Config import Config
                connection_config = {
                    'host': Config.MYSQL_HOST,
                    'user': Config.MYSQL_USER,
                    'password': Config.MYSQL_PASSWORD,
                    'database': Config.MYSQL_DATABASE,
                    'table': Config.MYSQL_TABLE
                }
            
            # Crear la conexión con SQLAlchemy
            engine = create_engine(
                f"mysql+mysqlconnector://{connection_config['user']}:{connection_config['password']}"
                f"@{connection_config['host']}/{connection_config['database']}"
            )
            
            # Cargar los datos
            self.df.to_sql(
                name=connection_config['table'],
                con=engine,
                if_exists='replace',  # Reemplazar la tabla si existe
                index=False,
                method='multi'
            )
            
            print(f"✅ Datos cargados exitosamente a MySQL:")
            print(f"   🗄️ Base de datos: {connection_config['database']}")
            print(f"   📋 Tabla: {connection_config['table']}")
            print(f"   📊 Registros: {len(self.df)}")
            
            return True
            
        except ImportError:
            print("❌ Error: mysql-connector-python y sqlalchemy son requeridos para cargar a MySQL")
            print("💡 Instala con: pip install mysql-connector-python sqlalchemy")
            return False
        except Exception as e:
            print(f"❌ Error al cargar datos a MySQL: {str(e)}")
            return False
    
    def get_load_summary(self):
        """
        Genera un resumen de los datos a cargar
        
        Returns:
            dict: Resumen de los datos
        """
        summary = {
            "timestamp": self.timestamp,
            "total_records": len(self.df),
            "columns": list(self.df.columns),
            "data_types": self.df.dtypes.to_dict(),
            "memory_usage": f"{self.df.memory_usage(deep=True).sum()} bytes",
            "sample_records": self.df.head(3).to_dict('records')
        }
        
        return summary
    
    def validate_data_integrity(self):
        """
        Valida la integridad de los datos antes de cargar
        
        Returns:
            dict: Resultado de la validación
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Verificar que no haya registros vacíos
        if self.df.empty:
            validation["is_valid"] = False
            validation["issues"].append("El DataFrame está vacío")
            return validation
        
        # Verificar campos requeridos
        required_fields = ['id', 'nombre', 'tipo_principal']
        for field in required_fields:
            if field not in self.df.columns:
                validation["is_valid"] = False
                validation["issues"].append(f"Campo requerido faltante: {field}")
            elif self.df[field].isnull().any():
                validation["warnings"].append(f"Campo {field} tiene valores nulos")
        
        # Verificar duplicados en ID
        if self.df['id'].duplicated().any():
            validation["warnings"].append("IDs duplicados encontrados")
        
        # Verificar tipos de datos
        numeric_fields = ['id', 'hp', 'ataque', 'defensa']
        for field in numeric_fields:
            if field in self.df.columns and not pd.api.types.is_numeric_dtype(self.df[field]):
                validation["warnings"].append(f"Campo {field} no es numérico")
        
        print(f"🔍 Validación de integridad:")
        print(f"   ✅ Válido: {validation['is_valid']}")
        if validation["issues"]:
            print(f"   ❌ Problemas: {len(validation['issues'])}")
        if validation["warnings"]:
            print(f"   ⚠️ Advertencias: {len(validation['warnings'])}")
        
        return validation
