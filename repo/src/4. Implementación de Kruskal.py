import networkx as nx
import matplotlib.pyplot as plt

def generar_topologia():
    #Conexiones entre nodos con su respectivo ancho de banda remplezar con las ip a ver que se nos ocurre
    edges = [
        ("A", "B", 90),
        ("A", "C", 40),
        ("B", "C", 70),
        ("B", "D", 20),
        ("C", "D", 50),
        ("C", "E", 60),
        ("D", "E", 30)
    ]

    #Grafo original con los anchos de banda reales
    G_original = nx.Graph()
    for u, v, bandwidth in edges:
        G_original.add_edge(u, v, weight=bandwidth)

    #Se invierten los pesos para elegir los mayores anchos de banda
    G_invertido = nx.Graph()
    for u, v, bandwidth in edges:
        G_invertido.add_edge(u, v, weight=-bandwidth)

    #Se aplica Kruskal sobre los pesos invertiso
    mst_invertido = nx.minimum_spanning_tree(G_invertido, algorithm='kruskal')

    #Recuperamos los valores originales de los pesos en positivos
    mst = nx.Graph()
    for u, v, data in mst_invertido.edges(data=True):
        mst.add_edge(u, v, weight=-data["weight"])

    #Imprimir las conexiones elegidas por Kruskal
    print("\nTopología optimizada (Kruskal):")
    for u, v, data in mst.edges(data=True):
        print(f"{u} - {v}: {data['weight']} Mbps")

    pos = nx.spring_layout(G_original, seed=42)

    #grafo original
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    nx.draw(G_original, pos, with_labels=True, node_color='skyblue', node_size=800, font_size=10)
    labels_original = {(u, v): f"{d['weight']} Mbps" for u, v, d in G_original.edges(data=True)}
    nx.draw_networkx_edge_labels(G_original, pos, edge_labels=labels_original)
    plt.title("Topología de la red (original)")

    #MST con Kruskal
    plt.subplot(1, 2, 2)
    nx.draw(mst, pos, with_labels=True, node_color='lightgreen', node_size=800, font_size=10, edge_color='green')
    labels_mst = {(u, v): f"{d['weight']} Mbps" for u, v, d in mst.edges(data=True)}
    nx.draw_networkx_edge_labels(mst, pos, edge_labels=labels_mst)
    plt.title("Topología optimizada (Kruskal)")

    plt.tight_layout()
    plt.show()

generar_topologia()
