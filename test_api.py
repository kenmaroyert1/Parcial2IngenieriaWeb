import requests
import json
import time

# Configuración de la API
BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoints():
    """Prueba todos los endpoints de la API"""
    
    print("🧪 Iniciando pruebas de la API Pokemon ETL")
    print("=" * 60)
    
    # Lista de pruebas a ejecutar
    tests = [
        {
            "name": "Página de bienvenida",
            "method": "GET",
            "url": f"{BASE_URL}/",
            "expected_status": 200
        },
        {
            "name": "Obtener todos los Pokemon",
            "method": "GET", 
            "url": f"{BASE_URL}/api/pokemon",
            "expected_status": 200
        },
        {
            "name": "Obtener Pokemon por ID (Bulbasaur)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/1",
            "expected_status": 200
        },
        {
            "name": "Obtener Pokemon por ID inexistente",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/999",
            "expected_status": 404
        },
        {
            "name": "Obtener Pokemon por nombre (Charmander)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/name/Charmander",
            "expected_status": 200
        },
        {
            "name": "Obtener Pokemon por nombre inexistente",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/name/Inexistente",
            "expected_status": 404
        },
        {
            "name": "Obtener Pokemon por tipo (Fire)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/type/Fire",
            "expected_status": 200
        },
        {
            "name": "Obtener Pokemon por tipo (Water)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/type/Water",
            "expected_status": 200
        },
        {
            "name": "Buscar Pokemon (Char)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/search?q=char",
            "expected_status": 200
        },
        {
            "name": "Buscar Pokemon (Fire)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/search?q=fire",
            "expected_status": 200
        },
        {
            "name": "Buscar sin parámetro",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/search",
            "expected_status": 400
        },
        {
            "name": "Obtener Pokemon legendarios",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/legendary",
            "expected_status": 200
        },
        {
            "name": "Obtener estadísticas",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon/stats",
            "expected_status": 200
        },
        {
            "name": "Paginación (página 1)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon?page=1&per_page=10",
            "expected_status": 200
        },
        {
            "name": "Paginación (página 2)",
            "method": "GET",
            "url": f"{BASE_URL}/api/pokemon?page=2&per_page=10",
            "expected_status": 200
        }
    ]
    
    # Ejecutar pruebas
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i:2d}. Probando: {test['name']}")
        print(f"    URL: {test['url']}")
        
        try:
            # Realizar petición
            start_time = time.time()
            response = requests.get(test['url'], timeout=10)
            duration = (time.time() - start_time) * 1000
            
            # Verificar status code
            if response.status_code == test['expected_status']:
                print(f"    ✅ ÉXITO - Status: {response.status_code} - Tiempo: {duration:.2f}ms")
                
                # Mostrar información adicional para algunas pruebas
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if 'pokemon' in data and isinstance(data['pokemon'], list):
                            print(f"    📊 Pokemon encontrados: {len(data['pokemon'])}")
                        elif 'pokemon' in data and isinstance(data['pokemon'], dict):
                            print(f"    🎯 Pokemon: {data['pokemon'].get('nombre', 'N/A')}")
                        elif 'total' in data:
                            print(f"    📊 Total: {data['total']}")
                        elif 'total_pokemon' in data:
                            print(f"    📊 Total Pokemon: {data['total_pokemon']}")
                            
                    except json.JSONDecodeError:
                        print(f"    ⚠️ Respuesta no es JSON válido")
                
                passed += 1
            else:
                print(f"    ❌ FALLO - Esperado: {test['expected_status']}, Obtenido: {response.status_code}")
                print(f"    📄 Respuesta: {response.text[:200]}...")
                failed += 1
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ ERROR DE CONEXIÓN - {str(e)}")
            failed += 1
        except Exception as e:
            print(f"    ❌ ERROR INESPERADO - {str(e)}")
            failed += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Pruebas exitosas: {passed}")
    print(f"❌ Pruebas fallidas: {failed}")
    print(f"📈 Tasa de éxito: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n💥 {failed} pruebas fallaron. Revisa la configuración.")
    
    return passed, failed

def test_detailed_endpoints():
    """Pruebas detalladas de endpoints específicos"""
    
    print("\n" + "=" * 60)
    print("🔍 PRUEBAS DETALLADAS")
    print("=" * 60)
    
    # Probar estadísticas detalladas
    print("\n1. Analizando estadísticas generales...")
    try:
        response = requests.get(f"{BASE_URL}/api/pokemon/stats")
        if response.status_code == 200:
            stats = response.json()
            
            print(f"   📊 Total Pokemon: {stats.get('total_pokemon', 0)}")
            print(f"   🌟 Pokemon legendarios: {stats.get('pokemon_legendarios', 0)}")
            print(f"   💫 Pokemon mega: {stats.get('pokemon_mega', 0)}")
            print(f"   🎯 Poder promedio: {stats.get('estadisticas_poder', {}).get('promedio', 0)}")
            
            # Top 3 más poderosos
            top_pokemon = stats.get('top_5_mas_poderosos', [])[:3]
            if top_pokemon:
                print("   🏆 Top 3 más poderosos:")
                for i, pokemon in enumerate(top_pokemon, 1):
                    print(f"      {i}. {pokemon.get('nombre')} - Poder: {pokemon.get('poder_total')}")
                    
        else:
            print(f"   ❌ Error al obtener estadísticas: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Probar tipos de Pokemon
    print("\n2. Analizando distribución por tipos...")
    try:
        response = requests.get(f"{BASE_URL}/api/pokemon/stats")
        if response.status_code == 200:
            stats = response.json()
            tipos = stats.get('tipos_principales', {})
            
            print("   🎨 Distribución por tipos:")
            for tipo, cantidad in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
                print(f"      {tipo}: {cantidad} Pokemon")
                
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Probar búsqueda
    print("\n3. Probando funcionalidad de búsqueda...")
    busquedas = ["char", "fire", "mega", "grass"]
    
    for termino in busquedas:
        try:
            response = requests.get(f"{BASE_URL}/api/pokemon/search?q={termino}")
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                print(f"   🔍 '{termino}': {total} resultados encontrados")
                
                if total > 0 and total <= 3:
                    pokemon_names = [p.get('nombre') for p in data.get('pokemon', [])]
                    print(f"       Pokemon: {', '.join(pokemon_names)}")
                    
        except Exception as e:
            print(f"   ❌ Error buscando '{termino}': {str(e)}")

if __name__ == "__main__":
    print("🚀 Verificando conexión con la API...")
    
    try:
        # Verificar que la API esté activa
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API está activa y respondiendo")
            
            # Ejecutar pruebas
            passed, failed = test_api_endpoints()
            test_detailed_endpoints()
            
        else:
            print(f"❌ API no está respondiendo correctamente. Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API.")
        print("💡 Asegúrate de que la API esté ejecutándose en http://127.0.0.1:5000")
        print("   Ejecuta: python app_simple.py")
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    
    print("\n" + "=" * 60)