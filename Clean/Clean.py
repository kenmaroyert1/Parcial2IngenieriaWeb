import pandas as pd
import numpy as np

class Clean:
    """Clase para limpiar y transformar los datos de Pokemon"""
    
    def __init__(self, dataframe):
        """
        Inicializa el limpiador con un DataFrame
        
        Args:
            dataframe (pd.DataFrame): DataFrame con los datos a limpiar
        """
        self.df = dataframe.copy()
        self.original_shape = self.df.shape
    
    def clean_data(self):
        """
        Ejecuta todo el proceso de limpieza de datos
        
        Returns:
            pd.DataFrame: DataFrame limpio y transformado
        """
        print("🧹 Iniciando proceso de limpieza de datos...")
        
        # Ejecutar todas las funciones de limpieza
        self._clean_column_names()
        self._handle_missing_values()
        self._clean_pokemon_names()
        self._standardize_types()
        self._validate_numeric_columns()
        self._add_calculated_fields()
        self._remove_duplicates()
        
        print(f"✅ Limpieza completada:")
        print(f"   - Registros originales: {self.original_shape[0]}")
        print(f"   - Registros finales: {len(self.df)}")
        print(f"   - Columnas: {len(self.df.columns)}")
        
        return self.df
    
    def _clean_column_names(self):
        """Limpia y estandariza los nombres de las columnas"""
        print("📋 Limpiando nombres de columnas...")
        
        # Mapeo de nombres de columnas
        column_mapping = {
            '#': 'id',
            'Name': 'nombre',
            'Type 1': 'tipo_principal',
            'Type 2': 'tipo_secundario',
            'Total': 'poder_total',
            'HP': 'hp',
            'Attack': 'ataque',
            'Defense': 'defensa',
            'Sp. Atk': 'ataque_especial',
            'Sp. Def': 'defensa_especial',
            'Speed': 'velocidad',
            'Generation': 'generacion',
            'Legendary': 'es_legendario'
        }
        
        self.df = self.df.rename(columns=column_mapping)
        print(f"   ✓ Columnas renombradas: {list(self.df.columns)}")
    
    def _handle_missing_values(self):
        """Maneja los valores faltantes en el DataFrame"""
        print("🔍 Manejando valores faltantes...")
        
        # Mostrar valores faltantes antes
        missing_before = self.df.isnull().sum()
        if missing_before.sum() > 0:
            print(f"   📊 Valores faltantes encontrados:\n{missing_before[missing_before > 0]}")
        
        # Rellenar tipo_secundario con 'Sin tipo secundario'
        self.df['tipo_secundario'] = self.df['tipo_secundario'].fillna('Sin tipo secundario')
        
        # Para otros campos numéricos, rellenar con la mediana
        numeric_columns = ['hp', 'ataque', 'defensa', 'ataque_especial', 'defensa_especial', 'velocidad']
        for col in numeric_columns:
            if col in self.df.columns and self.df[col].isnull().sum() > 0:
                median_value = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_value)
                print(f"   ✓ {col}: {self.df[col].isnull().sum()} valores faltantes rellenados con mediana ({median_value})")
        
        print(f"   ✅ Valores faltantes después: {self.df.isnull().sum().sum()}")
    
    def _clean_pokemon_names(self):
        """Limpia los nombres de los Pokemon"""
        print("🔤 Limpiando nombres de Pokemon...")
        
        # Remover espacios extra
        self.df['nombre'] = self.df['nombre'].str.strip()
        
        # Separar mega evoluciones y formas especiales
        self.df['es_mega'] = self.df['nombre'].str.contains('Mega', case=False, na=False)
        self.df['forma_especial'] = self.df['nombre'].str.extract('(Mega [^\\s]+|Primal [^\\s]+|Alolan [^\\s]+)', expand=False)
        self.df['forma_especial'] = self.df['forma_especial'].fillna('Forma base')
        
        print(f"   ✓ {self.df['es_mega'].sum()} Pokemon Mega identificados")
        print(f"   ✓ Formas especiales catalogadas")
    
    def _standardize_types(self):
        """Estandariza los tipos de Pokemon"""
        print("🎯 Estandarizando tipos de Pokemon...")
        
        # Limpiar tipos
        self.df['tipo_principal'] = self.df['tipo_principal'].str.strip().str.title()
        self.df['tipo_secundario'] = self.df['tipo_secundario'].str.strip().str.title()
        
        # Crear combinación de tipos
        self.df['combinacion_tipos'] = self.df.apply(
            lambda row: row['tipo_principal'] if row['tipo_secundario'] == 'Sin Tipo Secundario' 
            else f"{row['tipo_principal']}/{row['tipo_secundario']}", axis=1
        )
        
        tipos_unicos = self.df['tipo_principal'].unique()
        print(f"   ✓ Tipos principales únicos: {len(tipos_unicos)}")
        print(f"   ✓ Tipos: {sorted(tipos_unicos)}")
    
    def _validate_numeric_columns(self):
        """Valida y corrige los datos numéricos"""
        print("🔢 Validando columnas numéricas...")
        
        numeric_columns = ['id', 'poder_total', 'hp', 'ataque', 'defensa', 
                          'ataque_especial', 'defensa_especial', 'velocidad', 'generacion']
        
        for col in numeric_columns:
            if col in self.df.columns:
                # Convertir a numérico, forzando errores a NaN
                original_nulls = self.df[col].isnull().sum()
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                new_nulls = self.df[col].isnull().sum()
                
                if new_nulls > original_nulls:
                    print(f"   ⚠️ {col}: {new_nulls - original_nulls} valores no numéricos convertidos a NaN")
                
                # Validar rangos lógicos
                if col in ['hp', 'ataque', 'defensa', 'ataque_especial', 'defensa_especial', 'velocidad']:
                    # Los stats no pueden ser negativos
                    negative_count = (self.df[col] < 0).sum()
                    if negative_count > 0:
                        self.df.loc[self.df[col] < 0, col] = 0
                        print(f"   ✓ {col}: {negative_count} valores negativos corregidos a 0")
        
        # Convertir es_legendario a booleano
        self.df['es_legendario'] = self.df['es_legendario'].astype(bool)
        
        print("   ✅ Validación numérica completada")
    
    def _add_calculated_fields(self):
        """Añade campos calculados útiles"""
        print("➕ Añadiendo campos calculados...")
        
        # Calcular stats ofensivos y defensivos
        self.df['poder_ofensivo'] = self.df['ataque'] + self.df['ataque_especial']
        self.df['poder_defensivo'] = self.df['defensa'] + self.df['defensa_especial']
        
        # Calcular ratio ataque/defensa
        self.df['ratio_ataque_defensa'] = self.df['poder_ofensivo'] / (self.df['poder_defensivo'] + 1)  # +1 para evitar división por 0
        
        # Categorizar por poder total
        def categorizar_poder(poder_total):
            if poder_total >= 600:
                return 'Muy Alto'
            elif poder_total >= 500:
                return 'Alto'
            elif poder_total >= 400:
                return 'Medio'
            elif poder_total >= 300:
                return 'Bajo'
            else:
                return 'Muy Bajo'
        
        self.df['categoria_poder'] = self.df['poder_total'].apply(categorizar_poder)
        
        print(f"   ✓ Campos calculados añadidos: poder_ofensivo, poder_defensivo, ratio_ataque_defensa, categoria_poder")
    
    def _remove_duplicates(self):
        """Elimina registros duplicados"""
        print("🔍 Eliminando duplicados...")
        
        initial_count = len(self.df)
        
        # Eliminar duplicados exactos
        self.df = self.df.drop_duplicates()
        
        # Eliminar duplicados basados en nombre (manteniendo el primero)
        duplicated_names = self.df[self.df.duplicated(subset=['nombre'], keep=False)]
        if len(duplicated_names) > 0:
            print(f"   📊 Pokemon con nombres duplicados encontrados: {len(duplicated_names)}")
            print(f"   📋 Nombres duplicados: {duplicated_names['nombre'].unique()}")
            # Mantener solo el primer registro de cada nombre
            self.df = self.df.drop_duplicates(subset=['nombre'], keep='first')
        
        final_count = len(self.df)
        removed_count = initial_count - final_count
        
        if removed_count > 0:
            print(f"   ✓ {removed_count} registros duplicados eliminados")
        else:
            print(f"   ✓ No se encontraron duplicados")
    
    def get_data_summary(self):
        """
        Genera un resumen de los datos limpios
        
        Returns:
            dict: Resumen estadístico de los datos
        """
        summary = {
            "total_pokemon": len(self.df),
            "columnas": list(self.df.columns),
            "tipos_principales": self.df['tipo_principal'].value_counts().to_dict(),
            "pokemon_legendarios": self.df['es_legendario'].sum(),
            "pokemon_mega": self.df['es_mega'].sum() if 'es_mega' in self.df.columns else 0,
            "generaciones": sorted(self.df['generacion'].unique().tolist()),
            "estadisticas_poder": {
                "promedio": round(self.df['poder_total'].mean(), 2),
                "mediana": self.df['poder_total'].median(),
                "minimo": self.df['poder_total'].min(),
                "maximo": self.df['poder_total'].max()
            }
        }
        
        return summary
