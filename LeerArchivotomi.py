import csv
import os
def leerArchivo(archivo: str) -> list:
    procesosLeidos = []
    try:
        with open(archivo) as archivo: #Abrimos el archivo en modo lectura, con el nombre "archivo".
            archivoLeido = csv.reader(archivo, delimiter=",") #Separamos el archivo leido en una matriz.
            for proceso in archivoLeido:
                proc = {} #creamos el diccionario.
                proc["id"] = int(proceso[0])
                proc["tam"] = int(proceso[1])
                proc["tiempoArribo"] = int(proceso[2])
                proc["tiempoIrrupcion"] = int(proceso[3])
                proc["estado"] = None 
                proc["tiempoEspera"] = 0
                proc["tiempoRestante"] = int(proceso[3])
                proc["particion"] = None
                procesosLeidos.append(proc) #agregamos el campo estado.

            procesosLeidos.sort(key = lambda x: x["tiempoArribo"])
        
        return procesosLeidos
    except IOError:
        return 1
    except ValueError:
        return 2

os.system("cls")
print(leerArchivo("archivo.csv"))