import os
import subprocess
from datetime import datetime

def check_directory(directory):
    # Verificar si la carpeta existe
    if not os.path.exists(directory):
        print(f"Error: El directorio {directory} no existe.")
        return False
    
    # Listar todos los archivos .wav en el directorio
    files = [f for f in os.listdir(directory) if f.endswith('.WAV') and os.path.isfile(os.path.join(directory, f))]
    
    if not files:
        print(f"Error: No se encontraron archivos .wav en el directorio {directory}.")
        return False
    
    return True

def diarize_files_in_directory(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.WAV') and os.path.isfile(os.path.join(directory, f))]
    
    for file in files:
        command = [
            'python', "diarize.py",
            '-a', os.path.join(directory, file),
            '--whisper-model', 'medium',
            '--device', 'cuda',
            '--language', 'es'
            #,'--no-stem'
        ]
        
        try:
            print(f"Ejecutando: {command}")
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print(result.stdout)  # Imprimir salida estándar
            print(f"Ejecutado: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar {command}: {e.stderr}")

def run_classifier():
    command = ['python', 'classifier.py']
    try:
        print(f"Ejecutando: {command}")
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)  # Imprimir salida estándar
        print(f"Ejecutado: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {command}: {e.stderr}")

if __name__ == "__main__":
    directory_path = 'audio_files/PDP_audios'

    print(f"Hora de inicio: {datetime.now()}")  # Hora de inicio
    
    if check_directory(directory_path):
        diarize_files_in_directory(directory_path)
        run_classifier()
    
    print(f"Hora de finalización: {datetime.now()}")  # Hora de finalización
