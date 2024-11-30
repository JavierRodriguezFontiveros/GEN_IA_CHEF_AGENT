# Bibliotecas de Python
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
import os

import pymysql

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Cargando mi llave personal de la API de HuggingFace:
load_dotenv(dotenv_path="Material_sensible/contraseña_api.env")

#Seleccionando la llave:
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

if not huggingface_api_key:
    raise ValueError("La clave API de Hugging Face no se cargó. Verifica el archivo contraseña.env.")

#Conexión con la api (LLM) de Hugging Face ya con la llave cargada:
client = InferenceClient(api_key=huggingface_api_key)




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Conexión con la DataBase de AWS
#Cargar las variables del archivo .env
load_dotenv(dotenv_path="Material_sensible/contraseña_database.env")

def connect_to_database():
    # Recuperar las variables de entorno del archivo .env
    host = os.getenv("DB_HOST")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = int(os.getenv("DB_PORT"))
    database = os.getenv("DB_NAME")

    try:
        
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            port=port,
            cursorclass=pymysql.cursors.DictCursor)

        print("Conexión exitosa a la base de datos.")

        connection.close()

    except pymysql.MySQLError as e:
        print(f"Error al conectarse a la base de datos: {e}")

#Realizar la conexión
connect_to_database()

#Generando la FastAPI
app = FastAPI()




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Creación de la clase de "recetas"
#Creación de la clase de "problemas culinarios"
#Creación de las clases de "Conversiones"
#Creación de las clases de"Temporadas y Países"
#Creación de la clase de "Condición"

class GenerateRecipeRequest(BaseModel):
    ingredients: list[str]  #Lista de ingredientes

class KitchenProblemRequest(BaseModel):
    issue: str  #Tipo de problema (salado, picante, ácido, etc.)

class ConversionRequest(BaseModel):
    quantity: float  #Cantidad que se desea convertir
    from_unit: str  #Unidad de origen (por ejemplo, "taza", "cucharada")
    to_unit: str  #Unidad de destino (por ejemplo, "gramos", "ml")

class SeasonalFoodRequest(BaseModel):
    season: str  #Estación del año: "primavera", "verano", "otoño", "invierno"
    country: str  #País: por ejemplo, "México", "España"

