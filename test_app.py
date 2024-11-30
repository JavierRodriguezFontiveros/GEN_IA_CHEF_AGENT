#Ejemplo de uso:
# pytest test_app.py
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from fastapi.testclient import TestClient
from app import app  # Asumiendo que tu archivo principal de FastAPI se llama app.py

# Crear un cliente de prueba
client = TestClient(app)




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Test 1
def test_generate_recipe():
    # Lista de casos de prueba con sus entradas y salidas esperadas
    test_cases = [
        {
            "ingredients": ["tomate", "lechuga", "aceite"],  # Caso válido
            "expected_status": 200,
            "expected_key": "recipe",
        },
        {
            "ingredients": ["tomate", "aceite"],  # Caso inválido (menos de 3 ingredientes)
            "expected_status": 400,
            "expected_error": {"detail": "Debes proporcionar almenos 3 ingredientes."},
        },
    ]
    
    for case in test_cases:
        # Realizar la solicitud POST con los ingredientes de cada caso de prueba
        response = client.post("/recetas/", json={"ingredients": case["ingredients"]})
        
        # Verificar el código de estado
        assert response.status_code == case["expected_status"]
        
        if case["expected_status"] == 200:
            # Si la respuesta es válida (200), comprobar que contiene la clave "recipe"
            assert "recipe" in response.json()
        else:
            # Si la respuesta es inválida (400), verificar el mensaje de error
            assert response.json() == case["expected_error"]




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Test 2
def test_solve_kitchen_problem(issue, expected_status_code):
    # Definir el payload para la solicitud
    payload = {"issue": issue}

    # Realizar la solicitud POST
    response = client.post("/problemas-cocina/", json=payload)

    # Verificar que el código de estado sea el esperado
    assert response.status_code == expected_status_code

    # Si la solicitud fue exitosa, verificar que la respuesta tenga la clave 'solution'
    if response.status_code == 200:
        assert "solution" in response.json()