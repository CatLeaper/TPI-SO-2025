"""
Simulador de Planificación de Procesos y Asignación de Memoria

Versión Final:
- Todo el código está en un solo archivo (como pidió el equipo).
- La lógica de carga del CSV está en una función separada
  (como propusiste tú) para mayor claridad.
"""

import csv
import os
import time

# --- 1. DEFINICIÓN DE CLASES (Modelos) ---
# (Esto es nuestro "Paso 1" original)

class Process:
    """Representa un proceso en el simulador."""
    def __init__(self, id, size, arrival_time, burst_time):
        self.id = int(id)
        self.size = int(size)
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        self.state = 'New'
        self.remaining_time = int(burst_time) 
        self.partition = None 
        
        # --- Atributos para Estadísticas ---
        self.finish_time = 0
        self.turnaround_time = 0 # T. Retorno = T. Fin - T. Arribo
        self.wait_time = 0       # T. Espera = T. Retorno - T. Irrupción

    def __repr__(self):
        """Función 'mágica' para un print legible."""
        return f"Proceso(ID: {self.id}, T_Arribo: {self.arrival_time}, T_Irrup: {self.burst_time}, Tam: {self.size}K)"

class Partition:
    """Representa una partición de memoria fija."""
    def __init__(self, id, size, start_address):
        self.id = id
        self.size = int(size)
        self.start_address = int(start_address)
        self.process = None
        self.internal_fragmentation = 0

    def is_free(self):
        """Verifica si la partición está libre."""
        return self.process is None

    def assign_process(self, process_to_assign):
        """Asigna un proceso a esta partición."""
        if self.is_free() and self.size >= process_to_assign.size:
            self.process = process_to_assign
            self.internal_fragmentation = self.size - process_to_assign.size
            process_to_assign.partition = self
            return True
        return False

    def free_process(self):
        """Libera la partición y retorna el proceso que estaba en ella."""
        if not self.is_free():
            freed_process = self.process
            self.process.partition = None
            self.process = None
            self.internal_fragmentation = 0
            return freed_process
        return None

# --- 2. FUNCIÓN AUXILIAR (Tu idea del Lector CSV) ---
# (Basado en la 'image_465703.png' que subiste)

def leer_archivo_procesos(filename="ArchivodeProcesos.csv", max_processes=10):
    """
    Carga los procesos desde el archivo CSV.
    Esta es tu función `leerArchivo`, pero adaptada para
    devolver una lista de OBJETOS Process, no diccionarios.
    """
    if not os.path.exists(filename):
        print(f"Error: No se encuentra el archivo '{filename}'.")
        return None # Devolvemos None para indicar un error
    
    procesos_leidos = []
    
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Omitir cabecera
            
            total_loaded = 0
            for row in reader:
                if len(row) == 4 and total_loaded < max_processes:
                    # ¡AQUÍ ESTÁ EL CAMBIO!
                    # En lugar de un diccionario, creamos un objeto Process
                    process = Process(
                        id=row[0], 
                        size=row[1], 
                        arrival_time=row[2], 
                        burst_time=row[3]
                    )
                    procesos_leidos.append(process)
                    total_loaded += 1
                elif total_loaded >= max_processes:
                    print(f"Advertencia: Límite de {max_processes} procesos alcanzado.")
                    break
        
        if not procesos_leidos:
            print(f"Error: El archivo '{filename}' está vacío.")
            return None

        # Ordenamos la lista por tiempo de arribo
        procesos_leidos.sort(key=lambda p: p.arrival_time)
        print(f"Simulador: Se cargaron {len(procesos_leidos)} procesos.")
        return procesos_leidos

    except (IOError, csv.Error) as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer los procesos: {e}")
        return None

# --- 3. CLASE PRINCIPAL DEL SIMULADOR ---
# (Nuestro "Paso 2" y "Paso 3")

