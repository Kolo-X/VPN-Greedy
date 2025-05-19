import socket
import os
import time
import logging

# Configuración
SERVER_IP = '100.115.229.55'  # Cambiar por IP del servidor
PORT = 5001
BUFFER_SIZE = 4096  # 4KB
LOG_FILE = 'client_log.txt'

# Configurar logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                   format='%(asctime)s - %(message)s')

def send_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            start_time = time.time()
            s.connect((SERVER_IP, PORT))
            
            # Enviar metadatos primero
            s.sendall(f"{file_name}<SEPARATOR>{file_size}".encode())
            
            # Enviar archivo por chunks
            with open(file_path, 'rb') as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    s.sendall(bytes_read)
            
            # Recibir confirmación
            response = s.recv(BUFFER_SIZE).decode()
            end_time = time.time()
            
            # Calcular métricas
            transfer_time = end_time - start_time
            speed = (file_size / 1024) / transfer_time  # KB/s
            
            log_msg = (f"Archivo {file_name} enviado a {SERVER_IP} - "
                      f"Tamaño: {file_size/1024:.2f} KB - "
                      f"Tiempo: {transfer_time:.2f}s - "
                      f"Velocidad: {speed:.2f} KB/s")
            
            print(log_msg)
            logging.info(log_msg)
            
            return {
                'status': 'success',
                'file_name': file_name,
                'file_size': file_size,
                'transfer_time': transfer_time,
                'speed': speed,
                'response': response
            }
            
    except Exception as e:
        error_msg = f"Error al enviar {file_path}: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    file_to_send = input("Ingrese la ruta del archivo a enviar: ")
    if os.path.exists(file_to_send):
        result = send_file(file_to_send)
        print("\nResultado de la transferencia:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print(f"Error: El archivo {file_to_send} no existe")