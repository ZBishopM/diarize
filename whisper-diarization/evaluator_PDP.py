import os
import json
import requests
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
client = OpenAI(api_key= "")
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
input_directory = "./audio_files/CR_AUDIOS" ##CAMBIAR POR PDP_audios
#output_file = "classification_results.json"

def classify_text(text):
    data = {
        "model": "evaluator",
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
               Contexto: Recibirás un audio transcrito de conversación de cobanza simulada entre dos personas.
        Uno de ellos es un agente de cobranzas de la Financiera 'Oh' y el otro un cliente.        
        Tu Objetivo: 
        Eres un evaluador de rendimiento de los asesores, asi que tienes que prestar mucha atención al que identifiques como el asesor.
        ***Tu objetivo es SOLO RESPONDER CON UN JSON, usa los Ejemplo como referencia para identificar frases parecidas en la trascripción, no debes usar los datos de los ejemplos si no te proporcionan suficiente información en la trasncripción***
        El objetivo del asesor es maximizar la cantidad de dinero que el cliente, para ello ejecuta estrategias de cobranza y diferentes montos escalonados (Deuda total -> LTD (Limpia tu Deuda, de 1.2 de su deuda capital) -> LTDE (Limpia tu Deuda Especial, desde 0.6 a 0.9 de su deuda capital) -> Convenios a 3 o 6 meses (dividir un pago en varias cuotas dentro del mismo mes o mes subsiguiente), Bajas 30,60 o 90 días (la última instancia, monto por el cual se aplaza el tiempo antes de que su cuenta bancaria sea castigada)).
        Estas son los campos que calificarás y que cada asesor debe , después de su descripción se muestra un ejemplo, de cumplirse, colocarás 1, de lo contrario, un 0:
        Campos de presentación:
            'pres_asert' : El asesor debe atender la llamada asumiendo que el que contestó es el titular de la deuda, mencionando el nombre del cliente. Ejemplo: “Buenos días, ¿Alberto Paredes?”.
            'pres_nom_ape' : El asesor menciona su propio nombre y apellido. Ejemplo: “Soy Valentina Soza”.
            'orig_llamada' : El asesor explica el origen de la llamada, generalmente es “llamo de la Financiera Oh” o un equivalente.
            'motiv_llamada' : El asesor indica al cliente el monto total de su deuda y que se quiere llegar a un acuerdo para pagarla. Se espera que el primer monto mencionado sea su deuda total. Ejemplo: “Mi motivo de esta llamada es porque presenta una deuda de 2000 soles y quisiera ayudarle a llegar a un acuerdo para pagarla”.
        Campos de negociación:
            'motiv_no_pago' : Se espera que el asesor pregunte el motivo de no pago del cliente, sin embargo, a veces el cliente la menciona sin que el asesor lo pregunte, en ese caso, considerar este campo como cumplido. Ejemplo: “¿A qué se debe que no pudo realizar el pago de la deuda?”.
            'manejo_objec' : A el motivo de no pago del cliente, dar alternativas de solución de pago (por lo menos una), lo esperado es que a cada motivo de no pago del cliente, el asesor debe ofrecer una opción de pago cada vez más accesible. Ejemplo: “Entiendo que no pueda pagar a totalidad de su deuda, usted cuenta con una promoción de Liquida tu deuda pagando solo 1200 soles”.
            'opciones_pago' : Se espera que el asesor pase a través de todas las opciones de pago disponibles desde el monto más alto (deuda total), hasta el más bajo (bajas).
            'beneficio_pago' : Se espera que el asesor explique los beneficios de pagar la deuda pendiente. Ejemplo: “Al cancelar esta deuda en su totalidad podrá volver a tener acceso a créditos”.
            'fecha_hora_pago' : Se espera que el asesor sea el que tome la iniciativa y proponga una fecha y monto probables a pagar, preguntas como “¿Cuándo puede pagar?” o “Cuánto puede pagar?”, no deberían hacerse.
        Campos de cierre:
            'datos_adicionales' : Se espera que el asesor solicite siempre algún otro teléfono de contacto, WhatsApp o correo. (Incluso aunque el cliente no se lo brinde, se evalúa el intento mas no el resultado). Ejemplo: “¿Podría brindarme otro número de contacto en caso no pueda atender desde el primero?”.
            'confirm_monto' : Se espera que el asesor repita el monto de pago acordado. Ejemplo: “Según lo conversado estamos quedando con un pago de 1200 soles”.
            'confirm_fecha' : Se espera que el asesor repita la fecha y hora acordadas: “Según lo conversado estamos quedando que el pago se realizará el día 20 de octubre a las 2pm”.
            'confirm_canal' : Se espera que el asesor mencione los medios y canales por los cuales se puede realizar el pago. Ejemplo: “Puede realizar el pago en ‘Plaza Vea’ u “Oeshle”.
            'consec_pago' : El asesor debe comunicar al cliente las consecuencias negativas de incumplir o no realizar el pago en la fecha y hora acordadas. Ejemplo: “Ok, Alberto, según lo coordinado si incumples la promesa de pago no podremos brindártela nuevamente en el futuro, y la oferta se anulará”.        
        Este es el formato en el que debes responder:
        {
            "presentacion":{"pres_asert": "1","pres_nom_ape": "0","orig_llamada": "1","motiv_llamada": "1"},
            "negociacion":{"motiv_no_pago": "1","manejo_objec": "0","opciones_pago": "0","beneficio_pago": "1","fecha_hora_pago":"0"},
            "cierre":{"datos_adicionales": "1", "confirm_monto": "0", "confirm_fecha": "1","confirm_canal":"0","consec_pago": "1"},
            "summary":"Explicar el motivo por el cual se puso 1 o 0 en cada campo de evaluación, detalladamente"
        }
        Ejemplo de summary: "La agente preguntó por Carlos Aguirre (pres_asert) se presentó como Victoria Valle (pres_nom_ape), explicó que llamaba de la financiera 'Oh' (orig_llamada) y explica que se debe a el pago de una deuda de 1000 soles (motiv_llamada)"
        """},{
               "role": "user",
               "content":f"""{text}"""}],
        temperature=0.33,
        stream=False
        )
        return completion.choices[0].message.content
    
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
        #cleaned_response = full_response.replace('\n', '')
        
        # Limpiar espacios y saltos de línea
        #cleaned_response = full_response.replace('\n', '')
        # Verificar si falta la llave de cierre
        if not full_response.endswith('}'):
            full_response += '}'

        return full_response.strip()  # Devolver solo la respuesta consolidada y limpia
    
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None

def insert_result(db_connection, filename, classification):
    cursor = db_connection.cursor()
    query = """
    INSERT INTO AUDIOS_EVALUACIONES (filename, pres_asert, pres_nom_ape, orig_llamada, motiv_llamada, motiv_no_pago, manejo_objec, opciones_pago, beneficio_pago, fecha_hora_pago, datos_adicionales, confirm_monto, confirm_fecha, confirm_canal, consec_pago, summary)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        "GPT-"+filename if usar_GPT ==True else "OLLAMA-"+filename,
        classification["presentacion"]["pres_asert"],
        classification["presentacion"]["pres_nom_ape"],
        classification["presentacion"]["orig_llamada"],
        classification["presentacion"]["motiv_llamada"],
        classification["negociacion"]["motiv_no_pago"],
        classification["negociacion"]["manejo_objec"],
        classification["negociacion"]["opciones_pago"],
        classification["negociacion"]["beneficio_pago"],
        classification["negociacion"]["fecha_hora_pago"],
        classification["cierre"]["datos_adicionales"],
        classification["cierre"]["confirm_monto"],
        classification["cierre"]["confirm_fecha"],
        classification["cierre"]["confirm_canal"],
        classification["cierre"]["consec_pago"],
        classification["summary"]
    )

    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()

def main():
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**db_config)
        if db_connection.is_connected():
            print("Conexión exitosa a la base de datos.")
            for filename in os.listdir("./audio_files/CR_AUDIOS"):#pdp
                if filename.endswith(".txt"):
                    with open(os.path.join("./audio_files/CR_AUDIOS", filename), 'r',  encoding='utf-8') as file:#pdp
                        content = file.read()
                        classification = classify_text(content)
                        print("EVALUACION: ")
                        print(classification)
                        if classification is not None:
                            try:
                                json_object = json.loads(classification)
                                insert_result(db_connection, filename,  json_object)
                            except json.JSONDecodeError:
                                print(f"Respuesta no válida para {filename}:    {classification}")

            print("Evaluacion completada y datos guardados en la base de datos.")
        else:
            print("No se pudo conectar a la base de datos.")
        

    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()

if __name__ == "__main__":
    main()