class Simulator:
    """Clase principal que orquesta la simulación."""
    def __init__(self, degree_of_multiprogramming=5):
        self.degree_of_multiprogramming = degree_of_multiprogramming
        self.clock = 0
        self.partitions = []
        
        self.all_processes_from_csv = [] # Esta lista la llenará la función
        
        self.new_queue = []
        self.ready_queue = []
        self.suspended_queue = []
        self.executing_process = None
        self.terminated_queue = []
        
        self.setup_partitions()

    def setup_partitions(self):
        """Crea las particiones fijas."""
        self.partitions.append(Partition(id=1, size=250, start_address=100))
        self.partitions.append(Partition(id=2, size=150, start_address=350))
        self.partitions.append(Partition(id=3, size=50, start_address=500))
        print("Simulador: Particiones de memoria inicializadas.")
        self.print_memory_map()

    def find_best_fit(self, process_to_fit):
        """Encuentra la mejor partición (Best-Fit)."""
        best_partition = None
        min_fragmentation = float('inf')
        for partition in self.partitions:
            if partition.is_free() and partition.size >= process_to_fit.size:
                fragmentation = partition.size - process_to_fit.size
                if fragmentation < min_fragmentation:
                    min_fragmentation = fragmentation
                    best_partition = partition
        return best_partition

    def print_memory_map(self):
        """Muestra el estado actual de las particiones de memoria."""
        print("--- Tabla de Particiones de Memoria ---")
        print("ID  | Dir. Inicio | Tamaño | Proceso Asignado | Frag. Interna")
        print("---------------------------------------------------------------")
        print("0   | 0           | 100K   | SO               | ---")
        for p in self.partitions:
            process_id = p.process.id if p.process else "Libre"
            frag = f"{p.internal_fragmentation}K" if p.process else "---"
            print(f"{p.id:<3} | {p.start_address:<11} | {p.size:<6}K | {process_id:<16} | {frag}")
        print("---------------------------------------------------------------")

    def print_queues(self):
        """Muestra el estado de las colas de procesos."""
        print("--- Colas de Estado ---")
        print(f"Cola de Nuevos:      {[p.id for p in self.new_queue]}")
        print(f"Cola de Listos:      {[p.id for p in self.ready_queue]}")
        print(f"Cola de Suspendidos: {[p.id for p in self.suspended_queue]}")
        exec_id = self.executing_process.id if self.executing_process else "Ninguno"
        print(f"En Ejecución:      {exec_id}")
        print("-----------------------")

    def print_statistics(self):
        """Imprime el informe estadístico final."""
        print("\n--- INFORME ESTADÍSTICO FINAL ---")
        
        if not self.terminated_queue:
            print("No terminaron procesos.")
            return

        self.terminated_queue.sort(key=lambda p: p.id)
        total_turnaround = 0
        total_wait = 0
        
        print("Proceso | T. Arribo | T. Irrupción | T. Fin | T. Retorno | T. Espera")
        print("-----------------------------------------------------------------------")
        for p in self.terminated_queue:
            total_turnaround += p.turnaround_time
            total_wait += p.wait_time
            print(f"{p.id:<7} | {p.arrival_time:<9} | {p.burst_time:<12} | {p.finish_time:<6} | {p.turnaround_time:<10} | {p.wait_time:<9}")
        
        num_processes = len(self.terminated_queue)
        avg_turnaround = total_turnaround / num_processes
        avg_wait = total_wait / num_processes
        throughput = num_processes / self.clock 
        
        print("-----------------------------------------------------------------------")
        print(f"Tiempo Promedio de Retorno: {avg_turnaround:.2f}")
        print(f"Tiempo Promedio de Espera:  {avg_wait:.2f}")
        print(f"Rendimiento del sistema:    {throughput:.4f} (procesos por unidad de tiempo)")


    def run(self):
        """Ejecuta el bucle principal de la simulación."""
        
        # --- ¡AQUÍ USAMOS TU FUNCIÓN! ---
        self.all_processes_from_csv = leer_archivo_procesos("ArchivodeProcesos.csv", max_processes=10)
        
        if self.all_processes_from_csv is None:
            print("Deteniendo simulación: no se pudieron cargar los procesos.")
            return

        print(f"--- Iniciando simulación (Reloj: {self.clock}) ---")
        
        total_processes_to_run = len(self.all_processes_from_csv)
        
        # Bucle principal
        while len(self.terminated_queue) < total_processes_to_run:
            print(f"\n--- Reloj: {self.clock} ---")

            # --- 3a: LLEGADA DE NUEVOS PROCESOS ---
            new_arrivals = False
            remaining_processes = []
            for p in self.all_processes_from_csv:
                if p.arrival_time == self.clock:
                    p.state = 'New'
                    self.new_queue.append(p)
                    print(f"Llegó Proceso {p.id} (Tamaño: {p.size}K) -> Cola de Nuevos")
                    new_arrivals = True
                else:
                    remaining_processes.append(p)
            self.all_processes_from_csv = remaining_processes
            if new_arrivals:
                self.print_queues()

            
            # --- 3b: CARGA A MEMORIA (DOM) ---
            current_dom = len(self.ready_queue) + (1 if self.executing_process else 0)
            loaded_this_tick = False
            
            temp_new_queue = []
            for process in self.new_queue:
                if current_dom < self.degree_of_multiprogramming:
                    partition = self.find_best_fit(process)
                    if partition:
                        partition.assign_process(process)
                        process.state = 'Ready'
                        self.ready_queue.append(process)
                        current_dom += 1
                        loaded_this_tick = True
                        print(f"Memoria: Proceso {process.id} asignado a Partición {partition.id}")
                    else:
                        process.state = 'Suspended'
                        self.suspended_queue.append(process)
                        print(f"Memoria: Proceso {process.id} no cabe (Tamaño: {process.size}K). Movido a Suspendidos.")
                else:
                    temp_new_queue.append(process)
            self.new_queue = temp_new_queue

            temp_suspended_queue = []
            if current_dom < self.degree_of_multiprogramming:
                for process in self.suspended_queue:
                    if current_dom < self.degree_of_multiprogramming:
                        partition = self.find_best_fit(process)
                        if partition:
                            partition.assign_process(process)
                            process.state = 'Ready'
                            self.ready_queue.append(process)
                            current_dom += 1
                            loaded_this_tick = True
                            print(f"Memoria: Proceso {process.id} (Suspendido) asignado a Partición {partition.id}")
                        else:
                            temp_suspended_queue.append(process)
                    else:
                        temp_suspended_queue.append(process)
                self.suspended_queue = temp_suspended_queue
            
            if loaded_this_tick:
                self.print_memory_map()
                self.print_queues()

            
            # --- 3c: PLANIFICACIÓN CPU (SRTF) ---
            if not self.ready_queue and not self.executing_process:
                print("Planificador: CPU Ociosa.")
            else:
                best_in_ready = None
                if self.ready_queue:
                    best_in_ready = min(self.ready_queue, key=lambda p: p.remaining_time)

                if self.executing_process is None:
                    if best_in_ready:
                        print(f"Planificador: Proceso {best_in_ready.id} (T_Rest: {best_in_ready.remaining_time}) pasa a ejecución.")
                        self.executing_process = best_in_ready
                        best_in_ready.state = 'Executing'
                        self.ready_queue.remove(best_in_ready)
                
                elif best_in_ready is None:
                    print(f"Planificador: Proceso {self.executing_process.id} (T_Rest: {self.executing_process.remaining_time}) sigue ejecutando (Cola de listos vacía).")
                
                else:
                    if best_in_ready.remaining_time < self.executing_process.remaining_time:
                        print(f"Planificador: Proceso {best_in_ready.id} (T_Rest: {best_in_ready.remaining_time}) desaloja a {self.executing_process.id} (T_Rest: {self.executing_process.remaining_time}).")
                        old_process = self.executing_process
                        old_process.state = 'Ready'
                        self.ready_queue.append(old_process)
                        self.executing_process = best_in_ready
                        best_in_ready.state = 'Executing'
                        self.ready_queue.remove(best_in_ready)
                    else:
                        print(f"Planificador: Proceso {self.executing_process.id} (T_Rest: {self.executing_process.remaining_time}) sigue ejecutando (SRTF).")

            
            # --- 3d: EJECUCIÓN Y TERMINACIÓN ---
            if self.executing_process:
                self.executing_process.remaining_time -= 1
                print(f"Ejecución: Proceso {self.executing_process.id} trabajando (T_Rest: {self.executing_process.remaining_time})")

                if self.executing_process.remaining_time == 0:
                    print(f"¡PROCESO TERMINADO! (ID: {self.executing_process.id})")
                    finished_process = self.executing_process
                    finished_process.state = 'Terminated'
                    finished_process.finish_time = self.clock + 1
                    finished_process.turnaround_time = finished_process.finish_time - finished_process.arrival_time
                    finished_process.wait_time = finished_process.turnaround_time - finished_process.burst_time
                    
                    print(f"Memoria: Liberando Partición {finished_process.partition.id}")
                    finished_process.partition.free_process()
                    self.terminated_queue.append(finished_process)
                    self.executing_process = None
                    self.print_memory_map()
                    self.print_queues()
            else:
                if not self.ready_queue and self.all_processes_from_csv and not self.new_queue and not self.suspended_queue:
                    print("Ejecución: CPU Ociosa (Esperando llegadas).")
                

            # --- AVANZAR EL RELOJ ---
            self.clock += 1
            
            # --- Frenos de seguridad ---
            if self.clock > 100: 
                print("\nERROR: Simulación excede los 100 ticks. Deteniendo.")
                break
            
            if (not self.all_processes_from_csv and 
                not self.new_queue and 
                not self.ready_queue and 
                not self.suspended_queue and 
                not self.executing_process):
                
                if len(self.terminated_queue) < total_processes_to_run:
                    print(f"Simulación atascada en T={self.clock}.")
                    print("Procesos que nunca corrieron (posiblemente muy grandes):")
                    for p in self.suspended_queue:
                        print(f" - {p}")
                break
                
            # time.sleep(0.2) # Pausa para leer


        # --- FIN DE LA SIMULACIÓN ---
        print(f"\n--- Fin de la Simulación en Reloj: {self.clock} ---")
        self.print_statistics()


# --- 4. PUNTO DE ENTRADA ---
# (Aquí es donde todo comienza)

if __name__ == "__main__":
    
    # Crear el archivo CSV de prueba (si no existe)
    csv_filename = "ArchivodeProcesos.csv"
    if not os.path.exists(csv_filename):
        print(f"Creando archivo de prueba '{csv_filename}'...")
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Tamano", "TiempoArribo", "TiempoIrrupcion"])
            writer.writerow(["1", "40", "0", "8"])
            writer.writerow(["2", "200", "2", "3"])
            writer.writerow(["3", "100", "3", "4"])
            writer.writerow(["4", "300", "5", "6"])
            writer.writerow(["5", "140", "7", "2"])
    
    # 1. Crear el simulador
    simulador = Simulator(degree_of_multiprogramming=5)
    
    # 2. Ejecutar la simulación
    simulador.run()