class HealthConditionRequest(BaseModel):
    condition: str  #Condición del usuario (por ejemplo, "celíaco", "intolerancia a la lactosa", "diabetes")




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Bienvenida a la página
@app.get("/")
async def home():
    return {"message": """
                    ¡Bienvenidos a Tu Chef Virtual, donde el sabor cobra vida! 🍳✨
                    
                    ¿Te has quedado sin ideas para cocinar? ¡No te preocupes! Con nuestra API personalizada, puedes:

                    🍴 **Generar recetas**: Introduce una lista de ingredientes y nuestro chef virtual creará una receta deliciosa para ti. ¡Perfecta para esos días en los que no sabes qué cocinar! 

                    🔥 **Resolver problemas de cocina**: ¿Tu comida está demasiado salada, picante o ácida? Dinos el problema y te damos la solución para que no se eche a perder. 🍽️

                    🧑‍🍳 **Conversión de medidas**: ¿No sabes cuántos gramos tiene una taza de harina o cuántos mililitros en una cucharada sopera? ¡Aquí te lo calculamos!

                    🌿 **Comidas según temporada**: Introduce una estación del año y un país, y te sugerimos platos de temporada que puedes preparar con ingredientes frescos.

                    🧑‍⚕️ **Alergias y enfermedades**: Si tienes alguna condición de salud como celiaquía, intolerancia a la lactosa o diabetes, te recomendamos qué alimentos evitar y qué alternativas usar.

                    Con nosotros, tu cocina será más fácil, creativa y saludable. ¡Deja que tu chef virtual te guíe en cada paso!

                    ¿Listo para cocinar con estilo? ¡Comencemos juntos! 🍴
                   """
    }



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Recetario
@app.post("/recetas/")
async def generate_recipe(request: GenerateRecipeRequest):
    ingredients = request.ingredients.lower() # Convertir a minúsculas para consistencia

    if len(ingredients) < 3:
        raise HTTPException(
            status_code=400, detail="Debes proporcionar almenos 3 ingredientes.")

    try:
        #Configuración del modelo:
        llm = HuggingFaceEndpoint(endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  # Modelo
                                  huggingfacehub_api_token=huggingface_api_key,  # Contraseña
                                  temperature=0.7,  # Precisión
                                  max_length=300)  # Tokens
        
        #Detallamos el prompt:
        prompt = PromptTemplate(input_variables=["ingredients_list"],
                                template="""
                                            Eres un chef experto en crear recetas clásicas y deliciosas.
                                            Dada la siguiente lista de ingredientes: {ingredients_list},
                                            crea un plato típico. Describe brevemente el nombre del plato, 
                                            los pasos para prepararlo y un consejo especial para mejorar su sabor.
                                        """)

        #Generación de la respuesta respecto al prompt:
        formatted_prompt = prompt.format(ingredients_list=", ".join(ingredients))
        respuesta = llm.invoke(formatted_prompt)

        # Devuelve la respuesta generada
        return {"recipe": respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ejemplo de uso
# {
#   "ingredients": ["lechuga", "tomate", "atun", "maiz", "aceite"]
# }



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Solucionario
@app.post("/problemas_cocina/")
async def solve_kitchen_problem(request: KitchenProblemRequest):
    issue = request.issue.lower()  

    try:
        llm = HuggingFaceEndpoint(endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  
                                  huggingfacehub_api_token=huggingface_api_key, 
                                  temperature=0.7,  
                                  max_length=300)  

        prompt = PromptTemplate(input_variables=["issue", "ingredient"],
                                template="""
                                            Eres un chef experimentado que ayuda a resolver problemas de cocina.
                                            Si el plato está {issue}, ¿qué se debe hacer para solucionar el problema?
                                            Dar anímos con el problema.
                                            Solo en caso de que no haya solución proponer un plato de cocinado rápido.
                                         """)

        formatted_prompt = prompt.format(issue=issue)
        respuesta = llm.invoke(formatted_prompt)  

        return {"solution": respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ejemplo de uso:
# {
#   "issue": "salado",
# }




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Conversionario:
@app.post("/conversiones/")
async def convert_measurements(request: ConversionRequest):
    quantity = request.quantity
    from_unit = request.from_unit.lower()
    to_unit = request.to_unit.lower()

    try:

        llm = HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  
            huggingfacehub_api_token=huggingface_api_key,
            temperature=0.7,
            max_length=300
        )

        prompt = PromptTemplate(input_variables=["quantity", "from_unit", "to_unit"],
                                template="""
                                            Tienes la cantidad {quantity} {from_unit} y quieres convertirla a {to_unit}.
                                            Proporcióname la cantidad convertida y una breve explicación de cómo se realiza la conversión.
                                            Si no es posible hacer la conversión, indica un mensaje de error amigable.
                                        """)


        formatted_prompt = prompt.format(quantity=quantity, from_unit=from_unit, to_unit=to_unit)
        respuesta = llm.invoke(formatted_prompt)

        return {"conversion": respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la conversión: {str(e)}")

# Ejemplo de uso
# {
#   "quantity": 1,
#   "from_unit": "taza",
#   "to_unit": "gramos"
# }




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Temporadas/Países
@app.post("/comidas_por_temporada/")
async def get_seasonal_foods(request: SeasonalFoodRequest):
    season = request.season.lower()
    country = request.country.lower()

    try:
        llm = HuggingFaceEndpoint(endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  
                                  huggingfacehub_api_token=huggingface_api_key,
                                  temperature=0.7,
                                  max_length=300)

        prompt = PromptTemplate(input_variables=["season", "country"],
                                template="""
                                            En el país de {country}, ¿cuáles son las comidas típicas para la estación {season}?
                                            Dame una lista de platos típicos, explicando brevemente qué los hace característicos de esta temporada.
                                        """)

        formatted_prompt = prompt.format(season=season, country=country)
        respuesta = llm.invoke(formatted_prompt)

        return {"foods": respuesta}

    except Exception as e:
        # Manejo de errores
        raise HTTPException(status_code=500, detail=f"Error al obtener comidas: {str(e)}")





# ejemplo de uso:
# {
#     "season": "otoño",
#     "country": "mexico"
# }
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Enfermedades
@app.post("/alergias-enfermedades/")
async def get_food_recommendations(request: HealthConditionRequest):
    condition = request.condition.lower()

    try:
        llm = HuggingFaceEndpoint(endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  
                                  huggingfacehub_api_token=huggingface_api_key,  
                                  temperature=0.7,
                                  max_length=300)

        prompt = PromptTemplate(input_variables=["condition"],
                                template="""
                                            Si alguien tiene la condición de salud llamada '{condition}', ¿qué alimentos debe evitar y qué alternativas saludables podría considerar?
                                            Proporciona una lista de alimentos a evitar y alguna recomendación adicional sobre cómo manejar esta condición con la dieta.
                                        """)

        formatted_prompt = prompt.format(condition=condition)
        respuesta = llm.invoke(formatted_prompt)

        return {"recommendations": respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener recomendaciones: {str(e)}")


# ejemplo de uso:
# {
#     "condition": "celíaco"
# }



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Punto de entrada principal
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
