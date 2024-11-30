# Bibliotecas de Python
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
import os




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# Cargar el archivo .env
load_dotenv(dotenv_path="contraseña.env")

# Recuperar la clave API
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

# Verifica que la clave se cargó correctamente (solo para pruebas)
if not huggingface_api_key:
    raise ValueError("La clave API de Hugging Face no se cargó. Verifica el archivo contraseña.env.")



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#Conexión con la api (LLM) de Hugging Face

client = InferenceClient(api_key=huggingface_api_key)



app = FastAPI()





''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Modelos de entrada
class GenerateRecipeRequest(BaseModel):
    ingredients: list[str]  # Lista de 5 ingredientes

# Bienvenida a la página
@app.get("/")
async def home():
    return {
        "message": """
                    ¡Bienvenidos a Tu Chef Virtual, donde el sabor cobra vida! 🍳✨
          
                    Aquí encontrarás recetas personalizadas, consejos culinarios, 
                    y la inspiración que necesitas para convertir cualquier plato en una obra maestra. 🥗🍝  
                                
                    ¡Deja que nuestro chef te guíe paso a paso y transforma tu cocina en el corazón de la creatividad y el buen gusto! 👨‍🍳🔥  
                                
                    ¿Listo para cocinar con estilo? ¡Comencemos juntos! 🍴
                   """
    }




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
@app.post("/recetas/")
async def generate_recipe(request: GenerateRecipeRequest):
    ingredients = request.ingredients

    if len(ingredients) != 5:
        raise HTTPException(
            status_code=400, detail="Debes proporcionar exactamente 5 ingredientes."
        )

    try:
        # Configuración del modelo:
        llm = HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",  # Modelo
            huggingfacehub_api_token=huggingface_api_key,  # Contraseña
            temperature=0.7,  # Precisión
            max_length=300,  # Tokens
        )

        # Detallamos el prompt:
        prompt = PromptTemplate(
            input_variables=["ingredients_list"],
            template="""
                Eres un chef experto en crear recetas innovadoras y deliciosas.
                Dada la siguiente lista de ingredientes: {ingredients_list},
                crea un plato único. Describe brevemente el nombre del plato, 
                los pasos para prepararlo y un consejo especial para mejorar su sabor.
            """
        )

        # Generación de la respuesta respecto al prompt:
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
# Modelos de entrada
class KitchenProblemRequest(BaseModel):
    issue: str  # Descripción del problema (salado, picante, etc.)
    ingredient: str = None  # Ingrediente opcional que causa el problema

@app.get("/")
async def home():
    return {
        "message": """
                    ¡Bienvenidos a Tu Chef Virtual, donde el sabor cobra vida! 🍳✨
          
                    Aquí encontrarás recetas personalizadas, consejos culinarios, 
                    y la inspiración que necesitas para convertir cualquier plato en una obra maestra. 🥗🍝  
                                
                    ¡Deja que nuestro chef te guíe paso a paso y transforma tu cocina en el corazón de la creatividad y el buen gusto! 👨‍🍳🔥  
                                
                    ¿Listo para cocinar con estilo? ¡Comencemos juntos! 🍴
                   """
    }

@app.post("/problemas-cocina/")
async def solve_kitchen_problem(request: KitchenProblemRequest):
    issue = request.issue.lower()
    ingredient = request.ingredient

    # Diccionario con soluciones para problemas comunes
    solutions = {
        "salado": "Si tu comida está muy salada, añade papas crudas, arroz o un líquido sin sal como agua o crema para diluir el exceso.",
        "picante": "Si está muy picante, añade productos lácteos como crema, leche o yogur, o incrementa el volumen del plato con más ingredientes no picantes.",
        "acido": "Si está demasiado ácido, agrega un poco de azúcar, miel, o incluso un toque de bicarbonato de sodio para neutralizar la acidez.",
    }

    # Respuesta para ingredientes específicos (si se proporciona)
    if ingredient:
        response = f"Parece que te pasaste con el ingrediente '{ingredient}'. "
        if issue in solutions:
            response += f"{solutions[issue]}"
        else:
            response += "Intenta equilibrarlo añadiendo más ingredientes complementarios al plato."
        return {"solution": response}

    # Respuesta general según el problema
    if issue in solutions:
        return {"solution": solutions[issue]}
    else:
        raise HTTPException(
            status_code=400, detail="No reconozco el problema descrito. Intenta especificar si es salado, picante o ácido."
        )

# Ejemplo de uso:
# {
#   "issue": "salado",
#   "ingredient": "sal"
# }



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Modelos de entrada
class ConversionRequest(BaseModel):
    quantity: float  # Cantidad que se desea convertir
    from_unit: str  # Unidad de origen (por ejemplo, "taza", "cucharada")
    to_unit: str  # Unidad de destino (por ejemplo, "gramos", "ml")

@app.get("/")
async def home():
    return {
        "message": """
                    ¡Bienvenidos a Tu Chef Virtual, donde el sabor cobra vida! 🍳✨
          
                    Aquí encontrarás recetas personalizadas, consejos culinarios, 
                    y la inspiración que necesitas para convertir cualquier plato en una obra maestra. 🥗🍝  
                                
                    ¡Deja que nuestro chef te guíe paso a paso y transforma tu cocina en el corazón de la creatividad y el buen gusto! 👨‍🍳🔥  
                                
                    ¿Listo para cocinar con estilo? ¡Comencemos juntos! 🍴
                   """
    }

