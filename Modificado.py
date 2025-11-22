from app import leer_archivo_procesos # Este archivo no se modifica
import os
from tabulate import tabulate


# Requerimiento 2023: 60, 120, 250
# Requerimiento 2025: 50, 150, 250 [cite: 55, 56]
memoria = [] 
memoria.append({"idPart": 0, "dirInicio": 0, "tam": 50, "idProc": None, "fragInt": None, "libre": True }) 
memoria.append({"idPart": 1, "dirInicio": 50, "tam": 150, "idProc": None, "fragInt": None, "libre": True})
memoria.append({"idPart": 2, "dirInicio": 200, "tam": 250, "idProc": None, "fragInt": None, "libre": True})


disco = []
colaEjec = [] # Esta sigue siendo la cola de multiprogramación (max 5)
tiempo = 0
cambio = False # Variable de control, sin cambios

# Eliminadas variables de Round-Robin contQ y contEjec ya no son necesarios para SRTF

# (Sin Cambios)
# Funciones son de muestra y carga de archivo
def menuPrincipal(): 
    print("Menu:\n")
    print("1- Cargar archivo")
    print("2- Salir\n")
    seleccionPrincipal=input("Ingrese una opcion: ") 
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
    global procesos 
    archivo = input("Ingrese el nombre del archivo a leer.\n\nEl archivo debe ser de tipo CSV y estar en la misma carpeta que el programa.\n\n")
    if ".csv" not in archivo:
        archivo += ".csv"
    procesos = [] 
    procesos = leer_archivo_procesos(archivo)
    
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
        confirmarArchivo = input("Ingrese una opción: ") 
        
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
        if proceso['tiempoArribo'] == 0: 
            if hayEspacioEnMP(proceso) == True:
                cargarMP(proceso)
            else:
                cargarDisco(proceso)
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
    return

#(Sin Cambios) Gestion de memoria por que sigue siendo Best-Fit

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
    # Lógica Best-Fit (sin cambios)
    for particion in memoria: 
        if particion["libre"] == True:
            if particion["tam"] >= proceso["tam"]:
                if (particion["tam"] - proceso["tam"]) < menorFrag:
                    menorFrag = particion["tam"] - proceso["tam"]
                    partMenorFrag = particion["idPart"]

    if partMenorFrag == -1: # Si no encontró partición
        return False # No pudo cargar

    if memoria[partMenorFrag]["idProc"] != None: 
        for p in procesos:
            if p["id"] == memoria[partMenorFrag]["idProc"]:
                cargarDisco(p)

    memoria[partMenorFrag]["idProc"] = proceso["id"] 
    memoria[partMenorFrag]["libre"] = False
    memoria[partMenorFrag]["fragInt"] = menorFrag 
    proceso["estado"] = "Listo"
    proceso["particion"] = partMenorFrag 
    cambio = True
    return True # Pudo cargar

def cargarDisco(proceso: list) -> None:
    global disco
    proceso["estado"] = "Listo/Suspendido"
    proceso["particion"] = None
    disco.append(proceso["id"])

def cargarColaEjec(proceso: list) -> None:
    if proceso["id"] not in colaEjec:
        colaEjec.append(proceso["id"]) 

# función ejecutar() se reemplaza por planificadorSRTF()

#(Sin Cambios) Gestion de colas y estados
# La lógica de cómo los procesos se mueven entre Nuevo, Listo, Listo/Suspendido
# y la cola de multiprogramación (colaEjec) no cambia.

def agregarListosEjec() -> None:
    for proceso in procesos:
        if proceso["estado"] == "Listo" and proceso["id"] not in colaEjec: 
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
            else:
                return

def agregarLSEjec() -> None:
    global disco
    procesos_en_disco_ordenados = []
    # Ordenar por tiempo de irrupción (SRTF) para desempatar
    temp_list = [p for p in procesos if p["id"] in disco]
    temp_list.sort(key=lambda x: x['tiempoRestante'])
    
    for proceso in temp_list:
        if proceso["estado"] == "Listo/Suspendido" and proceso["id"] not in colaEjec: 
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)

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
    # Cargar procesos de la cola de ejecución a memoria (si es posible)
    for i in range(len(colaEjec)): 
        for proceso in procesos:
            if proceso["id"] == colaEjec[i] and proceso["estado"] == "Listo/Suspendido": # Solo si está suspendido
                if hayEspacioEnMP(proceso):
                    if cargarMP(proceso): # Intentar cargar en MP
                        if proceso["id"] in disco:
                            disco.remove(proceso["id"])
                    
