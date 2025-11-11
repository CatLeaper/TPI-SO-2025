"""
Gestor de Memoria.
Maneja la asignación de procesos a particiones de memoria usando Best-Fit.
"""

from typing import List, Optional
from models.partition import Partition
from models.process import Process, ProcessState


class MemoryManager:
    """Gestiona la asignación de memoria usando particiones fijas y algoritmo Best-Fit."""
    
    def __init__(self, partitions: List[Partition]):
        """
        Inicializa el gestor de memoria.
        
        Args:
            partitions: Lista de particiones de memoria disponibles
        """
        self.partitions = partitions
    
    def find_best_fit(self, process: Process) -> Optional[Partition]:
        """
        Encuentra la mejor partición para un proceso usando Best-Fit.
        
        Args:
            process: Proceso a asignar
            
        Returns:
            La mejor partición o None si no hay espacio disponible
        """
        best_partition = None
        min_fragmentation = float('inf')
        
        for partition in self.partitions:
            if partition.is_free() and partition.size >= process.size:
                fragmentation = partition.size - process.size
                if fragmentation < min_fragmentation:
                    min_fragmentation = fragmentation
                    best_partition = partition
        
        return best_partition
    
    def allocate_process(self, process: Process) -> bool:
        """
        Asigna un proceso a memoria usando Best-Fit.
        
        Args:
            process: Proceso a asignar
            
        Returns:
            True si se asignó correctamente, False en caso contrario
        """
        partition = self.find_best_fit(process)
        
        if partition is None:
            return False
        
        # Si la partición ya tiene un proceso, lo movemos a disco (suspendido)
        if not partition.is_free():
            old_process = partition.free()
            if old_process:
                old_process.state = ProcessState.SUSPENDED
                old_process.partition = None
        
        # Asignar el nuevo proceso
        partition.assign_process(process)
        process.state = ProcessState.READY
        return True
    
    def free_process(self, process: Process) -> None:
        """
        Libera la memoria ocupada por un proceso.
        
        Args:
            process: Proceso a liberar
        """
        if process.partition:
            process.partition.free()
            process.partition = None
    
    def get_memory_status(self) -> List[dict]:
        """
        Obtiene el estado actual de la memoria.
        
        Returns:
            Lista de diccionarios con información de cada partición
        """
        status = []
        for partition in self.partitions:
            status.append({
                'id': partition.id,
                'size': partition.size,
                'start_address': partition.start_address,
                'process_id': partition.process.id if partition.process else None,
                'internal_fragmentation': partition.internal_fragmentation,
                'free': partition.is_free()
            })
        return status

