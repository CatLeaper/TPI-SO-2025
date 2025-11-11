"""
Modelo de Partición de Memoria.
Representa una partición fija de memoria principal.
"""

from typing import Optional
from .process import Process


class Partition:
    """Representa una partición de memoria fija."""
    
    def __init__(self, id: int, size: int, start_address: int):
        """
        Inicializa una partición de memoria.
        
        Args:
            id: Identificador único de la partición
            size: Tamaño de la partición en KB
            start_address: Dirección de inicio en memoria
        """
        self.id = int(id)
        self.size = int(size)
        self.start_address = int(start_address)
        self.process: Optional[Process] = None
        self.internal_fragmentation = 0
    
    def is_free(self) -> bool:
        """Verifica si la partición está libre."""
        return self.process is None
    
    def assign_process(self, process: Process) -> bool:
        """
        Asigna un proceso a esta partición.
        
        Args:
            process: Proceso a asignar
            
        Returns:
            True si se asignó correctamente, False en caso contrario
        """
        if not self.is_free():
            return False
        
        if self.size < process.size:
            return False
        
        self.process = process
        self.internal_fragmentation = self.size - process.size
        process.partition = self
        return True
    
    def free(self) -> Optional[Process]:
        """
        Libera la partición y retorna el proceso que estaba asignado.
        
        Returns:
            El proceso que estaba asignado, o None si estaba libre
        """
        if self.is_free():
            return None
        
        freed_process = self.process
        self.process.partition = None
        self.process = None
        self.internal_fragmentation = 0
        return freed_process
    
    def __repr__(self):
        """Representación legible de la partición."""
        process_id = self.process.id if self.process else "Libre"
        return (f"Partition(id={self.id}, size={self.size}K, "
                f"start={self.start_address}, process={process_id}, "
                f"frag={self.internal_fragmentation}K)")