def cargarLSMemoria() -> None:
    global colaEjec, procesos, memoria, disco
    
    temp_list = [p for p in procesos if p["id"] in disco]
    temp_list.sort(key=lambda x: x['tiempoRestante']) # Priorizar por SRTF

    for proceso in temp_list:
        if proceso["estado"] == "Listo/Suspendido":
            if hayEspacioEnMP(proceso):
                if cargarMP(proceso):
                    disco.remove(proceso["id"])

def cargarNuevosMemoria() -> None:
    global colaEjec, procesos, memoria, tiempo
    
    # Ordenar los nuevos por SRTF para que se carguen primero los más cortos
    nuevos_procesos = [p for p in procesos if p["tiempoArribo"] == tiempo and p["estado"] == None]
    nuevos_procesos.sort(key=lambda x: x['tiempoRestante'])

    for proceso in nuevos_procesos:
        if proceso["particion"] == None:
            if hayEspacioEnMP(proceso):
                cargarMP(proceso)
            else:
                cargarDisco(proceso)

# Lógica de avanzarTiempo() modificada, se saco la lógica de Round-Robin (contQ, contEjec)
# La función ahora solo avanza el reloj 1 unidad y actualiza tiempos.
def avanzarTiempo() -> None:
    global memoria, procesos, tiempo, colaEjec, cambio
    tiempo += 1

    proceso_en_ejecucion = None
    for proceso in procesos: # Actualizar tiempos para cada proceso
        if proceso["estado"] == "Ejecucion":
            proceso_en_ejecucion = proceso
        elif proceso["estado"] == "Listo" or proceso["estado"] == "Listo/Suspendido":
            proceso["tiempoEspera"] += 1
    
    if proceso_en_ejecucion:
        proceso_en_ejecucion["tiempoRestante"] -= 1
        
        # Verificar si el proceso terminó
        if proceso_en_ejecucion["tiempoRestante"] == 0:
            memoria[proceso_en_ejecucion["particion"]]["libre"] = True    
            memoria[proceso_en_ejecucion["particion"]]["idProc"] = None
            memoria[proceso_en_ejecucion["particion"]]["fragInt"] = 0
            proceso_en_ejecucion["estado"] = "Terminado"
            proceso_en_ejecucion["particion"] = None
            colaEjec.remove(proceso_en_ejecucion["id"])
            cambio = True
        
        # NO HAY 'else' para quantum. En SRTF, un proceso solo
        # deja la CPU si termina o si es desalojado por el planificador.


# Reemplaza a la vieja función ejecutar() y decide quién debe ejecutarse en este instante de tiempo.

def planificadorSRTF() -> None:
    global procesos, colaEjec, cambio

    proceso_actual = None
    candidatos = [] # Procesos que pueden ejecutarse

    # 1. Buscar al proceso actualmente en ejecución
    for p in procesos:
        if p["estado"] == "Ejecucion":
            proceso_actual = p
            break
    
    # 2. Buscar todos los procesos "Listos" (en memoria y en cola)
    for id_proc in colaEjec:
        for p in procesos:
            if p["id"] == id_proc and p["estado"] == "Listo":
                candidatos.append(p)
                break
    
    # 3. El proceso actual (si existe) también es un candidato
    if proceso_actual:
        candidatos.append(proceso_actual)

    if not candidatos:
        return # No hay nada que ejecutar

    # 4. Decisión SRTF: encontrar el candidato con menor tiempo restante [cite: 59]
    proceso_a_ejecutar = min(candidatos, key=lambda x: x['tiempoRestante'])

    # 5. Lógica de Desalojo (Preemptive)
    # Si el que estaba ejecutando NO es el que debe ejecutar ahora
    if proceso_actual and proceso_actual["id"] != proceso_a_ejecutar["id"]:
        proceso_actual["estado"] = "Listo"
        # ¡Importante! No liberamos su memoria, solo fue desalojado.
        cambio = True
    
    # 6. Iniciar ejecución del proceso elegido
    if proceso_a_ejecutar["estado"] != "Ejecucion":
        proceso_a_ejecutar["estado"] = "Ejecucion"
        cambio = True



