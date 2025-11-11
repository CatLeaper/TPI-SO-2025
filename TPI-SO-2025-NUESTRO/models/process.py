"""
Modelo de Proceso.
Representa un proceso en el sistema operativo simulado.
"""

from enum import Enum


class ProcessState(Enum):
    """Estados posibles de un proceso."""
    NEW = "New"
    READY = "Ready"
    EXECUTING = "Executing"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"


class Process:
    """Representa un proceso en el simulador."""
    
    def __init__(self, id: int, size: int, arrival_time: int, burst_time: int):
        """
        Inicializa un proceso.
        
        Args:
            id: Identificador único del proceso
            size: Tamaño en KB que ocupa en memoria
            arrival_time: Tiempo de arribo al sistema
            burst_time: Tiempo de irrupción (duración de ejecución)
        """
        self.id = int(id)
        self.size = int(size)
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        
        # Estado inicial
        self.state = ProcessState.NEW
        self.remaining_time = int(burst_time)
        self.partition = None
        
        # Estadísticas
        self.wait_time = 0
        self.finish_time = 0
        self.turnaround_time = 0
        self.first_execution_time = None  # Tiempo en que se ejecuta por primera vez
    
    @property
    def state_str(self) -> str:
        """Retorna el estado como string."""
        return self.state.value
    
    def calculate_statistics(self):
        """
        Calcula las estadísticas del proceso al terminar.
        Tiempo de espera = Tiempo desde que llega hasta que entra al procesador por primera vez
        """
        self.turnaround_time = self.finish_time - self.arrival_time
        
        # Calcular tiempo de espera: desde que llega hasta que se ejecuta por primera vez
        if self.first_execution_time is not None:
            # Tiempo de espera = Tiempo de primera ejecución - Tiempo de arribo
            self.wait_time = self.first_execution_time - self.arrival_time
        else:
            # Si nunca se ejecutó, usar la fórmula estándar
            # (pero esto no debería pasar para procesos terminados)
            self.wait_time = self.turnaround_time - self.burst_time
    
    def __repr__(self):
        """Representación legible del proceso."""
        return (f"Process(id={self.id}, size={self.size}K, "
                f"arrival={self.arrival_time}, burst={self.burst_time}, "
                f"state={self.state_str})")

