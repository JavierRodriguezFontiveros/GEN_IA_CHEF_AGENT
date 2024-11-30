from fastapi import FastAPI, HTTPException
import pymysql
import uvicorn


from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate



huggingface_api_key = ""
client = InferenceClient(api_key=huggingface_api_key)

llm = HuggingFaceEndpoint(endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct",
                          huggingfacehub_api_token=huggingface_api_key,
                          temperature=0.7,  
                          max_length=300)

prompt = PromptTemplate(input_variables=["location"],
                        template="Eres un experto en viajes. Proporciona una lista de 3 lugares interesantes para visitar en Salamanca, con una breve descripción de cada lugar.")

place = "Salamanca"
llm.invoke(prompt.format(location=place))

app = FastAPI()

@app.get('/')
async def home():
    return {"message": "Hola, esta es la API de Rubén"}





if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)