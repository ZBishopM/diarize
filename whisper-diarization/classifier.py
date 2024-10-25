import os
import json
import requests
import mysql.connector
from mysql.connector import Error
# URL del modelo de Ollama en el puerto 11434
ollama_url = "http://localhost:11434/api/generate"

db_config = {
    'host': '18.191.247.200',
    'port':'3306',
    'database': 'foh-qas',
    'user': 'foh',  # Cambia esto por tu usuario de MySQL
    'password': 'NS**!24!00',  # Cambia esto por tu contraseña de MySQL
}

# Define el directorio donde están tus archivos .txt
input_directory = "./audio_files"
#output_file = "classification_results.json"

def classify_text(text):
    data = {
        "model": "pepito",
        "prompt": f"""{text}""",
        "stream": False
    }
    
    try:
        # Enviar la solicitud con `stream=True` para procesar la respuesta en partes
        response = requests.post(ollama_url, json=data, stream=True)
        response.raise_for_status()  # Verificar si hay errores en la solicitud
        
        # Acumular las partes de la respuesta
        full_response = ""
        for line in response.iter_lines():
            if line:
                # Convertir cada línea de JSON en un diccionario
                json_line = json.loads(line)
                # Agregar solo el contenido relevante de la respuesta
                full_response += json_line.get("response", "")
        # Limpiar espacios y saltos de línea
        cleaned_response = full_response.replace('\n', '')
        # Verificar si falta la llave de cierre
        if not cleaned_response.endswith('}'):
            cleaned_response += '}'

        return cleaned_response.strip()  # Devolver solo la respuesta consolidada y limpia
    
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None

def insert_result(db_connection, filename, classification):
    cursor = db_connection.cursor()
    print(classification)
    query = """
    INSERT INTO AUDIOS_CATEGORIAS (filename, deuda_total, LTD, LTDE, convenio, bajas, tipi)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        filename,
        1 if classification["negociaciones"]["deuda_total"] == "sí" else 0,
        1 if classification["negociaciones"]["LTD"] == "sí" else 0,
        1 if classification["negociaciones"]["LTDE"] == "sí" else 0,
        1 if classification["negociaciones"]["convenio"] == "sí" else 0,
        1 if classification["negociaciones"]["bajas"] == "sí" else 0,
        classification["tipi"]
    )
    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()


""" def main():

    classifications = {}
    for filename in os.listdir(input_directory):
        if filename.endswith(".txt"):
            with open(os.path.join(input_directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                classification = classify_text(content)
                if classification is not None:
                    print(f"respuesta: {classification}")
                    try:
                        json_object=json.loads(classification)
                        classifications[filename] = json_object
                    except json.JSONDecodeError:
                        print(f"Respuesta no válida para {filename}:{classification}")

    # Guardar las clasificaciones en un archivo JSON
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(classifications, outfile, ensure_ascii=False)

    print(f"Clasificación completada. Resultados guardados en {output_file}.") """
def main():
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**db_config)
        if db_connection.is_connected():
            print("Conexión exitosa a la base de datos.")
            for filename in os.listdir("./audio_files"):
                if filename.endswith(".txt"):
                    with open(os.path.join("./audio_files", filename), 'r',  encoding='utf-8') as file:
                        content = file.read()
                        classification = classify_text(content)
                        if classification is not None:
                            try:
                                json_object = json.loads(classification)
                                insert_result(db_connection, filename,  json_object)
                            except json.JSONDecodeError:
                                print(f"Respuesta no válida para {filename}:    {classification}")

            print("Clasificación completada y datos guardados en la base de datos.")
        else:
            print("No se pudo conectar a la base de datos.")
        

    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()

if __name__ == "__main__":
    main()
