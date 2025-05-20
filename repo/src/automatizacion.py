import networkx as nx
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import time
import json
import os
from datetime import datetime

# Generar claves RSA (pública/privada)
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Serializar claves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem

# Cifrar datos con clave pública
def encrypt_data(data, public_key):
    encrypted = public_key.encrypt(
        json.dumps(data).encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

# Descifrar datos con clave privada
def decrypt_data(encrypted_data, private_key):
    decrypted = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return json.loads(decrypted.decode())

# Simular datos de red (pueden venir de una API o base de datos)
def fetch_network_data():
    return [
        ("PC1", "PC2", 100),
        ("PC1", "PC3", 85),
        ("PC2", "PC3", 50),
        ("PC3", "PC4", 95),
        ("PC2", "PC4", 40),
        ("PC1", "PC4", 60)
    ]

# Construir grafo y calcular MST
def build_and_optimize_network(data):
    G = nx.Graph()
    for n1, n2, ancho in data:
        peso = 1 / ancho
        G.add_edge(n1, n2, weight=peso, bandwidth=ancho)

    mst = nx.minimum_spanning_tree(G, weight="weight")
    return G, mst

# Guardar gráfico en un archivo (para verificación)
def save_graph_plot(G, mst, filename="network_plot.png"):
    plt.figure(figsize=(12, 5))

    # Grafo original
    plt.subplot(1, 2, 1)
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f'{d["bandwidth"]}Mbps' for u, v, d in G.edges(data=True)})
    plt.title("Topología Original")

    # MST (Kruskal)
    plt.subplot(1, 2, 2)
    nx.draw(mst, pos, with_labels=True, node_color='lightgreen', edge_color='blue')
    nx.draw_networkx_edge_labels(mst, pos, edge_labels={(u, v): f'{d["bandwidth"]}Mbps' for u, v, d in mst.edges(data=True)})
    plt.title("Topología Optimizada (Kruskal)")

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Función principal que se ejecuta cada 5 minutos
def main():
    # Generar claves RSA
    private_pem, public_pem = generate_keys()
    private_key = serialization.load_pem_private_key(private_pem, password=None)
    public_key = serialization.load_pem_public_key(public_pem)

    # Obtener datos de red
    network_data = fetch_network_data()

    # Cifrar datos antes de procesar (simulación de transporte seguro)
    encrypted_data = encrypt_data(network_data, public_key)
    print("Datos cifrados correctamente.")

    # Descifrar datos
    decrypted_data = decrypt_data(encrypted_data, private_key)
    print("Datos descifrados correctamente.")

    # Construir grafo y calcular MST
    G, mst = build_and_optimize_network(decrypted_data)

    # Guardar gráfico con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"network_plot_{timestamp}.png"
    save_graph_plot(G, mst, plot_filename)

    print(f"Grafo actualizado y guardado como: {plot_filename}")

    # Mostrar resumen de las conexiones
    print("\nResumen de conexiones óptimas (MST):")
    for u, v, d in mst.edges(data=True):
        print(f"{u} ↔ {v} | Ancho de banda: {d['bandwidth']}Mbps")

if __name__ == "__main__":
    print("Iniciando monitor de red...")
    while True:
        main()
        print("\n⏳ Esperando 5 minutos para la próxima actualización...")
        time.sleep(300)  # 300 segundos = 5 minutos