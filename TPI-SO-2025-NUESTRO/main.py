"""
Punto de entrada principal del simulador.
"""

import sys
import os

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.partition import Partition
from simulator import Simulator
from ui.menu import Menu


def main():
    """Función principal del programa."""
    menu = Menu()
    
    while True:
        menu.show_main_menu()
        choice = input("Seleccione una opción: ").strip()
        
        if choice == '1':
            # Cargar archivo
            processes = menu.load_file()
            
            if processes:
                # Configurar simulación
                config = menu.show_simulation_options()
                
                # Crear particiones
                partitions = []
                for part_config in config['partitions']:
                    partitions.append(Partition(
                        id=part_config['id'],
                        size=part_config['size'],
                        start_address=part_config['start']
                    ))
                
                # Crear y ejecutar simulador (solo SRTF según especificaciones)
                simulator = Simulator(
                    partitions=partitions,
                    degree_of_multiprogramming=config['degree_of_multiprogramming']
                )
                
                simulator.load_processes(processes)
                
                # Ejecutar simulación (siempre muestra cuando llega proceso nuevo o termina uno)
                simulator.run()
                
                input("\nPresione Enter para volver al menú principal...")
        
        elif choice == '2':
            print("\n¡Hasta luego!")
            break
        
        else:
            print("\nOpción inválida. Por favor seleccione 1 o 2.")
            input("Presione Enter para continuar...")


if __name__ == "__main__":
    main()

