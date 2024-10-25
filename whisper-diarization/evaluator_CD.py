import os
import json
import requests
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
client = OpenAI()
#USAR GPT 4.0 mini
usar_GPT=True
ollama_url = "http://localhost:11434/api/generate"

db_config = {
    'host': '18.191.247.200',
    'port':'3306',
    'database': 'foh-qas',
    'user': 'foh',  # Cambia esto por tu usuario de MySQL
    'password': 'NS**!24!00',  # Cambia esto por tu contraseña de MySQL
}

# Define el directorio donde están tus archivos .txt
input_directory = "./audio_files/CD_audios"
#output_file = "classification_results.json"

def classify_text(text):
    data = {
        "model": "evaluator_CD",
        "prompt": f"""{text}""",
        "stream": False
    }
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": 
        """
        Contexto: Recibirás un audio transcrito de conversación de cobanza simulada entre dos personas: el Speaker 0 y Speaker 1.
        Uno de ellos es un agente de cobranzas de la Financiera 'Oh' y el otro un cliente. El cliente pertenece al "Tramo 5" los clientes en ese tramo tienen 100 días de mora como mínimo.
        El objetivo del asesor es maximizar la cantidad de dinero que el cliente, para ello ejecuta estrategias de cobranza y diferentes montos escalonados (Deuda total -> LTD (Limpia tu Deuda, de 1.2 de su deuda capital) -> LTDE (Limpia tu Deuda Especial, de 0.6 a 0.9 de su deuda capital) -> Convenios a 3 o 6 meses (dividir un pago en varias cuotas dentro del mismo mes o mes subsiguiente), Bajas 30,60 o 90 días (la última instancia, monto por el cual se aplaza el tiempo antes de que su cuenta bancaria sea castigada)).
        Objetivo: 
        Eres un evaluador de rendimiento de los asesores, asi que tienes que prestar mucha atención al speaker que identifiques como el asesor.
        ***Tu objetivo es SOLO RESPONDER CON UN JSON y en español en el siguiente formato (Solo puedes modificar los valores de "sí" y "no" dependiendo de la conversación):***
        {
            "presentacion":{"presentacion asertiva": "sí","se presentó usando nombre y apellido": "(si el asesor se presentó con su nombre y apellido)","explicó el origen de la llamada": "(si el asesor dijo que llamaba desde Financiera "Oh")","explicó motivo de llamada": "sí"},
            "negociacion":{"solicitó motivo de no pago": "sí","Hizo manejo de objeciones": "no","Brindó opciones de pago de manera escalonada": "no","Brindó beneficios de pago de obligación": "sí","Manejó la fecha y monto de pago":"no"},
            "cierre": {
        "Define la propuesta más cercana al cliente": "sí",
        "Logra agenda para propuesta": "no",
        "Confirma hora de la agenda": "sí",
        "Valida tomo nota de condiciones de propuesta": "no",
        "Comunica la consecuencia de no pago": "no"
    },"summary":"Explicar el motivo por el cual se puso "sí" o "no" en cada campo de evaluación"
        }

        En el formato anterior escribirás "sí" si identificas que el asesor ha cubierto ese parámetro, al final en el parámetro "summary", agregarás una justificación de tus respuestas en los parametros y por qué fueron calificados como tal.
        Ejemplo de summary: "El asesor dijo explícitamente 'Gustaría de una Baja 30?' por lo que marqué 'sí' en el campo de 'beneficios de pago de obligación', así mismo el asesor pasó de ofrecer un 'LTD' a una baja, es por eso que marqué que 'sí' en 'Brindó opciones de pago de manera escalonada'"
        Ejemplo de transcripción que recibirás: 'Speaker 0: Aló.  Speaker 1: Aló, buen día.  Speaker 0: Buenos días.  Speaker 1: Buenos días.  Me comunico con el señor Wilfredo Ramírez Reyes.  Speaker 0: Sí, de parte.  Speaker 1: Le saludo a Romina Tapia de Financiera 'Oh'.  Estamos llamando debido a que usted tiene una cuenta pendiente con nosotros y este mes tiene una promoción para que pueda liquidar la totalidad de su cuenta.
        Señor Wilfredo, ¿me escuchas?  Speaker 0: Sí, ahorita no tengo, ¿por qué?  Speaker 1: Podríamos cancelar la cuenta, señor, con tan solo 1.100 soles.  ¿Con 1.100 soles le quedamos la totalidad de esta cuenta, señor Wilfredo?  Speaker 0: Sí, pero, señorita, ahorita ya no tengo.  Pero, ¿tanto?  Sin más y luego como 500 soles.  Speaker 1: Su monto de su deuda capital es de 917 soles.  Speaker 0: porque si yo tengo los recibos que yo he pagado como más de $600 y el mes no queda $200 yo tengo los vouchers, tengo todo perfecto señor.  por eso yo le digo, por lo que yo tengo que arreglar porque yo, mire yo sé que a mí ya sino que a mí me han quedado mal en la frontera, no me pagan me han quedado con mi negocio, se han quedado.  por eso Si no yo hubiera pagado, yo estaba pagando.  Por eso yo no coje la plata porque mi negocio es tan bajo.  Y ahorita me di que en ese problema yo estoy en la frontera.  Y no me quieren pagar, todo mi negocio y me quieren volver nada.  Speaker 1: ¿Usted en dónde se encuentra, señor Wilfredo?  Speaker 0: ¿Ah?  Speaker 1: ¿Usted dónde se encuentra, dónde radica?  Speaker 0: En la frontera.  estoy ahorita porque yo soy ambulante.  Yo ando buscando trabajo y me voy.  Y voy así, voy así para... y ese día voy allá para ver que me solucionan, porque no me quieren devolver ni mi negocio, porque yo entero, yo soy comerciante ambulante.  Speaker 1: Es correcto.  Speaker 0: Por eso, es el motivo que yo quedé mal, porque si no, yo estoy pagando bien, si no me quedaron mal, porque no me quieren devolver el negocio, nada así, nada.  Eso es lo que tengo yo, porque estoy arriesgando yo ese día.  que me devuelvan porque yo les hago problemas, todo eso allá en la frontera.  Nada.  Que me espere, que me espere.  Speaker 1: En la frontera con Ecuador, señor Wilfredo?  Speaker 0: Sí, entonces voy aquí.  Yo paso la frontera.  Yo paso la frontera.  Para entregar negocios.  Por eso.  Speaker 1: ¿Cuándo me podría volver a comunicar con usted para poder coordinar su forma de pago?  Speaker 0: Yo no sé, señorita.  Yo estoy tranquilo.  Apenas me paguen, yo llamo y yo para ver cómo soluciono.  Voy abonando para que me caen, para que me den algo.  O estar por acá, porque no hay mi trabajo, no hay nada.  Por eso no, no, no, no.  Yo estoy delicado también.  Ahorita me he cogido todo.  Por esos motivos.  Si no, yo fuera pagando y yo... Quiere que me lleve un negocio y yo hago por ahí donde están y yo hago y lo llamo.  Yo tengo el número del teléfono de la de la garjeta y yo le llamo.  O me voy a plomar, voy a pagar, a ver cómo soluciono.  A depositar lo que tenga.  Speaker 1: Muy bien, señor Wilfred.  Entonces yo le estoy llamando y le voy a mandar información vía WhatsApp, ¿sí?  Para que usted ahí tenga mi número y cualquier cosa me llama.  Speaker 0: ¿Y a mí?  Ya, ya.  Speaker 1: Bendiciones, cuídense, hasta luego.  Speaker 0: Ya, ya, hasta luego.'
        Ejemplo de respuesta: "Saludó y se presentó como Romina Tapia asertivamente, explicó que llamada de Financiera Oh, no hizo hincapié en porqué el cliente no pagó, manejó las objeciones del cliente a pesar de sus excusas, ofreció multiples modos de pago. Además brindó los beneficios or bligación, sin embargo, no concretó una fecha o monto de pago, no solició datos de contacto adicionales ni expresó de que no pagar la deuda tendrá un gran problema financiero"
        """},{
        "role": "user",
        "content":f"""{text}"""}],
    temperature=0.1,
    stream=False

)
    if usar_GPT:
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
        1 if classification["presentacion"]["presentacion asertiva"] == "sí" else 0,
        1 if classification["presentacion"]["se presentó usando nombre y apellido"] == "sí" else 0,
        1 if classification["presentacion"]["explicó el origen de la llamada"] == "sí" else 0,
        1 if classification["presentacion"]["explicó motivo de llamada"] == "sí" else 0,
        1 if classification["negociacion"]["solicitó motivo de no pago"] == "sí" else 0,
        1 if classification["negociacion"]["Hizo manejo de objeciones"] == "sí" else 0,
        1 if classification["negociacion"]["Brindó opciones de pago de manera escalonada"] == "sí" else 0,
        1 if classification["negociacion"]["Brindó beneficios de pago de obligación"] == "sí" else 0,
        1 if classification["negociacion"]["Manejó la fecha y monto de pago"] == "sí" else 0,
        1 if classification["cierre"]["Define la propuesta más cercana al cliente"] == "sí" else 0,
        1 if classification["cierre"]["Logra agenda para propuesta"] == "sí" else 0,
        1 if classification["cierre"]["Confirma hora de la agenda"] == "sí" else 0,
        1 if classification["cierre"]["Valida tomo nota de condiciones de propuesta"] == "sí" else 0,
        1 if classification["cierre"]["Comunica la consecuencia de no pago"] == "sí" else 0,
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
            for filename in os.listdir("./audio_files/CD_audios"):
                if filename.endswith(".txt"):
                    with open(os.path.join("./audio_files/CD_audios", filename), 'r',  encoding='utf-8') as file:
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
