"""
Planificador de Procesos.
Implementa algoritmo SRTF (Shortest Remaining Time First).
"""

from typing import List, Optional
from models.process import Process, ProcessState


class Scheduler:
    """Planifica la ejecución de procesos usando SRTF."""
    
    def __init__(self):
        """Inicializa el planificador SRTF."""
        self.current_process: Optional[Process] = None
    
    def select_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        """
        Selecciona el siguiente proceso a ejecutar usando SRTF.
        Elige el proceso con menor tiempo restante.
        
        Args:
            ready_queue: Cola de procesos listos
            
        Returns:
            El proceso seleccionado o None si la cola está vacía
        """
        if not ready_queue:
            return None
        
        # SRTF: Shortest Remaining Time First
        return min(ready_queue, key=lambda p: p.remaining_time)
    
    def should_preempt(self, ready_queue: List[Process]) -> bool:
        """
        Determina si se debe hacer un cambio de contexto (preemption) con SRTF.
        Hace preemption si hay un proceso en la cola de listos con menor tiempo restante.
        
        Args:
            ready_queue: Cola de procesos listos
            
        Returns:
            True si se debe hacer preemption, False en caso contrario
        """
        if not self.current_process:
            return False
        
        # SRTF: Preemption si hay un proceso con menor tiempo restante
        if ready_queue:
            best_ready = min(ready_queue, key=lambda p: p.remaining_time)
            if best_ready.remaining_time < self.current_process.remaining_time:
                return True
        
        return False
    
    def start_execution(self, process: Process) -> None:
        """
        Inicia la ejecución de un proceso.
        
        Args:
            process: Proceso a ejecutar
        """
        self.current_process = process
        process.state = ProcessState.EXECUTING
    
    def execute_tick(self) -> Optional[Process]:
        """
        Ejecuta una unidad de tiempo del proceso actual.
        
        Returns:
            El proceso si terminó, None en caso contrario
        """
        if not self.current_process:
            return None
        
        self.current_process.remaining_time -= 1
        
        # Verificar si el proceso terminó
        if self.current_process.remaining_time <= 0:
            finished = self.current_process
            finished.state = ProcessState.TERMINATED
            self.current_process = None
            return finished
        
        return None
    
    def preempt_current(self) -> Optional[Process]:
        """
        Hace preemption del proceso actual.
        
        Returns:
            El proceso que fue preemptado
        """
        if not self.current_process:
            return None
        
        preempted = self.current_process
        preempted.state = ProcessState.READY
        self.current_process = None
        return preempted