def mostrarTablas() -> None:
    global memoria, procesos, tiempo
    matMemoria=[['Particion','Tamaño','Proceso','FI'],
                [memoria[0]["idPart"], memoria[0]["tam"], memoria[0]["idProc"], memoria[0]["fragInt"]],
                [memoria[1]["idPart"], memoria[1]["tam"], memoria[1]["idProc"], memoria[1]["fragInt"]],
                [memoria[2]["idPart"], memoria[2]["tam"], memoria[2]["idProc"], memoria[2]["fragInt"]]
                ]
    matProcesos=[['Colas', 'Procesos'],
                ['Ejecución', ""],
                ['Listo (en Memoria)', ""],
                ['Listo/Suspendido (en Disco)', ""],
                ['Cola Ejecución (Multiprogramación)', ""],
                ]
    
    listos = ""
    listos_suspendidos = ""
    
    for proceso in procesos:
        if proceso["estado"]== "Ejecucion":
            matProcesos[1][1] = str(proceso["id"])
        elif proceso["estado"]== "Listo":
            listos += (str(proceso["id"])+' ')
        elif proceso["estado"]== "Listo/Suspendido":
            listos_suspendidos += (str(proceso["id"])+' ')

    matProcesos[2][1] = listos
    matProcesos[3][1] = listos_suspendidos

    for proceso_id in colaEjec:
        matProcesos[4][1] += (str(proceso_id)+' ')

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

# Añadido cálculo de Rendimiento
def mostrarEstadisticas():
    global tiempo # Necesitamos el tiempo final
    promEspera = 0
    promRetorno = 0
    num_procesos = len(procesos)

    print('\nINFORME ESTADÍSTICO:')
    matEst = [['Proceso', 'TR', 'TE']]
    for proceso in procesos:
        tr = (tiempo - proceso["tiempoArribo"]) # Tiempo de Retorno
        matEst.append([proceso["id"], tr, proceso["tiempoEspera"]])
        promEspera += proceso["tiempoEspera"]
        promRetorno += tr
    
    promEspera = round(promEspera / num_procesos, 2)
    promRetorno = round(promRetorno / num_procesos, 2)
    
    # Nuevo cálculo de Rendimiento [cite: 67]
    rendimiento = round(num_procesos / tiempo, 3)

    matEst.append(["Promedios", promRetorno, promEspera])
    matEst.append(["Rendimiento", str(rendimiento) + " proc/t", ""]) # Nueva fila

    print(tabulate(matEst, 
        headers='firstrow', 
        tablefmt='fancy_grid',
        stralign='center',
        numalign='center'))


# Bucle principal del simulador actualizado
def simulador() -> None:
    global memoria, procesos, disco, colaEjec, tiempo, cambio
    
    agregarProcesosInicio() # Carga de procesos en tiempo 0

    while True: # El bucle se ejecuta hasta que todos los procesos terminen
        
        # 1. Verificar fin de simulación
        terminados = sum(1 for p in procesos if p["estado"] == "Terminado")
        if terminados == len(procesos):
            break # Salir del bucle principal

        # 2. Cargar procesos que llegan en ESTE 'tiempo'
        cargarNuevosMemoria() 
        # 3. Mover de Disco a Memoria si hay espacio
        cargarLSMemoria() 
        # 4. Cargar de 'colaEjec' a Memoria (para los desalojados que vuelven)
        cargarEjecMemoria() 

        # 5. Llenar la cola de multiprogramación (max 5)
        agregarListosEjec()   
        agregarLSEjec()       
        agregarNuevosEjec()   

        # 6. ¡NUEVO PLANIFICADOR SRTF!
        # Decide quién debe estar en "Ejecucion"
        planificadorSRTF()
        
        # 7. Mostrar tablas si hubo un cambio
        if cambio:
            mostrarTablas()
            cambio = False
        
        # 8. Avanzar el reloj 1 unidad
        # (Esto actualizará 'tiempoRestante', 'tiempoEspera' y manejará procesos terminados)
        avanzarTiempo()
    
    mostrarTablas() # Mostrar estado final
    
    print(tabulate([["Simulación terminada."]], 
        tablefmt='fancy_grid',
        stralign='center'))

    mostrarEstadisticas()

    input("\nPulse para terminar...")
    return

os.system("cls")

menuPrincipal()
