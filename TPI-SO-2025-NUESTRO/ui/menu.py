"""
Módulo de menú.
Maneja la interfaz de usuario por consola.
"""

import os
from typing import Optional, List
from models.process import Process
from services.file_reader import FileReader
from ui.display import Display


class Menu:
    """Maneja la interfaz de menú del simulador."""
    
    def __init__(self):
        """Inicializa el menú."""
        self.display = Display()
    
    def show_main_menu(self):
        """Muestra el menú principal."""
        self.display.clear_screen()
        print("="*60)
        print("SIMULADOR DE ASIGNACIÓN DE MEMORIA Y PLANIFICACIÓN")
        print("="*60)
        print("\n1. Cargar archivo de procesos")
        print("2. Salir")
        print("\n" + "="*60)
    
    def get_file_input(self) -> Optional[str]:
        """
        Solicita al usuario el nombre del archivo.
        
        Returns:
            Nombre del archivo o None si se cancela
        """
        print("\nIngrese el nombre del archivo CSV (o 'cancelar' para volver):")
        filename = input("> ").strip()
        
        if filename.lower() == 'cancelar':
            return None
        
        # Agregar extensión .csv si no la tiene
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        return filename
    
    def load_file(self) -> Optional[List[Process]]:
        """
        Carga un archivo de procesos.
        
        Returns:
            Lista de procesos o None si hubo error
        """
        filename = self.get_file_input()
        
        if filename is None:
            return None
        
        processes = FileReader.read_processes(filename)
        
        if processes:
            FileReader.preview_processes(processes)
            confirm = input("¿Confirmar carga? (s/n): ").strip().lower()
            
            if confirm == 's' or confirm == 'si' or confirm == 'sí':
                return processes
            else:
                print("Carga cancelada.")
                input("\nPresione Enter para continuar...")
                return None
        else:
            input("\nPresione Enter para continuar...")
            return None
    
    def show_simulation_options(self) -> dict:
        """
        Muestra opciones de configuración de simulación.
        
        Returns:
            Diccionario con las opciones seleccionadas
        """
        self.display.clear_screen()
        print("="*60)
        print("CONFIGURACIÓN DE SIMULACIÓN")
        print("="*60)
        
        # Algoritmo de planificación - Solo SRTF según especificaciones
        print("\nAlgoritmo de planificación: SRTF (Shortest Remaining Time First)")
        algorithm = 'SRTF'
        
        # Grado de multiprogramación
        dom_input = input("\nGrado de multiprogramación (default=5): ").strip()
        try:
            degree_of_multiprogramming = int(dom_input) if dom_input else 5
        except ValueError:
            degree_of_multiprogramming = 5
        
        # Particiones de memoria según especificaciones del TP
        print("\nConfiguración de particiones de memoria:")
        print("1. Configuración del TP (250K, 150K, 50K) - POR DEFECTO")
        print("2. Configuración alternativa (60K, 120K, 250K)")
        print("3. Personalizada")
        
        part_choice = input("\nSeleccione (1-3, default=1): ").strip()
        
        if part_choice == '2':
            partitions = [
                {'id': 1, 'size': 60, 'start': 100},
                {'id': 2, 'size': 120, 'start': 161},
                {'id': 3, 'size': 250, 'start': 281}
            ]
        elif part_choice == '3':
            partitions = []
            print("\nIngrese las particiones (formato: id,tamaño,dirección_inicio):")
            print("Ejemplo: 1,100,200")
            print("Escriba 'fin' para terminar")
            part_id = 1
            while True:
                part_input = input(f"Partición {part_id}: ").strip()
                if part_input.lower() == 'fin':
                    break
                try:
                    parts = part_input.split(',')
                    if len(parts) == 3:
                        partitions.append({
                            'id': int(parts[0]),
                            'size': int(parts[1]),
                            'start': int(parts[2])
                        })
                        part_id += 1
                except ValueError:
                    print("Formato inválido. Intente nuevamente.")
        else:
            # Configuración según especificaciones del TP:
            # 100K para SO (no se crea partición, es reservado)
            # 250K, 150K, 50K para procesos
            partitions = [
                {'id': 1, 'size': 250, 'start': 100},  # Trabajos grandes
                {'id': 2, 'size': 150, 'start': 350},  # Trabajos medianos
                {'id': 3, 'size': 50, 'start': 500}    # Trabajos pequeños
            ]
        
        return {
            'algorithm': algorithm,
            'degree_of_multiprogramming': degree_of_multiprogramming,
            'partitions': partitions
        }
    
    def wait_for_continue(self):
        """Espera a que el usuario presione Enter."""
        input("\nPresione Enter para continuar...")

