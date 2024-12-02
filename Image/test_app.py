import requests

def test_generate_recipe():
    url = 'http://localhost:8000/recetas/'  
    data = {'ingredients': ["lechuga", "tomate", "atun", "maiz", "aceite"]}  
    response = requests.post(url, json=data)  
    assert response.status_code == 200
    assert "recipe" in response.json()

def test_convert_measurements():
    url = 'http://localhost:8000/conversiones/'  
    data = {'quantity': 1, 'from_unit': 'taza', 'to_unit': 'gramos'}  
    response = requests.post(url, json=data)  
    assert response.status_code == 200
    assert "conversion" in response.json()

def test_get_seasonal_foods():
    url = 'http://localhost:8000/comidas_temporada/'  
    data = {'season': 'otoño', 'country': 'mexico'}  
    response = requests.post(url, json=data)  
    assert response.status_code == 200
    assert "foods" in response.json()

def test_get_food_recommendations():
    url = 'http://localhost:8000/alergias_enfermedades/'  
    data = {'condition': 'celíaco'}  
    response = requests.post(url, json=data)  
    assert response.status_code == 200
    assert "recommendations" in response.json()


