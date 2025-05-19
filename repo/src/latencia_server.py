import socket

HOST = '0.0.0.0'
PORT = 5002  # Puerto diferente al del servidor de archivos

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Servidor de latencia escuchando en {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                try:
                    data = conn.recv(1024)
                    if data.startswith(b'PING'):
                        conn.sendall(b'PONG' + data[4:])  # Eco del timestamp
                except Exception as e:
                    print(f"Error con {addr}: {e}")

if __name__ == "__main__":
    start_server()