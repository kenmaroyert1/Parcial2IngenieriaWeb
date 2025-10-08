import pandas as pd
import os
import sys
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Config.Config import Config
from Extract.Extract import Extract
from Clean.Clean import Clean
from Load.Load import Load

class TestETL:
    """Clase para probar el proceso ETL con los primeros 50 registros"""
    
    def __init__(self):
        self.test_results = {
            'extract': False,
            'clean': False,
            'load': False,
            'errors': [],
            'warnings': []
        }
        self.start_time = datetime.now()
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas del proceso ETL"""
        print("🧪 Iniciando pruebas del proceso ETL...")
        print("=" * 60)
        
        # Test de extracción
        self.test_extract()
        
        # Si la extracción es exitosa, continuar con limpieza
        if self.test_results['extract']:
            self.test_clean()
        
        # Si la limpieza es exitosa, continuar con carga
        if self.test_results['clean']:
            self.test_load()
        
        # Mostrar resumen
        self.show_summary()
    
    def test_extract(self):
        """Prueba el módulo de extracción"""
        print("\n📥 Probando módulo de Extracción...")
        
        try:
            # Verificar que el archivo existe
            if not os.path.exists(Config.INPUT_PATH):
                self.test_results['errors'].append(f"Archivo CSV no encontrado: {Config.INPUT_PATH}")
                print(f"❌ Error: Archivo CSV no encontrado")
                return
            
            # Crear extractor
            extractor = Extract(Config.INPUT_PATH)
            
            # Obtener información del archivo
            info = extractor.get_data_info()
            if 'error' in info:
                self.test_results['errors'].append(f"Error al obtener info del archivo: {info['error']}")
                print(f"❌ Error al obtener información del archivo")
                return
            
            print(f"✅ Archivo encontrado: {info['total_records']} registros totales")
            print(f"📋 Columnas: {info['columns']}")
            
            # Extraer primeros 50 registros
            df = extractor.extract_first_n_rows(50)
            
            if df is None:
                self.test_results['errors'].append("Error al extraer datos del CSV")
                print("❌ Error al extraer datos")
                return
            
            # Validaciones
            if len(df) != 50:
                self.test_results['warnings'].append(f"Se esperaban 50 registros, se obtuvieron {len(df)}")
            
            required_columns = ['#', 'Name', 'Type 1', 'HP', 'Attack', 'Defense']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.test_results['errors'].append(f"Columnas faltantes: {missing_columns}")
                print(f"❌ Columnas faltantes: {missing_columns}")
                return
            
            self.df_extracted = df
            self.test_results['extract'] = True
            print(f"✅ Extracción exitosa: {len(df)} registros, {len(df.columns)} columnas")
            
        except Exception as e:
            self.test_results['errors'].append(f"Error en extracción: {str(e)}")
            print(f"❌ Error en extracción: {str(e)}")
    
    def test_clean(self):
        """Prueba el módulo de limpieza"""
        print("\n🧹 Probando módulo de Limpieza...")
        
        try:
            # Crear limpiador
            cleaner = Clean(self.df_extracted)
            
            # Ejecutar limpieza
            df_clean = cleaner.clean_data()
            
            if df_clean is None or df_clean.empty:
                self.test_results['errors'].append("Error: DataFrame limpio está vacío")
                print("❌ Error: DataFrame limpio está vacío")
                return
            
            # Validaciones después de la limpieza
            expected_columns = ['id', 'nombre', 'tipo_principal', 'hp', 'ataque', 'defensa']
            missing_columns = [col for col in expected_columns if col not in df_clean.columns]
            if missing_columns:
                self.test_results['errors'].append(f"Columnas esperadas faltantes después de limpieza: {missing_columns}")
                print(f"❌ Columnas faltantes después de limpieza: {missing_columns}")
                return
            
            # Verificar que no hay valores nulos en columnas críticas
            critical_columns = ['id', 'nombre', 'tipo_principal']
            for col in critical_columns:
                if col in df_clean.columns and df_clean[col].isnull().any():
                    self.test_results['warnings'].append(f"Valores nulos encontrados en columna crítica: {col}")
            
            # Verificar tipos de datos
            numeric_columns = ['id', 'hp', 'ataque', 'defensa']
            for col in numeric_columns:
                if col in df_clean.columns and not pd.api.types.is_numeric_dtype(df_clean[col]):
                    self.test_results['warnings'].append(f"Columna {col} no es numérica después de limpieza")
            
            # Obtener resumen de limpieza
            summary = cleaner.get_data_summary()
            print(f"✅ Limpieza exitosa:")
            print(f"   - Pokemon procesados: {summary['total_pokemon']}")
            print(f"   - Tipos únicos: {len(summary['tipos_principales'])}")
            print(f"   - Pokemon legendarios: {summary['pokemon_legendarios']}")
            
            self.df_clean = df_clean
            self.test_results['clean'] = True
            
        except Exception as e:
            self.test_results['errors'].append(f"Error en limpieza: {str(e)}")
            print(f"❌ Error en limpieza: {str(e)}")
    
    def test_load(self):
        """Prueba el módulo de carga"""
        print("\n📤 Probando módulo de Carga...")
        
        try:
            # Crear cargador
            loader = Load(self.df_clean)
            
            # Validar integridad de datos
            validation = loader.validate_data_integrity()
            if not validation['is_valid']:
                for issue in validation['issues']:
                    self.test_results['errors'].append(f"Problema de integridad: {issue}")
                print("❌ Problemas de integridad de datos")
                return
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    self.test_results['warnings'].append(f"Advertencia de integridad: {warning}")
            
            # Probar guardado en CSV
            test_csv_path = Config.OUTPUT_PATH.replace('.csv', '_test.csv')
            csv_result = loader.to_csv(test_csv_path, include_timestamp=False)
            
            if csv_result:
                print(f"✅ CSV guardado exitosamente en: {csv_result}")
                
                # Verificar que el archivo se creó y tiene contenido
                if os.path.exists(csv_result):
                    file_size = os.path.getsize(csv_result)
                    if file_size > 0:
                        print(f"   📊 Tamaño del archivo: {file_size} bytes")
                    else:
                        self.test_results['warnings'].append("El archivo CSV está vacío")
                else:
                    self.test_results['errors'].append("El archivo CSV no se creó correctamente")
                    return
            else:
                self.test_results['errors'].append("Error al guardar CSV")
                return
            
            # Probar guardado en JSON (opcional)
            try:
                test_json_path = test_csv_path.replace('.csv', '.json')
                json_result = loader.to_json(test_json_path, include_timestamp=False)
                if json_result:
                    print(f"✅ JSON guardado exitosamente en: {json_result}")
                else:
                    self.test_results['warnings'].append("No se pudo guardar en formato JSON")
            except Exception as e:
                self.test_results['warnings'].append(f"Error al guardar JSON: {str(e)}")
            
            # Obtener resumen de carga
            summary = loader.get_load_summary()
            print(f"✅ Carga exitosa:")
            print(f"   - Registros cargados: {summary['total_records']}")
            print(f"   - Uso de memoria: {summary['memory_usage']}")
            
            self.test_results['load'] = True
            
        except Exception as e:
            self.test_results['errors'].append(f"Error en carga: {str(e)}")
            print(f"❌ Error en carga: {str(e)}")
    
    def show_summary(self):
        """Muestra un resumen de todas las pruebas"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS ETL")
        print("=" * 60)
        
        # Tiempo total
        duration = datetime.now() - self.start_time
        print(f"⏱️ Tiempo total: {duration.total_seconds():.2f} segundos")
        
        # Resultados por módulo
        modules = [
            ('Extracción', 'extract'),
            ('Limpieza', 'clean'),
            ('Carga', 'load')
        ]
        
        for module_name, module_key in modules:
            status = "✅ EXITOSO" if self.test_results[module_key] else "❌ FALLIDO"
            print(f"{module_name}: {status}")
        
        # Errores
        if self.test_results['errors']:
            print(f"\n❌ Errores encontrados ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results['errors'], 1):
                print(f"   {i}. {error}")
        
        # Advertencias
        if self.test_results['warnings']:
            print(f"\n⚠️ Advertencias ({len(self.test_results['warnings'])}):")
            for i, warning in enumerate(self.test_results['warnings'], 1):
                print(f"   {i}. {warning}")
        
        # Resultado general
        all_passed = all([
            self.test_results['extract'],
            self.test_results['clean'],
            self.test_results['load']
        ])
        
        if all_passed:
            print(f"\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            print("El proceso ETL está funcionando correctamente con los primeros 50 registros.")
        else:
            print(f"\n💥 ALGUNAS PRUEBAS FALLARON")
            print("Revisa los errores anteriores antes de continuar.")
        
        print("=" * 60)


def run_basic_test():
    """Función para ejecutar una prueba básica rápida"""
    print("🚀 Ejecutando prueba básica del ETL...")
    
    try:
        # Verificar configuración
        print(f"📁 Archivo de entrada: {Config.INPUT_PATH}")
        print(f"📁 Archivo de salida: {Config.OUTPUT_PATH}")
        
        if not os.path.exists(Config.INPUT_PATH):
            print("❌ Error: Archivo Pokemon.csv no encontrado")
            return False
        
        # Prueba rápida de cada módulo
        print("\n🔍 Probando Extract...")
        extractor = Extract(Config.INPUT_PATH)
        df = extractor.extract_first_n_rows(5)  # Solo 5 registros para prueba rápida
        
        if df is None:
            print("❌ Error en Extract")
            return False
        print(f"✅ Extract OK - {len(df)} registros")
        
        print("\n🔍 Probando Clean...")
        cleaner = Clean(df)
        df_clean = cleaner.clean_data()
        
        if df_clean is None or df_clean.empty:
            print("❌ Error en Clean")
            return False
        print(f"✅ Clean OK - {len(df_clean)} registros limpios")
        
        print("\n🔍 Probando Load...")
        loader = Load(df_clean)
        test_path = "test_output.csv"
        result = loader.to_csv(test_path, include_timestamp=False)
        
        if result and os.path.exists(result):
            print(f"✅ Load OK - Archivo guardado: {result}")
            # Limpiar archivo de prueba
            try:
                os.remove(result)
            except:
                pass
            return True
        else:
            print("❌ Error en Load")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba básica: {str(e)}")
        return False


if __name__ == "__main__":
    # Permitir elegir entre prueba básica o completa
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "basic":
        success = run_basic_test()
        if success:
            print("\n🎉 Prueba básica completada exitosamente")
        else:
            print("\n💥 Prueba básica falló")
    else:
        # Ejecutar pruebas completas
        test_runner = TestETL()
        test_runner.run_all_tests()
