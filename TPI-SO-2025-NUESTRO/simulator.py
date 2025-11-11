"""
Simulador Principal.
Orquesta la simulación de asignación de memoria y planificación de procesos.
"""

from typing import List, Optional
from models.process import Process, ProcessState
from models.partition import Partition
from services.memory_manager import MemoryManager
from services.scheduler import Scheduler
from ui.display import Display


class Simulator:
    """Simulador principal del sistema operativo."""
    
    def __init__(self, partitions: List[Partition], 
                 degree_of_multiprogramming: int = 5):
        """
        Inicializa el simulador.
        
        Args:
            partitions: Lista de particiones de memoria
            degree_of_multiprogramming: Grado de multiprogramación (máximo de procesos en memoria)
            algorithm: Algoritmo de planificación a usar
        """
        self.partitions = partitions
        self.degree_of_multiprogramming = degree_of_multiprogramming
        self.clock = 0
        
        # Componentes del sistema
        self.memory_manager = MemoryManager(partitions)
        self.scheduler = Scheduler()  # Solo SRTF
        self.display = Display()
        
        # Colas de procesos
        self.all_processes: List[Process] = []  # Procesos que aún no han llegado
        self.loaded_processes: List[Process] = []  # Todos los procesos cargados (para estadísticas)
        self.new_queue: List[Process] = []
        self.ready_queue: List[Process] = []
        self.suspended_queue: List[Process] = []
        self.terminated_queue: List[Process] = []
        
        # Control de eventos para visualización
        self.new_process_arrived = False
        self.process_finished = False
    
    def load_processes(self, processes: List[Process]):
        """
        Carga los procesos en el simulador.
        
        Args:
            processes: Lista de procesos a simular
        """
        self.all_processes = processes.copy()
        self.loaded_processes = processes.copy()  # Guardar todos los procesos para estadísticas
        self.new_queue = []
        self.ready_queue = []
        self.suspended_queue = []
        self.terminated_queue = []
        self.clock = 0
    
    def _arrive_new_processes(self):
        """Maneja la llegada de nuevos procesos."""
        arrived = []
        remaining = []
        
        for process in self.all_processes:
            if process.arrival_time == self.clock:
                process.state = ProcessState.NEW
                arrived.append(process)
                self.new_process_arrived = True  # Marcar que llegó un nuevo proceso
            elif process.arrival_time > self.clock:
                remaining.append(process)
            # Los que ya llegaron se manejan en otras colas
        
        self.all_processes = remaining
        
        # Intentar cargar los nuevos procesos a memoria
        for process in arrived:
            self._try_load_to_memory(process)
    
    def _try_load_to_memory(self, process: Process):
        """
        Intenta cargar un proceso a memoria.
        
        Args:
            process: Proceso a cargar
        """
        # Verificar grado de multiprogramación
        current_dom = len(self.ready_queue) + (1 if self.scheduler.current_process else 0)
        
        if current_dom >= self.degree_of_multiprogramming:
            # No hay espacio, ir a suspendidos
            process.state = ProcessState.SUSPENDED
            if process not in self.suspended_queue:
                self.suspended_queue.append(process)
            return
        
        # Intentar asignar memoria
        if self.memory_manager.allocate_process(process):
            if process not in self.ready_queue:
                self.ready_queue.append(process)
            if process in self.suspended_queue:
                self.suspended_queue.remove(process)
        else:
            # No cabe en memoria, ir a suspendidos
            process.state = ProcessState.SUSPENDED
            if process not in self.suspended_queue:
                self.suspended_queue.append(process)
    
    def _try_load_suspended(self):
        """Intenta cargar procesos suspendidos a memoria."""
        current_dom = len(self.ready_queue) + (1 if self.scheduler.current_process else 0)
        
        if current_dom >= self.degree_of_multiprogramming:
            return
        
        # Intentar cargar suspendidos
        to_remove = []
        for process in self.suspended_queue:
            if current_dom >= self.degree_of_multiprogramming:
                break
            
            if self.memory_manager.allocate_process(process):
                if process not in self.ready_queue:
                    self.ready_queue.append(process)
                to_remove.append(process)
                current_dom += 1
        
        for process in to_remove:
            self.suspended_queue.remove(process)
    
    def _update_wait_times(self):
        """
        Actualiza los tiempos de espera de los procesos.
        Solo cuenta el tiempo para procesos que están esperando ANTES de ejecutarse por primera vez.
        Una vez que un proceso se ejecuta, ya no cuenta más tiempo de espera.
        """
        # Actualizar tiempo de espera solo para procesos que NO están ejecutándose
        # y que AÚN NO se han ejecutado por primera vez
        executing_id = self.scheduler.current_process.id if self.scheduler.current_process else None
        
        for process in self.ready_queue + self.suspended_queue:
            # Solo actualizar si:
            # 1. El proceso está esperando (READY o SUSPENDED)
            # 2. NO es el que está ejecutándose ahora
            # 3. AÚN NO se ha ejecutado por primera vez (first_execution_time es None)
            if (process.state == ProcessState.READY or process.state == ProcessState.SUSPENDED) and \
               process.id != executing_id and \
               process.first_execution_time is None:
                process.wait_time += 1
    
    def _schedule_process(self):
        """Planifica el siguiente proceso a ejecutar."""
        # Verificar si hay que hacer preemption
        if self.scheduler.should_preempt(self.ready_queue):
            preempted = self.scheduler.preempt_current()
            if preempted and preempted not in self.ready_queue:
                self.ready_queue.append(preempted)
        
        # Seleccionar siguiente proceso
        if not self.scheduler.current_process:
            next_process = self.scheduler.select_next_process(self.ready_queue)
            if next_process:
                # Marcar la primera vez que se ejecuta (para calcular tiempo de espera)
                if next_process.first_execution_time is None:
                    next_process.first_execution_time = self.clock
                self.scheduler.start_execution(next_process)
                if next_process in self.ready_queue:
                    self.ready_queue.remove(next_process)
    
    def _execute_tick(self):
        """Ejecuta una unidad de tiempo."""
        finished = self.scheduler.execute_tick()
        
        if finished:
            # Validar que el proceso realmente terminó
            if finished.remaining_time <= 0 and finished.state == ProcessState.TERMINATED:
                # Proceso terminado
                # finish_time es el tiempo al final del tick actual (clock + 1)
                finished.finish_time = self.clock + 1
                finished.calculate_statistics()
                self.memory_manager.free_process(finished)
                # Solo agregar si no está ya en la cola
                if finished not in self.terminated_queue:
                    self.terminated_queue.append(finished)
                self.scheduler.current_process = None
                self.process_finished = True  # Marcar que terminó un proceso
    
    def run(self):
        """
        Ejecuta la simulación.
        Muestra salida cada vez que llega un nuevo proceso o termina uno en ejecución.
        No permite corridas ininterrumpidas.
        """
        print("\n" + "="*60)
        print("INICIANDO SIMULACIÓN")
        print("="*60)
        print("Algoritmo: SRTF (Shortest Remaining Time First)")
        print("="*60)
        
        # Contar procesos totales
        total_processes = len(self.all_processes)
        
        # Bucle principal
        max_ticks = 1000  # Límite de seguridad
        while len(self.terminated_queue) < total_processes:
            
            if self.clock >= max_ticks:
                print(f"\nAdvertencia: Simulación detenida por límite de tiempo ({max_ticks} ticks).")
                break
            
            # Resetear flags de eventos
            self.new_process_arrived = False
            self.process_finished = False
            
            # 1. Llegada de nuevos procesos
            self._arrive_new_processes()
            
            # 2. Intentar cargar suspendidos a memoria
            self._try_load_suspended()
            
            # 3. Planificar proceso (ANTES de actualizar tiempos de espera)
            self._schedule_process()
            
            # 4. Actualizar tiempos de espera (solo para procesos que NO están ejecutándose)
            # Esto se hace DESPUÉS de planificar para no contar el tiempo si se ejecuta
            self._update_wait_times()
            
            # 5. Ejecutar tick
            self._execute_tick()
            
            # 6. Mostrar estado si llegó un nuevo proceso o terminó uno
            if self.new_process_arrived or self.process_finished:
                self.display.show_time(self.clock)
                self.display.show_memory_table(self.partitions)
                # Construir lista completa de procesos activos
                # Incluir todos los procesos que ya llegaron (no los que están en all_processes esperando llegar)
                # Usar listas separadas para evitar duplicados
                all_active_processes = []
                seen_ids = set()
                
                # Agregar proceso en ejecución (si hay uno)
                if self.scheduler.current_process:
                    if self.scheduler.current_process.id not in seen_ids:
                        all_active_processes.append(self.scheduler.current_process)
                        seen_ids.add(self.scheduler.current_process.id)
                
                # Agregar procesos de ready_queue
                for p in self.ready_queue:
                    if p.id not in seen_ids:
                        all_active_processes.append(p)
                        seen_ids.add(p.id)
                
                # Agregar procesos de suspended_queue
                for p in self.suspended_queue:
                    if p.id not in seen_ids:
                        all_active_processes.append(p)
                        seen_ids.add(p.id)
                
                # Agregar procesos terminados (solo los que realmente terminaron)
                for p in self.terminated_queue:
                    if p.id not in seen_ids and p.state == ProcessState.TERMINATED:
                        all_active_processes.append(p)
                        seen_ids.add(p.id)
                self.display.show_process_queues(
                    all_active_processes,
                    [p.id for p in self.ready_queue],
                    [p.id for p in self.suspended_queue],
                    self.scheduler.current_process.id if self.scheduler.current_process else None,
                    self.clock
                )
                self.display.wait_for_continue()
            
            # 7. Avanzar reloj
            self.clock += 1
        
        # Mostrar estado final
        self.display.show_time(self.clock)
        self.display.show_memory_table(self.partitions)
        all_processes_list = self.ready_queue + self.suspended_queue + self.terminated_queue
        self.display.show_process_queues(
            all_processes_list,
            [p.id for p in self.ready_queue],
            [p.id for p in self.suspended_queue],
            self.scheduler.current_process.id if self.scheduler.current_process else None,
            self.clock
        )
        
        # Mostrar estadísticas finales
        print("\n" + "="*60)
        print("SIMULACIÓN FINALIZADA")
        print("="*60)
        # Pasar todos los procesos cargados para estadísticas (no solo los activos)
        self.display.show_statistics(self.loaded_processes, self.clock)

