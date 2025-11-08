#Creacion del Lector para archivo.csv
import csv
import os

# Intentamos importar 'tabulate'.
try:
    # Esta es la librería que dibuja la tabla
    from tabulate import tabulate
except ImportError:
    print("---------------------------------------------------------------")
    print("Error: La librería 'tabulate' no está instalada.")
    print("Para ver la tabla formateada, por favor ejecute en su terminal:")
    print("pip install tabulate")
    print("---------------------------------------------------------------")
    tabulate = None  # Ponemos 'tabulate' como None para saber que no podemos usarla

def leer_archivo_procesos(filename):
    """
    Carga los procesos desde el archivo CSV.
    Devuelve una lista de diccionarios.
    """
    
    # Verificamos que el archivo exista
    if not os.path.exists(filename):
        print(f"Error: El archivo '{filename}' no existe.")
        print("Asegúrese de que 'ArchivodeProcesos.csv' esté en la misma carpeta.")
        return None

    procesos_leidos = []
    
    # Usamos try y except para manejar errores de lectura
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            try:
                # Omitir la cabecera (ID, Tamaño, etc.)
                next(reader)  
            except StopIteration:
                print(f"Error: El archivo '{filename}' está vacío.")
                return [] # Devolvemos lista vacía

            # Recorremos cada fila del CSV
            for row in reader:
                # Nos aseguramos que la fila no esté vacía y tenga 4 columnas
                if len(row) == 4:
                    # Creamos el diccionario
                    proc = {}
                    proc["id"] = int(row[0])
                    proc["tam"] = int(row[1])
                    proc["tiempoArribo"] = int(row[2])
                    proc["tiempoIrrupcion"] = int(row[3])
                    proc["estado"] = "New"
                    proc["tiempoRestante"] = int(row[3])
                    proc["tiempoEspera"] = 0
                    proc["particion"] = None
                    
                    procesos_leidos.append(proc)
                elif row: # Si la fila no está vacía pero no tiene 4 columnas
                    print(f"Error: Omitiendo fila mal formada: {row}")
        
        # Ordenamos la lista por tiempo de arribo
        procesos_leidos.sort(key=lambda x: x["tiempoArribo"])
        
        if procesos_leidos:
            print(f"Se cargaron {len(procesos_leidos)} procesos exitosamente.")
        else:
            print("Error: El archivo se leyó pero no contenía procesos válidos.")

        return procesos_leidos

    except Exception as e:
        print(f"Error inesperado al leer el archivo CSV: {e}")
        return None

def mostrar_vista_previa(lista_procesos):
    """
    Muestra los procesos cargados en una tabla
    """
    
    # Si 'tabulate' no se pudo importar, mostramos los datos de forma simple.
    if not tabulate:
        print("No se pudo importar 'tabulate'. Mostrando datos :")
        for p in lista_procesos:
            print(p)
        return

    print("\nVISTA PREVIA DE PROCESOS:")
    
    #  Definimos los encabezados
    headers = ["IDP", "TAM", "TA", "TI"]
    
    #  Creamos una lista de listas (filas) con los datos
    tabla_datos = []
    for proc in lista_procesos:
        fila = [
            proc["id"],
            proc["tam"],
            proc["tiempoArribo"],
            proc["tiempoIrrupcion"]
        ]
        tabla_datos.append(fila)
        
    #  Imprimimos la tabla
    print(tabulate(tabla_datos, headers=headers, tablefmt="grid"))


# --- Bloque de Prueba (Actualizado) ---
if __name__ == "__main__":
    
    # Limpiamos la consola 
    # os.system('cls' if os.name == 'nt' else 'clear') # Descomentar si se desea limpiar
    
    nombre_archivo = "ArchivodeProcesos.csv"
    print(f"--- Prueba del Lector (Paso 1) ---")
    
    lista_procesos = leer_archivo_procesos(nombre_archivo)
    
    # Verificamos que la lista no sea None (error) y no esté vacía
    if lista_procesos:
        # Llamamos a la nueva función
        mostrar_vista_previa(lista_procesos)
    elif lista_procesos is None:
        print("Hubo un error al cargar los procesos.")
    else:
        print("No se cargaron procesos (el archivo podría estar vacío).")
