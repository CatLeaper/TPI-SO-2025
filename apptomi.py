from LeerArchivo import leerArchivo
import os
from tabulate import tabulate

memoria = [] #Creamos un arreglo para la memoria principal.
memoria.append({"idPart": 0, "dirInicio": 0, "tam": 60, "idProc": None, "fragInt": None, "libre": True }) #Agregamos las tres particiones de la MP.
memoria.append({"idPart": 1, "dirInicio": 61, "tam": 120, "idProc": None, "fragInt": None, "libre": True})
memoria.append({"idPart": 2, "dirInicio": 121, "tam": 250, "idProc": None, "fragInt": None, "libre": True})

disco = []
colaEjec = []
tiempo = 0
contQ = 0
contEjec = 0
cambio = False #Variable que sirve para controlar que en el último paso haya habido un cambio para mostrarlo.

def menuPrincipal(): #Función que muestra el menú principal. 
    print("Menu:\n")
    print("1- Cargar archivo")
    print("2- Salir\n")
    seleccionPrincipal=input("Ingrese una opcion: ") #Depende de lo ingresado por usuario, iremos a la interfaz correspondientes. 
    if seleccionPrincipal == "1":
        os.system("cls")
        vistaPrevia()
    elif seleccionPrincipal == "2":
        return
    else:
        os.system("cls")
        print("ERROR: Ingrese una opcion valida.\n")
        menuPrincipal()

def vistaPrevia():
    global procesos #Definimos como variable global.
    archivo = input("Ingrese el nombre del archivo a leer.\n\nEl archivo debe ser de tipo CSV y estar en la misma carpeta que el programa.\n\n")
    if ".csv" not in archivo:
        archivo += ".csv"
    procesos = [] #Al principio no se tiene nada cargado, por lo que tenemos una lista vacía. 
    procesos = leerArchivo(archivo)
    
    if procesos == 1:
        os.system("cls")
        print('ERROR: Archivo no encontrado, intente nuevamente.')
        vistaPrevia()
    elif procesos == 2:
        os.system("cls")
        print('ERROR: Archivo invalido, revise sus valores e intente nuevamente.')
        vistaPrevia()
    else:
        matInicio= [["IDP","TAM","TA","TI"]]
        for proceso in procesos:
            matInicio.append([proceso["id"], proceso["tam"], proceso["tiempoArribo"], proceso["tiempoIrrupcion"]]) 

        print("\nVISTA PREVIA DE PROCESOS: ")    
        print(tabulate(matInicio, 
            headers='firstrow', 
            tablefmt='fancy_grid',
            stralign='center',
            numalign='center',
            floatfmt='.0f'))
            
        print("\n¿Confirmar?\n")
        print("1- Aceptar")
        print("2- Cancelar\n")
        confirmarArchivo = input("Ingrese una opción: ") #Solicita confirmación para arrancar el simulador.
        
        if confirmarArchivo == "1":
            os.system("cls")
            simulador()
        elif confirmarArchivo =="2":
            os.system("cls")
            menuPrincipal()
        else:
            os.system("cls")
            print("ERROR: Ingrese una opcion valida.\n")
            vistaPrevia()
    return

def agregarProcesosInicio():
    global procesos
    for proceso in procesos:
        if proceso['tiempoArribo'] == 0: #Controlamos qué procesos entran en el tiempo 0. 
            if hayEspacioEnMP(proceso) == True:
                cargarMP(proceso)
            else:
                cargarDisco(proceso)
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
    return

def hayEspacioEnMP(proceso: list) -> bool:
    global memoria
    for particion in memoria:
        if particion["libre"] == True:
            if particion["tam"] >= proceso["tam"]:
                return True
    return False

