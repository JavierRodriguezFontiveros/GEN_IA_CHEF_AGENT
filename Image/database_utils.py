#Bibliotecas de Python
import pymysql
from dotenv import load_dotenv
import os

#Carga un archivo .env específico
def load_env_file(env_path: str):
    load_dotenv(dotenv_path=env_path)



#Valida que las variables de entorno necesarias estén presentes
def validate_env_variables(required_vars: list[str]):
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
    print("Variables de entorno cargadas correctamente.")




#Conecta con la database de Irlanda:
def connect_to_database():
    host = os.getenv("DB_HOST")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    try:
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor)

        print("Conexión exitosa a la base de datos.")
        return connection

    except pymysql.MySQLError as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None
    



#Crea el dataframe si no existe:
def create_table_if_not_exists():
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                create_table = '''
                                    CREATE TABLE IF NOT EXISTS receta_logs (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                                        input_prompt TEXT NOT NULL,
                                        output_response TEXT NOT NULL,
                                        status_code INT NOT NULL,
                                        error_message TEXT)
                                '''

                cursor.execute(create_table)
                connection.commit()
                print("Tabla receta_logs verificada o creada exitosamente.")

        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            connection.close()




#Hace el Regsitro en el dataframe:
def insert_recipe_log(input_prompt: str, output_response: str, status_code: int, error_message: str = None):
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO receta_logs (input_prompt, output_response, status_code, error_message)
                VALUES (%s, %s, %s, %s)
                """
                print(f"Inserting log: {input_prompt}, {output_response}, {status_code}, {error_message}")
                cursor.execute(sql, (input_prompt, output_response, status_code, error_message))
                connection.commit()
                print("Log insertado exitosamente.")
        except Exception as e:
            print(f"Error al insertar en la base de datos: {e}")
        finally:
            connection.close()



