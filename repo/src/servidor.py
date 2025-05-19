import socket
import os
import logging
from datetime import datetime

# Configuración
IP = '0.0.0.0'
PORT = 5001
BUFFER_SIZE = 4096  # 4KB
LOG_FILE = 'server_log.txt'

# Configurar logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                   format='%(asctime)s - %(message)s')

def save_file(conn, address):
    try:
        # Recibir primero el nombre y tamaño del archivo
        file_info = conn.recv(BUFFER_SIZE).decode()
        file_name, file_size = file_info.split('<SEPARATOR>')
        file_size = int(file_size)
        
        # Crear directorio de recibidos si no existe
        if not os.path.exists('recibidos'):
            os.makedirs('recibidos')
            
        file_path = os.path.join('recibidos', file_name)
        
        # Recibir el archivo por chunks
        with open(file_path, 'wb') as f:
            received = 0
            while received < file_size:
                data = conn.recv(min(BUFFER_SIZE, file_size - received))
                if not data:
                    break
                f.write(data)
                received += len(data)
        
        # Registrar la transferencia
        log_msg = f"Recibido {file_name} de {address} - Tamaño: {file_size/1024:.2f} KB"
        print(log_msg)
        logging.info(log_msg)
        
        return True
        
    except Exception as e:
        logging.error(f"Error con {address}: {str(e)}")
        return False

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen(5)
        print(f"[*] Servidor escuchando en {IP}:{PORT}")
        logging.info(f"Servidor iniciado en {IP}:{PORT}")
        
        while True:
            try:
                conn, addr = s.accept()
                print(f"\nConexión establecida con {addr}")
                
                if save_file(conn, addr):
                    conn.sendall(b"Archivo recibido exitosamente")
                else:
                    conn.sendall(b"Error al recibir el archivo")
                    
                conn.close()
                
            except KeyboardInterrupt:
                print("\nCerrando servidor...")
                logging.info("Servidor detenido por el usuario")
                break
            except Exception as e:
                logging.error(f"Error en el servidor: {str(e)}")
                continue

if __name__ == "__main__":
    start_server()