def cargarMP(proceso: list) -> None:
    global memoria, procesos, cambio
    partMenorFrag = -1
    menorFrag = 999
    for particion in memoria: #Busca la mejor partición para guardar el proceso, siguiendo el algoritmo best-fit.
        if particion["libre"] == True:
            if particion["tam"] >= proceso["tam"]:
                if (particion["tam"] - proceso["tam"]) < menorFrag:
                    menorFrag = particion["tam"] - proceso["tam"]
                    partMenorFrag = particion["idPart"]

    if memoria[partMenorFrag]["idProc"] != None: #Si hay un proceso en la partición, se lo pasa a disco.
        for p in procesos:
            if p["id"] == memoria[partMenorFrag]["idProc"]:
                cargarDisco(p)

    memoria[partMenorFrag]["idProc"] = proceso["id"] #Colocamos el proceso en la partición que menor frag int dio. 
    memoria[partMenorFrag]["libre"] = False
    memoria[partMenorFrag]["fragInt"] = menorFrag #Asignamos la fragmentación interna, calculada en el bucle.
    proceso["estado"] = "Listo"
    proceso["particion"] = partMenorFrag #Guardamos la posición de la partición que ocupa el proceso.
    cambio = True

def cargarDisco(proceso: list) -> None:
    global disco
    proceso["estado"] = "Listo/Suspendido"
    proceso["particion"] = None
    disco.append(proceso["id"])

def cargarColaEjec(proceso: list) -> None:
    colaEjec.append(proceso["id"]) 

def ejecutar() -> None:
    global procesos, colaEjec, contEjec
    for proceso in procesos:
        if proceso["id"] == colaEjec[contEjec]:
            proceso["estado"] = "Ejecucion"

def agregarListosEjec() -> None:
    for proceso in procesos:
        if proceso["estado"] == "Listo" and proceso["id"] not in colaEjec: 
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
            else:
                return

def agregarLSEjec() -> None:
    for proceso in procesos:
        if proceso["estado"] == "Listo/Suspendido" and proceso["id"] not in colaEjec: 
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
            else:
                return

def agregarNuevosEjec() -> None:
    global tiempo
    for proceso in procesos:
        if len(colaEjec) < 5:
            if proceso["tiempoArribo"] == tiempo:
                cargarColaEjec(proceso)
            elif proceso["tiempoArribo"] > tiempo:
                return
        else:
            return
            
def cargarEjecMemoria() -> None:
    global colaEjec, procesos, memoria, disco
    for i in range(contEjec, len(colaEjec)): 
        for proceso in procesos:
            if proceso["id"] == colaEjec[i] and hayEspacioEnMP(proceso):
                if (proceso["particion"] == None):
                    cargarMP(proceso)
                else:
                    memoria[proceso["particion"]]["libre"]=False
                
                if proceso["id"] in disco:
                    disco.remove(proceso["id"])
    
    for i in range(0, contEjec): 
        for proceso in procesos:
            if proceso["id"] == colaEjec[i] and hayEspacioEnMP(proceso):
                if (proceso["particion"] == None):
                    cargarMP(proceso)
                else:
                    memoria[proceso["particion"]]["libre"]=False

                if proceso["id"] in disco:
                    disco.remove(proceso["id"])


def cargarLSMemoria() -> None:
    global colaEjec, procesos, memoria, disco
    for proceso in procesos:
        if proceso["estado"] == "Listo/Suspendido":
            if hayEspacioEnMP(proceso):
                cargarMP(proceso)
                disco.remove(proceso["id"])

def cargarNuevosMemoria() -> None:
    global colaEjec, procesos, memoria, tiempo
    for proceso in procesos:
        if proceso["tiempoArribo"] == tiempo and proceso["estado"] == None:
            if proceso["particion"] == None:
                if hayEspacioEnMP(proceso):
                    cargarMP(proceso)
                else:
                    cargarDisco(proceso)
        elif proceso["tiempoArribo"] > tiempo:
            return

def avanzarTiempo() -> None:
    global memoria, procesos, tiempo, contQ, contEjec, colaEjec, cambio
    tiempo += 1
    contQ += 1

    for proceso in procesos: #Actualizar tiempos para cada proceso
        if proceso["estado"] == "Listo" or proceso["estado"] == "Listo/Suspendido":
            proceso["tiempoEspera"] += 1
        if proceso["estado"] == "Ejecucion":
            proceso["tiempoRestante"] -= 1
            if proceso["tiempoRestante"] == 0:
                contQ = 0
                memoria[proceso["particion"]]["libre"] = True    
                memoria[proceso["particion"]]["idProc"] = None
                memoria[proceso["particion"]]["fragInt"] = 0
                proceso["estado"] = "Terminado"
                proceso["particion"] = None
                colaEjec.remove(proceso["id"])
                cambio = True

            elif contQ == 2:
                contQ = 0
                contEjec += 1
                proceso["estado"] = "Listo"
                memoria[proceso["particion"]]["libre"] = True
                cambio = True     

    if contEjec == len(colaEjec):
        contEjec = 0

