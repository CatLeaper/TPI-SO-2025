"""
Módulo de visualización.
Maneja la presentación de información al usuario.
"""

from typing import List, Optional
from models.process import Process
from models.partition import Partition


class Display:
    """Maneja la visualización de información del simulador."""
    
    @staticmethod
    def clear_screen():
        """Limpia la pantalla."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def show_memory_table(partitions: List[Partition], os_size: int = 100):
        """
        Muestra la tabla de distribución de memoria.
        Según especificaciones: 100K para SO, luego particiones de 250K, 150K, 50K.
        
        Args:
            partitions: Lista de particiones
            os_size: Tamaño del sistema operativo (100K según especificaciones)
        """
        try:
            from tabulate import tabulate
            
            headers = ["Partición", "Tamaño", "Proceso", "Frag. Interna"]
            table_data = []
            
            # Sistema operativo
            table_data.append(["SO", f"{os_size}K", "SO", "---"])
            
            # Particiones
            for partition in partitions:
                process_id = partition.process.id if partition.process else "Libre"
                frag = f"{partition.internal_fragmentation}K" if partition.process else "---"
                table_data.append([
                    partition.id,
                    f"{partition.size}K",
                    process_id,
                    frag
                ])
            
            print("\n" + "="*60)
            print("DISTRIBUCIÓN DE MEMORIA")
            print("="*60)
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print("="*60 + "\n")
            
        except ImportError:
            # Fallback sin tabulate
            print("\n" + "="*60)
            print("DISTRIBUCIÓN DE MEMORIA")
            print("="*60)
            print(f"{'Partición':<12} {'Tamaño':<10} {'Proceso':<10} {'Frag. Interna':<15}")
            print("-"*60)
            print(f"{'SO':<12} {os_size:<10}K {'SO':<10} {'---':<15}")
            for partition in partitions:
                process_id = partition.process.id if partition.process else "Libre"
                frag = f"{partition.internal_fragmentation}K" if partition.process else "---"
                print(f"{partition.id:<12} {partition.size:<10}K {process_id:<10} {frag:<15}")
            print("="*60 + "\n")
    
    @staticmethod
    def show_process_queues(processes: List[Process], ready_queue: List[int], 
                           suspended_queue: List[int], executing_id: Optional[int],
                           clock: int = 0):
        """
        Muestra las colas de procesos.
        
        Args:
            processes: Lista de todos los procesos
            ready_queue: IDs de procesos en cola de listos
            suspended_queue: IDs de procesos suspendidos
            executing_id: ID del proceso en ejecución
            clock: Tiempo actual para filtrar procesos que aún no han llegado
        """
        try:
            from tabulate import tabulate
            
            # Organizar procesos por estado
            executing = []
            ready = []
            suspended = []
            new = []
            terminated = []
            
            # Usar un set para evitar duplicados
            seen_ids = set()
            
            for process in processes:
                # Evitar mostrar el mismo proceso dos veces
                if process.id in seen_ids:
                    continue
                seen_ids.add(process.id)
                
                if process.id == executing_id:
                    executing.append(process.id)
                elif process.state.value == "Ready":
                    # Si está en ready_queue o si no se especificó la lista, mostrarlo
                    if not ready_queue or process.id in ready_queue:
                        ready.append(process.id)
                elif process.state.value == "Suspended":
                    # Si está en suspended_queue o si no se especificó la lista, mostrarlo
                    if not suspended_queue or process.id in suspended_queue:
                        suspended.append(process.id)
                elif process.state.value == "New":
                    # Solo mostrar procesos que realmente están en estado New
                    # (excluir los que aún no han llegado: arrival_time > clock)
                    if process.arrival_time <= clock:
                        new.append(process.id)
                elif process.state.value == "Terminated":
                    # Solo mostrar procesos que realmente terminaron (remaining_time debe ser 0)
                    if process.remaining_time <= 0:
                        terminated.append(process.id)
            
            table_data = [
                ["Ejecución", ", ".join(map(str, executing)) if executing else "---"],
                ["Listo", ", ".join(map(str, ready)) if ready else "---"],
                ["Listo/Suspendido", ", ".join(map(str, suspended)) if suspended else "---"],
                ["Nuevo", ", ".join(map(str, new)) if new else "---"],
                ["Terminado", ", ".join(map(str, terminated)) if terminated else "---"],
            ]
            
            print("="*60)
            print("COLAS DE PROCESOS")
            print("="*60)
            print(tabulate(table_data, headers=["Estado", "Procesos"], tablefmt="grid"))
            print("="*60 + "\n")
            
        except ImportError:
            # Fallback sin tabulate
            print("="*60)
            print("COLAS DE PROCESOS")
            print("="*60)
            print(f"{'Estado':<20} {'Procesos':<40}")
            print("-"*60)
            # Similar lógica pero con print simple
            print("="*60 + "\n")
    
    @staticmethod
    def show_statistics(processes: List[Process], clock: int):
        """
        Muestra las estadísticas finales de la simulación.
        
        Args:
            processes: Lista de todos los procesos
            clock: Tiempo total de simulación
        """
        # Incluir todos los procesos que se cargaron (terminados o no)
        # Si un proceso no terminó, mostrar "N/A" en los campos correspondientes
        all_processes = sorted(processes, key=lambda p: p.id)
        terminated = [p for p in all_processes if p.state.value == "Terminated"]
        
        if not all_processes:
            print("\nNo hay procesos para mostrar estadísticas.")
            return
        
        try:
            from tabulate import tabulate
            
            headers = ["Proceso", "T. Arribo", "T. Irrupción", "T. Fin", "T. Retorno", "T. Espera"]
            table_data = []
            
            total_turnaround = 0
            total_wait = 0
            count_terminated = 0
            
            for process in all_processes:
                if process.state.value == "Terminated":
                    process.calculate_statistics()
                    table_data.append([
                        process.id,
                        process.arrival_time,
                        process.burst_time,
                        process.finish_time,
                        process.turnaround_time,
                        process.wait_time
                    ])
                    total_turnaround += process.turnaround_time
                    total_wait += process.wait_time
                    count_terminated += 1
                else:
                    # Proceso que no terminó (no cabe en memoria, etc.)
                    table_data.append([
                        process.id,
                        process.arrival_time,
                        process.burst_time,
                        "N/A",
                        "N/A",
                        process.wait_time  # Mostrar tiempo de espera acumulado
                    ])
            
            # Promedios solo de procesos terminados
            if count_terminated > 0:
                avg_turnaround = total_turnaround / count_terminated
                avg_wait = total_wait / count_terminated
            else:
                avg_turnaround = 0
                avg_wait = 0
            throughput = count_terminated / clock if clock > 0 else 0
            
            table_data.append(["PROMEDIOS", "---", "---", "---", 
                              f"{avg_turnaround:.2f}", f"{avg_wait:.2f}"])
            
            print("\n" + "="*80)
            print("INFORME ESTADÍSTICO")
            print("="*80)
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print("="*80)
            print(f"Rendimiento del sistema: {throughput:.4f} procesos/unidad de tiempo")
            print("="*80 + "\n")
            
        except ImportError:
            # Fallback sin tabulate
            print("\n" + "="*80)
            print("INFORME ESTADÍSTICO")
            print("="*80)
            print(f"{'Proceso':<10} {'T. Arribo':<12} {'T. Irrupción':<15} "
                  f"{'T. Fin':<10} {'T. Retorno':<12} {'T. Espera':<12}")
            print("-"*80)
            for process in sorted(terminated, key=lambda p: p.id):
                process.calculate_statistics()
                print(f"{process.id:<10} {process.arrival_time:<12} {process.burst_time:<15} "
                      f"{process.finish_time:<10} {process.turnaround_time:<12} {process.wait_time:<12}")
            print("="*80 + "\n")
    
    @staticmethod
    def show_time(clock: int):
        """Muestra el tiempo actual de simulación."""
        print(f"\n{'='*60}")
        print(f"TIEMPO: {clock}")
        print(f"{'='*60}")
    
    @staticmethod
    def wait_for_continue():
        """Espera a que el usuario presione Enter."""
        input("\nPresione Enter para continuar...")

