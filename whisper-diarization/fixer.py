import os
import json
import requests
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
client = OpenAI(api_key= "fdsajgldsahfdk")
#USAR GPT 4.0 mini
usar_GPT=False
ollama_url = "http://localhost:11434/api/generate"

db_config = {
    'host': '18.191.247.200',
    'port':'3306',
    'database': 'foh-qas',
    'user': 'foh',  # Cambia esto por tu usuario de MySQL
    'password': 'NS**!24!00',  # Cambia esto por tu contraseña de MySQL
}

# Define el directorio donde están tus archivos .txt
input_directory = "./audio_files/PDP_audios"
#output_file = "classification_results.json"

def classify_text(text):
    data = {
        "model": "fixer",
        "prompt": f"""{text}""",
        "stream": False
    }
    if usar_GPT:
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
               {
               "role": "system", "content": 
               """
               Los mensajes que recibirás a partir de ahora serán conversaciones transcritas sobre la simulación de cobro de una cuenta en donde participa un Asesor de cobranzas y un cliente.
        La transcripción fue hecha mediante inteligencia artifical, así que puede haber partes sin coherencia, mensajes asignados a un mismo speaker que en realidad eran dos personas hablando a la vez, o no claridad en lo que se quiere entender.
        Tu trabajo es corregir la conversación transcrita para que tenga sentido y que otra inteligencia artifical lo procese. Manteniendo el formato y la separación de personas. 
               """},{
               "role": "user",
               "content":f"""{text}"""}],
        temperature=0.5,
        stream=False
        )
        return completion.choices[0].message.content
    
    try:
        # Enviar la solicitud con `stream=True` para procesar la respuesta en partes
        response = requests.post(ollama_url, json=data, stream=True)
        response.raise_for_status()  # Verificar si hay errores en la solicitud
        
        print(response)
        # Acumular las partes de la respuesta
        full_response = ""
        for line in response.iter_lines():
            if line:
                # Convertir cada línea de JSON en un diccionario
                json_line = json.loads(line)
                # Agregar solo el contenido relevante de la respuesta
                full_response += json_line.get("response", "")
                
        return full_response.strip()  # Devolver solo la respuesta consolidada y limpia
    
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None


def main():
    print("A VER LOS AUDIOS")
    for filename in os.listdir("./audio_files/PDP_audios"):
        if filename.endswith(".txt"):
            print("ENCONTRE UNO")
            with open(os.path.join("./audio_files/PDP_audios", filename), 'r',  encoding='utf-8') as file:
                content = file.read()
                classification = classify_text(content)
                print("FIXED: ")
                print(classification)
                if classification is not None:
                    #create file with classification
                    f=open(f"""FIXED-{filename}""","w")
                    f.write(f"""{classification}""")
                    f.close()
        else:
            print("esto no es un txt")
                    
    print("He arreglado un poco la transcripción :D")
        

if __name__ == "__main__":
    main()