def mostrarTablas() -> None:
    global memoria, procesos, tiempo
    matMemoria=[['Particion','Tamaño','Proceso','FI'],
                [memoria[0]["idPart"], memoria[0]["tam"], memoria[0]["idProc"], memoria[0]["fragInt"]],
                [memoria[1]["idPart"], memoria[1]["tam"], memoria[1]["idProc"], memoria[1]["fragInt"]],
                [memoria[2]["idPart"], memoria[2]["tam"], memoria[2]["idProc"], memoria[2]["fragInt"]]
                ]
    matProcesos=[['Colas', 'Procesos'],
                ['Ejecución', ""],
                ['Listo', ""],
                ['Listo/Suspendido', ""],
                ['Cola Ejecución', ""],
                ]
    for proceso in procesos:
        if proceso["estado"]== "Ejecucion":
            matProcesos[1][1] = str(proceso["id"])
        elif proceso["estado"]== "Listo":
            matProcesos[2][1] += (str(proceso["id"])+' ')
        elif proceso["estado"]== "Listo/Suspendido":
            matProcesos[3][1] += (str(proceso["id"])+' ')

    for proceso in colaEjec:
        matProcesos[4][1] += (str(proceso)+' ')

    print(tabulate([["Tiempo: " + str(tiempo)]], 
        tablefmt='fancy_grid',
        stralign='center'))

    print('\nDISTRIBUCIÓN DE MEMORIA:')
    print(tabulate(matMemoria, 
        headers='firstrow', 
        tablefmt='fancy_grid',
        stralign='center',
        numalign='center',
        floatfmt='.0f'))
    
    print('\nCOLAS DE PROCESOS:')
    print(tabulate(matProcesos, 
        headers='firstrow', 
        tablefmt='fancy_grid',
        stralign='center',
        numalign='center',
        floatfmt='.0f'))
    
    input("\nPulse para continuar...\n")

def mostrarEstadisticas():
    promEspera = 0
    promRetorno = 0
    print('\nINFORME ESTADÍSTICO:')
    matEst = [['Proceso', 'TR', 'TE']]
    for proceso in procesos:
        matEst.append([proceso["id"], proceso["tiempoIrrupcion"] + proceso["tiempoEspera"], proceso["tiempoEspera"]])
        promEspera += proceso["tiempoEspera"]
        promRetorno += proceso["tiempoIrrupcion"] + proceso["tiempoEspera"]
    promEspera = round(promEspera / len(procesos),2)
    promRetorno = round(promRetorno / len(procesos),2)
    matEst.append(["Promedios", promRetorno, promEspera])

    print(tabulate(matEst, 
        headers='firstrow', 
        tablefmt='fancy_grid',
        stralign='center',
        numalign='center'))

def simulador() -> None:
    global memoria, procesos, disco, colaEjec, tiempo, contQ, contEjec, cambio
    
    agregarProcesosInicio()

    while len(colaEjec)>0: #Bucle principal del simulador. Se ejecuta hasta que no queden procesos para ejecutar.        
        
        ejecutar()
        
        if cambio:
            mostrarTablas()
            cambio = False
        
        avanzarTiempo()
        agregarListosEjec()
        agregarLSEjec()
        agregarNuevosEjec()
        cargarEjecMemoria()
        cargarLSMemoria()
        cargarNuevosMemoria()
    
    mostrarTablas()
    
    print(tabulate([["Simulación terminada."]], 
        tablefmt='fancy_grid',
        stralign='center'))

    mostrarEstadisticas()

    input("\nPulse para terminar...")

    return

os.system("cls")
menuPrincipal()
