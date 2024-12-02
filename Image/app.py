# Bibliotecas de Python
from fastapi import FastAPI, HTTPException, Request
import uvicorn
from pydantic import BaseModel

from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
import os

from database_utils import connect_to_database, create_table_if_not_exists, insert_recipe_log, load_env_file, validate_env_variables

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Cargando mi llave personal de la API de HuggingFace:
load_dotenv(dotenv_path="../Image/Material_sensible/contraseña_api.env")

#Seleccionando la llave:
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

if not huggingface_api_key:
    raise ValueError("La clave API de Hugging Face no se cargó. Verifica el archivo contraseña.env.")

#Conexión con la api (LLM) de Hugging Face ya con la llave cargada:
client = InferenceClient(api_key=huggingface_api_key)

#Configuración general del modelo:
llm = HuggingFaceEndpoint(endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  # Modelo
                          huggingfacehub_api_token=huggingface_api_key,  # Contraseña
                          temperature=0.7,  # Precisión
                          max_length=300)  # Tokens



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# Cargar archivo de entorno
load_dotenv(dotenv_path="../Image/Material_sensible/contraseña_database.env")

# Verificar variables requeridas
validate_env_variables(["HUGGINGFACE_API_KEY", "DB_HOST", "DB_USER", "DB_PASSWORD","DB_NAME"])



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Generando la FastAPI
app = FastAPI()

create_table_if_not_exists()

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

# Configuración de las plantillas
template_directory = "../Image/templates"
print("Archivos en el directorio:", os.listdir(template_directory))  # Para confirmar que se lee correctamente

templates = Jinja2Templates(directory=template_directory)

# Ruta para la página de inicio
@app.get("/")
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

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
                   """}



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

@app.get("/recetas/")
async def get_recetas(request: Request):
    return templates.TemplateResponse("recetas.html", {"request": request})


#Recetario
@app.post("/recetas/")
async def generate_recipe(request: GenerateRecipeRequest):
    ingredients = [ingredient.lower() for ingredient in request.ingredients] # Convertir a minúsculas para consistencia

    if len(ingredients) < 3:
        raise HTTPException(
            status_code=400, detail="Debes proporcionar almenos 3 ingredientes.")

    try:
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

        # Inserción en logs
        insert_recipe_log(", ".join(ingredients), respuesta, 200)

        # Devuelve la respuesta generada
        return {"recipe": respuesta}

    except Exception as e:
        insert_recipe_log(", ".join(ingredients), "", 500, str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Ejemplo de uso
# {
#   "ingredients": ["lechuga", "tomate", "atun", "maiz", "aceite"]
# }




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
@app.get("/conversiones/")
async def get_conversiones(request: Request):
    return templates.TemplateResponse("conversiones.html", {"request": request})


#Conversionario:
@app.post("/conversiones/")
async def convert_measurements(request: ConversionRequest):
    quantity = request.quantity
    from_unit = request.from_unit.lower()
    to_unit = request.to_unit.lower()

    try:
        prompt = PromptTemplate(input_variables=["quantity", "from_unit", "to_unit"],
                                template="""
                                            Tienes la cantidad {quantity} {from_unit} y quieres convertirla a {to_unit}.
                                            Proporcióname la cantidad convertida y una breve explicación de cómo se realiza la conversión.
                                            Si no es posible hacer la conversión, indica un mensaje de error amigable.
                                        """)


        formatted_prompt = prompt.format(quantity=quantity, from_unit=from_unit, to_unit=to_unit)
        respuesta = llm.invoke(formatted_prompt)

        input_data = f"{quantity} {from_unit} to {to_unit}"
        insert_recipe_log(input_data, respuesta, 200)

        return {"conversion": respuesta}

    except Exception as e:
        input_data = f"{quantity} {from_unit} to {to_unit}"
        insert_recipe_log(input_data, "", 500, str(e))
        raise HTTPException(status_code=500, detail=f"Error en la conversión: {str(e)}")

# Ejemplo de uso
# {
#   "quantity": 1,
#   "from_unit": "taza",
#   "to_unit": "gramos"
# }



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
@app.get("/comidas_temporada/")
async def get_comidas_temporada(request: Request):
    return templates.TemplateResponse("comidas_temporada.html", {"request": request})

#Temporadas/Países
@app.post("/comidas_temporada/")
async def get_seasonal_foods(request: SeasonalFoodRequest):
    season = request.season.lower()
    country = request.country.lower()

    try:
        prompt = PromptTemplate(input_variables=["season", "country"],
                                template="""
                                            En el país de {country}, ¿cuáles son las comidas típicas para la estación {season}?
                                            Dame una lista de platos típicos, explicando brevemente qué los hace característicos de esta temporada.
                                        """)

        formatted_prompt = prompt.format(season=season, country=country)
        respuesta = llm.invoke(formatted_prompt)

        input_data = f"{season}, {country}"
        insert_recipe_log(input_data, respuesta, 200)

        return {"foods": respuesta}

    except Exception as e:
        input_data = f"{season}, {country}"
        insert_recipe_log(input_data, "", 500, str(e))
        raise HTTPException(status_code=500, detail=f"Error al obtener comidas: {str(e)}")

# ejemplo de uso:
# {
#     "season": "otoño",
#     "country": "mexico"
# }



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
@app.get("/alergias_enfermedades/")
async def get_alergias_enfermedades(request: Request):
    return templates.TemplateResponse("alergias_enfermedades.html", {"request": request})

#Enfermedades
@app.post("/alergias_enfermedades/")
async def get_food_recommendations(request: HealthConditionRequest):
    condition = request.condition.lower()

    try:
        prompt = PromptTemplate(input_variables=["condition"],
                                template="""
                                            Eres un cocinero experto en comidas que tienen en cuenta enfermedades
                                            Si alguien tiene la condición de salud llamada '{condition}', ¿qué alimentos debe evitar y qué alternativas saludables podría considerar?
                                            Proporciona una lista de alimentos a evitar y alguna recomendación adicional sobre cómo manejar esta condición con la dieta.
                                        """)

        formatted_prompt = prompt.format(condition=condition)
        respuesta = llm.invoke(formatted_prompt)

        insert_recipe_log(condition, respuesta, 200)

        return {"recommendations": respuesta}

    except Exception as e:
        insert_recipe_log(condition, "", 500, str(e))
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
