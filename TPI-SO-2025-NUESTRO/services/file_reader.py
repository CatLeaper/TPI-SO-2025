"""
Servicio de lectura de archivos.
Maneja la carga de procesos desde archivos CSV.
"""

import csv
import os
from typing import List, Optional
from models.process import Process


class FileReader:
    """Maneja la lectura de procesos desde archivos CSV."""
    
    @staticmethod
    def read_processes(filename: str, max_processes: int = 10) -> Optional[List[Process]]:
        """
        Lee procesos desde un archivo CSV.
        
        Args:
            filename: Nombre del archivo CSV
            max_processes: Número máximo de procesos a cargar
            
        Returns:
            Lista de procesos o None si hubo un error
        """
        if not os.path.exists(filename):
            print(f"Error: El archivo '{filename}' no existe.")
            return None
        
        processes = []
        
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                # Omitir cabecera
                try:
                    next(reader)
                except StopIteration:
                    print(f"Error: El archivo '{filename}' está vacío.")
                    return []
                
                # Leer procesos
                for row in reader:
                    if len(row) == 4 and len(processes) < max_processes:
                        try:
                            process = Process(
                                id=row[0],
                                size=row[1],
                                arrival_time=row[2],
                                burst_time=row[3]
                            )
                            processes.append(process)
                        except (ValueError, IndexError) as e:
                            print(f"Error: Fila inválida omitida: {row} - {e}")
                            continue
                    elif len(processes) >= max_processes:
                        print(f"Advertencia: Límite de {max_processes} procesos alcanzado.")
                        break
                    elif row:  # Fila no vacía pero mal formada
                        print(f"Advertencia: Fila omitida (formato inválido): {row}")
            
            if not processes:
                print(f"Error: No se pudieron cargar procesos del archivo '{filename}'.")
                return None
            
            # Ordenar por tiempo de arribo
            processes.sort(key=lambda p: p.arrival_time)
            print(f"✓ Se cargaron {len(processes)} procesos exitosamente.")
            return processes
            
        except IOError as e:
            print(f"Error de E/S al leer el archivo: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al leer el archivo: {e}")
            return None
    
    @staticmethod
    def preview_processes(processes: List[Process]) -> None:
        """
        Muestra una vista previa de los procesos cargados.
        
        Args:
            processes: Lista de procesos a mostrar
        """
        try:
            from tabulate import tabulate
            
            headers = ["IDP", "TAM", "TA", "TI"]
            table_data = []
            
            for process in processes:
                table_data.append([
                    process.id,
                    f"{process.size}K",
                    process.arrival_time,
                    process.burst_time
                ])
            
            print("\n" + "="*50)
            print("VISTA PREVIA DE PROCESOS")
            print("="*50)
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print("="*50 + "\n")
            
        except ImportError:
            # Fallback si tabulate no está instalado
            print("\n" + "="*50)
            print("VISTA PREVIA DE PROCESOS")
            print("="*50)
            print(f"{'IDP':<5} {'TAM':<8} {'TA':<5} {'TI':<5}")
            print("-"*50)
            for process in processes:
                print(f"{process.id:<5} {process.size:<8}K {process.arrival_time:<5} {process.burst_time:<5}")
            print("="*50 + "\n")

