import pandas as pd
import os

class Extract:
    """Clase para extraer datos del archivo CSV de Pokemon"""
    
    def __init__(self, file_path):
        """
        Inicializa el extractor con la ruta del archivo
        
        Args:
            file_path (str): Ruta al archivo CSV
        """
        self.file_path = file_path
    
    def extract_all(self):
        """
        Extrae todos los datos del archivo CSV
        
        Returns:
            pd.DataFrame: DataFrame con todos los datos o None si hay error
        """
        try:
            if not os.path.exists(self.file_path):
                print(f"❌ Error: El archivo {self.file_path} no existe")
                return None
            
            # Leer el archivo CSV
            df = pd.read_csv(self.file_path)
            print(f"📄 Archivo leído exitosamente: {len(df)} registros encontrados")
            
            return df
            
        except Exception as e:
            print(f"❌ Error al leer el archivo CSV: {str(e)}")
            return None
    
    def extract_first_n_rows(self, n=50):
        """
        Extrae los primeros n registros del archivo CSV
        
        Args:
            n (int): Número de registros a extraer (por defecto 50)
            
        Returns:
            pd.DataFrame: DataFrame con los primeros n registros o None si hay error
        """
        try:
            if not os.path.exists(self.file_path):
                print(f"❌ Error: El archivo {self.file_path} no existe")
                return None
            
            # Leer solo los primeros n registros
            df = pd.read_csv(self.file_path, nrows=n)
            print(f"📄 Primeros {n} registros extraídos exitosamente")
            
            # Mostrar información básica
            print(f"📊 Dimensiones: {df.shape}")
            print(f"📋 Columnas: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error al extraer los primeros {n} registros: {str(e)}")
            return None
    
    def get_data_info(self):
        """
        Obtiene información general sobre el archivo CSV sin cargarlo completamente
        
        Returns:
            dict: Información sobre el archivo
        """
        try:
            if not os.path.exists(self.file_path):
                return {"error": f"El archivo {self.file_path} no existe"}
            
            # Leer solo las primeras filas para obtener columnas
            sample_df = pd.read_csv(self.file_path, nrows=5)
            
            # Contar el total de líneas
            with open(self.file_path, 'r', encoding='utf-8') as f:
                total_lines = sum(1 for line in f) - 1  # -1 para excluir el header
            
            info = {
                "file_path": self.file_path,
                "total_records": total_lines,
                "columns": list(sample_df.columns),
                "sample_data": sample_df.head().to_dict('records')
            }
            
            return info
            
        except Exception as e:
            return {"error": f"Error al obtener información del archivo: {str(e)}"}