@app.post("/conversiones/")
async def convert_measurements(request: ConversionRequest):
    quantity = request.quantity
    from_unit = request.from_unit.lower()
    to_unit = request.to_unit.lower()

    # Tabla de conversiones comunes
    conversions = {
        ("taza", "gramos", "harina"): 120,  # 1 taza de harina = 120 gramos
        ("taza", "gramos", "azúcar"): 200,  # 1 taza de azúcar = 200 gramos
        ("cucharada", "ml"): 15,  # 1 cucharada = 15 ml
        ("cucharadita", "ml"): 5,  # 1 cucharadita = 5 ml
    }

    # Conversión personalizada según el contexto (por ejemplo, tipo de ingrediente)
    if (from_unit, to_unit, "harina") in conversions:
        result = quantity * conversions[(from_unit, to_unit, "harina")]
        return {
            "conversion": f"{quantity} {from_unit} de harina equivale a {result} {to_unit}."
        }
    elif (from_unit, to_unit, "azúcar") in conversions:
        result = quantity * conversions[(from_unit, to_unit, "azúcar")]
        return {
            "conversion": f"{quantity} {from_unit} de azúcar equivale a {result} {to_unit}."
        }
    elif (from_unit, to_unit) in conversions:
        result = quantity * conversions[(from_unit, to_unit)]
        return {
            "conversion": f"{quantity} {from_unit} equivale a {result} {to_unit}."
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="No se encontró una conversión válida para las unidades proporcionadas. Verifica las unidades y prueba de nuevo.",
        )

{
  "quantity": 1,
  "from_unit": "taza",
  "to_unit": "gramos"
}

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Modelo de entrada
class SeasonalFoodRequest(BaseModel):
    season: str  # Estación del año: "primavera", "verano", "otoño", "invierno"
    country: str  # País: por ejemplo, "México", "España"

@app.post("/comidas-por-temporada/")
async def get_seasonal_foods(request: SeasonalFoodRequest):
    season = request.season.lower()
    country = request.country.lower()

    # Diccionario con comidas por temporada y país
    seasonal_foods = {
        "mexico": {
            "primavera": ["Tacos de pescado", "Ensalada de nopales", "Aguachile", "Pozole verde", "Tamalitos de acelga"],
            "verano": ["Ceviche", "Elotes asados", "Agua fresca de tamarindo", "Sopa fría de aguacate", "Ensalada de mango con chile"],
            "otoño": ["Pan de muerto", "Calabaza en tacha", "Champurrado", "Tamales de mole", "Pozole rojo"],
            "invierno": ["Rosca de Reyes", "Ponche navideño", "Atole de guayaba", "Chiles en nogada", "Buñuelos"],
        },
        "españa": {
            "primavera": ["Gazpacho", "Tortilla de espárragos", "Ensalada campera", "Arroz con alcachofas", "Salmorejo"],
            "verano": ["Paella de mariscos", "Salpicón de marisco", "Helado artesanal", "Ajoblanco", "Pipirrana"],
            "otoño": ["Castañas asadas", "Cocido madrileño", "Crema de calabaza", "Tarta de almendra", "Setas a la plancha"],
            "invierno": ["Roscón de Reyes", "Caldo gallego", "Churros con chocolate", "Estofado de cordero", "Pestiños"],
        },
    }

    # Verifica si el país y la estación están disponibles
    if country in seasonal_foods and season in seasonal_foods[country]:
        foods = seasonal_foods[country][season]
        return {"foods": foods}
    else:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron datos para la estación o el país proporcionados. Intenta con otro país o estación.",
        )





# ejemplo de uso:
# {
#     "season": "otoño",
#     "country": "mexico"
# }

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Modelo de entrada
class HealthConditionRequest(BaseModel):
    condition: str  # Condición del usuario (por ejemplo, "celíaco", "intolerancia a la lactosa", "diabetes")

@app.post("/alergias-enfermedades/")
async def get_food_recommendations(request: HealthConditionRequest):
    condition = request.condition.lower()

    # Diccionario con alimentos a evitar según la condición
    health_conditions = {
        "celíaco": {
            "avoid": ["Pan y pasteles con gluten", "Pasta de trigo", "Cerveza regular", "Salsas espesadas con harina", "Cereales con gluten"],
            "info": "Evita alimentos que contengan gluten. Busca productos etiquetados como 'sin gluten'.",
        },
        "intolerancia a la lactosa": {
            "avoid": ["Leche regular", "Queso", "Mantequilla", "Nata", "Yogures no deslactosados"],
            "info": "Evita productos lácteos o busca opciones deslactosadas y bebidas vegetales como leche de almendra o avena.",
        },
        "diabetes": {
            "avoid": ["Azúcar refinada", "Bebidas azucaradas", "Pan blanco", "Postres industriales", "Caramelos"],
            "info": "Controla el consumo de carbohidratos simples y azúcares. Prioriza alimentos de bajo índice glucémico.",
        },
        "alergia a los frutos secos": {
            "avoid": ["Nueces", "Almendras", "Avellanas", "Mantequillas de frutos secos", "Postres que contengan frutos secos"],
            "info": "Evita todos los productos que contengan frutos secos y revisa etiquetas por posibles trazas.",
        },
        "hipertensión": {
            "avoid": ["Comidas muy saladas", "Embutidos", "Alimentos enlatados", "Snacks salados", "Salsas procesadas"],
            "info": "Reduce el consumo de sodio. Opta por hierbas y especias para sazonar tus comidas.",
        },
    }

    # Busca la condición proporcionada
    if condition in health_conditions:
        data = health_conditions[condition]
        return {
            "condition": condition.capitalize(),
            "avoid": data["avoid"],
            "info": data["info"],
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="No se encontró información para la condición especificada. Intenta con otra como 'celíaco', 'diabetes' o 'intolerancia a la lactosa'.",
        )


# ejemplo de uso:
# {
#     "condition": "celíaco"
# }
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Punto de entrada principal
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
