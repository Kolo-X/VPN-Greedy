import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import time
import math
import os
import threading

# Define la clase principal de la aplicación de transferencia de archivos VPN
class VPNFileTransferApp:
    # Método constructor de la clase
    def __init__(self, root):
        self.root = root  # Ventana principal de la aplicación
        self.root.title("Implementación de Dijkstra (File Transfer Optimizer)")  # Título de la ventana
        self.root.geometry("800x600")  # Dimensiones iniciales de la ventana

        # Grafo de conexiones: representa la red con nodos y latencias (pesos en ms)
        self.graph = {
            "Dispositivo": {"ClienteRemotoVPN": 8.84, "Speedtest": 7.594},
            "ClienteRemotoVPN": {"Dispositivo": 8.84, "Speedtest": 15.0},
            "Speedtest": {"Dispositivo": 7.594, "ClienteRemotoVPN": 15.0}
        }
        # Asegura que todos los nodos mencionados en las conexiones internas
        # también sean claves de primer nivel en el grafo para consistencia.
        all_nodes = set(self.graph.keys())
        for node in self.graph:
            all_nodes.update(self.graph[node].keys())
        for node in all_nodes:
            if node not in self.graph:
                self.graph[node] = {}  # Añade nodos faltantes con conexiones vacías

        self.selected_files = []  # Lista para almacenar las rutas de los archivos seleccionados
        self.selected_device = tk.StringVar()  # Variable para almacenar el dispositivo destino seleccionado
        self.test_size = tk.StringVar(value="10 MB")  # Variable para el tamaño del archivo de prueba, con valor inicial
        self.active_transfers = 0  # Contador de simulaciones de transferencia activas
        self.total_progress = 0.0  # Progreso total acumulado para la barra de progreso (usa float para precisión)
        self.progress_lock = threading.Lock()  # Objeto Lock para sincronizar el acceso a variables compartidas por hilos
        self.running = True #variable para controlar el hilo

        # Llama al método para crear los elementos de la interfaz gráfica
        # Esta llamada se mantiene aquí para asegurar que la GUI se construya al instanciar la clase.
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Método para encontrar la ruta óptima (menor latencia) usando el algoritmo de Dijkstra
    def find_optimal_path(self, start_node, destination_node):
        if start_node not in self.graph or destination_node not in self.graph:
            return math.inf, []

        shortest_paths = {node: (math.inf, []) for node in self.graph}
        shortest_paths[start_node] = (0, [start_node])
        unvisited_nodes = set(self.graph.keys())

        while unvisited_nodes:
            if not self.running:
                return math.inf, []
            current_node = min(unvisited_nodes, key=lambda node: shortest_paths[node][0])
            
            if shortest_paths[current_node][0] == math.inf:
                break
            
            unvisited_nodes.remove(current_node)

            for neighbor, latency in self.graph.get(current_node, {}).items():
                if neighbor not in shortest_paths:
                    continue

                potential_latency = shortest_paths[current_node][0] + latency
                if potential_latency < shortest_paths[neighbor][0]:
                    shortest_paths[neighbor] = (potential_latency, shortest_paths[current_node][1] + [neighbor])
        
        path_info = shortest_paths.get(destination_node)
        if path_info and path_info[0] != math.inf:
            return path_info
        else:
            return math.inf, []

    # Método que simula la transferencia de un solo archivo (ejecutado en un hilo separado)
    def simulate_transfer_for_one_file_thread(self, file_name_for_log, actual_file_size_bytes, destination_node, num_total_files_in_batch):
        try:
            if not self.running:
                return
            with self.progress_lock:
                self.active_transfers += 1
            self.root.after(0, self.update_transfer_counter_display)

            size_mb = actual_file_size_bytes / (1024 * 1024)
            self.root.after(0, self.log_message, f"\n--- Iniciando simulación para: {file_name_for_log} ({size_mb:.2f} MB) ---")
            
            start_node = "Dispositivo"
            
            optimal_latency_ms, optimal_path_nodes = self.find_optimal_path(start_node, destination_node)
            transfer_time_optimal_s = math.inf

            if not self.running:
                return

            if optimal_latency_ms != math.inf and optimal_path_nodes:
                transfer_time_optimal_s = size_mb * (optimal_latency_ms / 100.0)
                self.root.after(0, self.log_message, f"  Ruta Óptima: {' → '.join(optimal_path_nodes)}")
                self.root.after(0, self.log_message, f"   Latencia (Óptima): {optimal_latency_ms:.2f} ms")
                self.root.after(0, self.log_message, f"   Tiempo Estimado (Óptima): {transfer_time_optimal_s:.2f} s")
            else:
                self.root.after(0, self.log_message, "  Ruta Óptima: No encontrada o no aplicable.")

            direct_latency_ms = self.graph.get(start_node, {}).get(destination_node, math.inf)
            
            if not self.running:
                return
            if direct_latency_ms != math.inf:
                transfer_time_direct_s = size_mb * (direct_latency_ms / 100.0)
                self.root.after(0, self.log_message, f"  Ruta Directa: {start_node} → {destination_node}")
                self.root.after(0, self.log_message, f"   Latencia (Directa): {direct_latency_ms:.2f} ms")
                self.root.after(0, self.log_message, f"   Tiempo Estimado (Directa): {transfer_time_direct_s:.2f} s")
            else:
                self.root.after(0, self.log_message, "  Ruta Directa: No disponible o no aplicable.")
            if not self.running:
                return
            if transfer_time_optimal_s != math.inf and transfer_time_optimal_s > 0:
                self.root.after(0, self.log_message, f"  Simulando transferencia (vía óptima) para {file_name_for_log}...")
                simulation_steps = 100
                for i in range(1, simulation_steps + 1):
                    if not self.running:
                        return
                    time.sleep(transfer_time_optimal_s / simulation_steps)
                    
                    with self.progress_lock:
                        progress_this_step = (1.0 / simulation_steps) * (100.0 / num_total_files_in_batch)
                        self.total_progress += progress_this_step
                        current_overall_progress = min(100.0, self.total_progress)
                        self.root.after(0, self.update_progress_display, current_overall_progress)
                self.root.after(0, self.log_message, f"  ¡Simulación para {file_name_for_log} (vía óptima) completada!")

            elif transfer_time_optimal_s == 0:
                self.root.after(0, self.log_message, f"  Transferencia (óptima) para {file_name_for_log} es instantánea (tiempo 0s).")
                with self.progress_lock:
                    self.total_progress += (100.0 / num_total_files_in_batch)
                    current_overall_progress = min(100.0, self.total_progress)
                    self.root.after(0, self.update_progress_display, current_overall_progress)
                self.root.after(0, self.log_message, f"  ¡Simulación para {file_name_for_log} (vía óptima) completada!")
            else:
                self.root.after(0, self.log_message, f"  No se puede simular transferencia para {file_name_for_log} (ruta óptima no viable).")

        except Exception as e:
            self.root.after(0, self.log_message, f"Error durante simulación de {file_name_for_log}: {str(e)}")
        finally:
            with self.progress_lock:
                self.active_transfers -= 1
            self.root.after(0, self.update_transfer_counter_display)
            if self.active_transfers == 0:
                self.root.after(0, self.log_message, "--- Todas las simulaciones de este lote han finalizado. ---")

    # Método para iniciar la simulación de un archivo de prueba
    def transfer_test_file(self):
        destination = self.selected_device.get()
        if not destination:
            messagebox.showerror("Error", "Selecciona un dispositivo destino.")
            return

        size_map = {"10 MB": 10 * 1024 * 1024, "100 MB": 100 * 1024 * 1024, "1 GB": 1024 * 1024 * 1024}
        actual_file_size_bytes = size_map.get(self.test_size.get())
        if actual_file_size_bytes is None:
            messagebox.showerror("Error", "Tamaño de archivo de prueba no válido.")
            return
            
        file_name_for_log = f"Archivo de prueba ({self.test_size.get()})"

        with self.progress_lock:
            self.total_progress = 0.0
        self.update_progress_display(0)
        self.log_message(f"\n>>> Iniciando lote de simulación para archivo de prueba...")

        thread = threading.Thread(
            target=self.simulate_transfer_for_one_file_thread,
            args=(file_name_for_log, actual_file_size_bytes, destination, 1),
            daemon=True
        )
        thread.start()

    # Método para iniciar la simulación de los archivos seleccionados por el usuario
    def transfer_selected_files(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No hay archivos seleccionados.")
            return

        destination = self.selected_device.get()
        if not destination:
            messagebox.showerror("Error", "Selecciona un dispositivo destino.")
            return

        with self.progress_lock:
            self.total_progress = 0.0
        self.update_progress_display(0)
        
        num_total_files_in_batch = len(self.selected_files)
        self.log_message(f"\n>>> Iniciando lote de simulación para {num_total_files_in_batch} archivos seleccionados...")

        for file_path in self.selected_files:
            try:
                actual_file_size_bytes = os.path.getsize(file_path)
                file_name_for_log = os.path.basename(file_path)
            except Exception as e:
                self.log_message(f"Error al acceder al archivo {file_path}: {str(e)}")
                continue

            thread = threading.Thread(
                target=self.simulate_transfer_for_one_file_thread,
                args=(file_name_for_log, actual_file_size_bytes, destination, num_total_files_in_batch),
                daemon=True
            )
            thread.start()

#_____________________________________INICIO DEL GUI_____________________________________#

    def create_widgets(self): #creamos la interfaz grafia
        style = ttk.Style()
        style.theme_use("xpnative")  # Uso de un tema ya establecido

# Defininimos un estilo para los botones
        style.configure("BotonAzul.TButton",
                        background="#007ACC",    # Azul
                        foreground="Black",      # Texto negro
                        font=("Segoe UI", 10, "bold"),
                        padding=6)

# Estilo cuando el botón está activo 
        style.map("BotonAzul.TButton",
                  background=[("active","#005A9E")],  # Azul más oscuro al presionar
                  foreground=[("disabled", "blue")])

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(style="TFrame")

        file_frame = ttk.LabelFrame(main_frame, text="Selección de Archivos", padding="10")
        file_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            file_frame,
            text="Abrir",
            command=self.select_files,
            style="BotonAzul.TButton"
        ).pack(side=tk.LEFT, padx=5) #pone el boton a la izquieda
        
        self.file_listbox = tk.Listbox(file_frame, height=5, selectmode=tk.EXTENDED) #select mopde extended permite seleccionar mas de un archivo
        self.file_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        config_frame = ttk.LabelFrame(main_frame, text="Configuración de Simulación", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Dispositivo Destino:").grid(row=0, column=0, sticky=tk.W)
        #obtiene los nombres de nuestra la lista de grafos
        devices = list(self.graph.get("Dispositivo", {}).keys())
        #En caso de que no estuvieran en la lista
        if not devices:
            devices = ["ClienteRemotoVPN", "Speedtest"]

        self.device_combo = ttk.Combobox(
            config_frame,
            textvariable=self.selected_device,
            values=devices,
            state="readonly"
        )
        self.device_combo.grid(row=0, column=1, sticky=tk.EW, padx=5)
        if devices:
            self.device_combo.current(0)
#boton que nos da opciones del tamaño de los archivos de prueba
        ttk.Label(config_frame, text="Tamaño de Archivo de Prueba:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(
            config_frame,
            textvariable=self.test_size,
            values=["10 MB", "100 MB", "1 GB"],
            state="readonly",
            
        ).grid(row=1, column=1, sticky=tk.EW, padx=5)
#Boton de simular transferencia de los archivos de prueba
        ttk.Button(
            config_frame,
            text="Simular Transferencia de Prueba",
            command=self.transfer_test_file,
            style="BotonAzul.TButton",
        ).grid(row=2, column=0, columnspan=2, pady=10)
#Boton de simular transferencia de los archivos seleccionados
        ttk.Button(
            config_frame,
            text="Simular Transferencia de Seleccionados",
            command=self.transfer_selected_files,
            style="BotonAzul.TButton"
        ).grid(row=3, column=0, columnspan=2, pady=5)

        log_frame = ttk.LabelFrame(main_frame, text="Vista previa de la simulacion", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        #cambia la fuente de lo que muestra en la simulacion

        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate', length=300)
        self.progress.pack(fill=tk.X, pady=5)
        self.progress["maximum"] = 100
        #no logre que se viera la barra

        self.transfer_counter_label = ttk.Label(main_frame, text="Simulaciones activas: 0")
        self.transfer_counter_label.pack(pady=(2,5))
        #etiqueta que muestra las simulaciones en proceso

    def select_files(self):
        files = filedialog.askopenfilenames(title="Seleccionar archivos para simular transferencia")
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, tk.END)
            for file_path in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
            self.log_message(f"Se seleccionaron {len(self.selected_files)} archivos.")
            #Añade un mensaje al área de texto si el GUI está corriendo.

    def log_message(self, message):
        if self.running and self.root.winfo_exists() and self.log_text.winfo_exists():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()

    def update_transfer_counter_display(self):
        if self.running and self.root.winfo_exists() and self.transfer_counter_label.winfo_exists():
            self.transfer_counter_label.config(text=f"Simulaciones activas: {self.active_transfers}")

    def update_progress_display(self, value):
        if self.running and self.root.winfo_exists() and self.progress.winfo_exists():
            self.progress["value"] = value
            self.root.update_idletasks()

    def on_closing(self):
        self.running = False  
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()  # Crea la ventana
    app = VPNFileTransferApp(root)
    root.mainloop()