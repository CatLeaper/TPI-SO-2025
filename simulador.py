from LectorCSV import leer_archivo_procesos  
import os
from tabulate import tabulate

# Particiones de memoria fija (tamaños 50, 150, 250)
memoria = [] 
memoria.append({"idPart": 0, "dirInicio": 0, "tam": 50,  "idProc": None, "fragInt": None, "libre": True}) 
memoria.append({"idPart": 1, "dirInicio": 51, "tam": 150, "idProc": None, "fragInt": None, "libre": True})
memoria.append({"idPart": 2, "dirInicio": 151, "tam": 250, "idProc": None, "fragInt": None, "libre": True})

disco = []
colaEjec = []  # Cola de multiprogramación (max 5)
tiempo = 0
cambio = False
procesos = []  # Lista global de procesos


# Menu/Carga del archivo #

def menuPrincipal(): 
    print("Menu:\n")
    print("1- Cargar archivo")
    print("2- Salir\n")
    seleccionPrincipal = input("Ingrese una opcion: ") 
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
    archivo = input("Ingrese el nombre del archivo a leer.\n\nEl mismo debe de ser del tipo CSV y estar en la misma carpeta que el programa.\n\n")
    if ".csv" not in archivo:
        archivo += ".csv"

    procesos = leer_archivo_procesos(archivo)
    
    if procesos == 1:
        os.system("cls")
        print('ERROR: Archivo no encontrado, intente nuevamente.')
        vistaPrevia()
        return
    elif procesos == 2:
        os.system("cls")
        print('ERROR: Archivo invalido, revise sus valores e intente nuevamente.')
        vistaPrevia()
        return
    else:
        #Manejo por si hay + de 10 procesos
        total_leidos = len(procesos)
        ignorados = []
        if total_leidos > 10:
            ignorados = procesos[10:]        # procesos que NO se van a simular
            procesos = procesos[:10]         # nos quedamos con los primeros 10
            os.system("cls")
            print("ADVERTENCIA:")
            print(f"Se leyeron {total_leidos} procesos del archivo.")
            print("Solo se simularán los primeros 10. Los siguientes NO serán tenidos en cuenta:\n")
            for p in ignorados:
                print(f"  - Proceso {p['id']} (TAM={p['tam']}, TA={p['tiempoArribo']}, TI={p['tiempoIrrupcion']})")
            print()
            input("Pulse una tecla para continuar...\n")
            os.system("cls")

        #  Rechaza si existen procesos demasiados grandes
        max_part = max(part["tam"] for part in memoria)  # tamaño de la partición más grande
        procesos_invalidos = [p for p in procesos if p["tam"] > max_part]

        if procesos_invalidos:
            os.system("cls")
            print("ERROR: Hay procesos que no entran en ninguna partición de memoria fija.\n")
            print(f"Tamaño máximo permitido por las particiones: {max_part}\n")
            print("Procesos no admitidos:")
            for p in procesos_invalidos:
                print(f"  - Proceso {p['id']} (TAM={p['tam']})")
            print("\nCorrija el archivo CSV y vuelva a intentar.\n")
            input("Pulse una tecla para volver al menú...\n")
            os.system("cls")
            menuPrincipal()
            return

        # Inicializar campos internos
        for p in procesos:
            p["estado"] = None
            p["tiempoRestante"] = p["tiempoIrrupcion"]
            p["tiempoEspera"] = 0
            p["particion"] = None
            p["tiempoFinalizacion"] = None

        # Vista previa
        matInicio = [["IDP","TAM","TA","TI"]]
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
        elif confirmarArchivo == "2":
            os.system("cls")
            menuPrincipal()
        else:
            os.system("cls")
            print("ERROR: Ingrese una opcion valida.\n")
            vistaPrevia()
    return


# Memoria BEST-FIT #

def hayEspacioEnMP(proceso: list) -> bool:
    global memoria
    for particion in memoria:
        if particion["libre"] and particion["tam"] >= proceso["tam"]:
            return True
    return False


def cargarMP(proceso: list) -> bool:
    global memoria, cambio
    partMenorFrag = -1
    menorFrag = 999

    # Best-Fit entre particiones libres
    for particion in memoria: 
        if particion["libre"] and particion["tam"] >= proceso["tam"]:
            frag = particion["tam"] - proceso["tam"]
            if frag < menorFrag:
                menorFrag = frag
                partMenorFrag = particion["idPart"]

    if partMenorFrag == -1:
        return False  # No pudo cargar

    memoria[partMenorFrag]["idProc"] = proceso["id"] 
    memoria[partMenorFrag]["libre"] = False
    memoria[partMenorFrag]["fragInt"] = menorFrag 
    proceso["estado"] = "Listo"
    proceso["particion"] = partMenorFrag 
    cambio = True
    return True


def cargarDisco(proceso: list) -> None:
    global disco
    proceso["estado"] = "Listo/Suspendido"
    proceso["particion"] = None
    if proceso["id"] not in disco:
        disco.append(proceso["id"])


def cargarColaEjec(proceso: list) -> None:
    if proceso["id"] not in colaEjec:
        colaEjec.append(proceso["id"]) 


# Colas/Estados #

def agregarProcesosInicio():
    global procesos
    for proceso in procesos:
        if proceso['tiempoArribo'] == 0: 
            if hayEspacioEnMP(proceso):
                cargarMP(proceso)
            else:
                cargarDisco(proceso)
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
    return


def agregarListosEjec() -> None:
    for proceso in procesos:
        if proceso["estado"] == "Listo" and proceso["id"] not in colaEjec: 
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
            else:
                return


def agregarLSEjec() -> None:
    global disco
    temp_list = [p for p in procesos if p["id"] in disco]
    temp_list.sort(key=lambda x: x['tiempoRestante'])
    
    for proceso in temp_list:
        if proceso["estado"] == "Listo/Suspendido" and proceso["id"] not in colaEjec: 
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)


def agregarNuevosEjec() -> None:
    global tiempo
    for proceso in procesos:
        if proceso["tiempoArribo"] == tiempo and proceso["id"] not in colaEjec:
            if len(colaEjec) < 5:
                cargarColaEjec(proceso)
            else:
                break


def cargarEjecMemoria() -> None:
    global colaEjec, procesos, memoria, disco
    for pid in colaEjec: 
        for proceso in procesos:
            if proceso["id"] == pid and proceso["estado"] == "Listo/Suspendido":
                if hayEspacioEnMP(proceso) and cargarMP(proceso):
                    if proceso["id"] in disco:
                        disco.remove(proceso["id"])
                    

def cargarLSMemoria() -> None:
    global procesos, memoria, disco
    temp_list = [p for p in procesos if p["id"] in disco]
    temp_list.sort(key=lambda x: x['tiempoRestante'])

    for proceso in temp_list:
        if proceso["estado"] == "Listo/Suspendido":
            if hayEspacioEnMP(proceso) and cargarMP(proceso):
                disco.remove(proceso["id"])


def cargarNuevosMemoria() -> None:
    global procesos, memoria, tiempo
    nuevos_procesos = [p for p in procesos if p["tiempoArribo"] == tiempo and p["estado"] is None]
    nuevos_procesos.sort(key=lambda x: x['tiempoRestante'])

    for proceso in nuevos_procesos:
        if proceso["particion"] is None:
            if hayEspacioEnMP(proceso):
                cargarMP(proceso)
            else:
                cargarDisco(proceso)


#  Tiempo  #

def avanzarTiempo() -> None:
    global memoria, procesos, tiempo, colaEjec, cambio
    tiempo += 1

    proceso_en_ejecucion = None
    for proceso in procesos:
        if proceso["estado"] == "Ejecucion":
            proceso_en_ejecucion = proceso
        elif proceso["estado"] in ("Listo", "Listo/Suspendido"):
            proceso["tiempoEspera"] += 1
    
    if proceso_en_ejecucion:
        proceso_en_ejecucion["tiempoRestante"] -= 1
        
        if proceso_en_ejecucion["tiempoRestante"] == 0:
            memoria[proceso_en_ejecucion["particion"]]["libre"] = True    
            memoria[proceso_en_ejecucion["particion"]]["idProc"] = None
            memoria[proceso_en_ejecucion["particion"]]["fragInt"] = 0
            proceso_en_ejecucion["estado"] = "Terminado"
            proceso_en_ejecucion["tiempoFinalizacion"] = tiempo
            proceso_en_ejecucion["particion"] = None
            colaEjec.remove(proceso_en_ejecucion["id"])
            cambio = True


# SRTF #

def planificadorSRTF() -> None:
    global procesos, colaEjec, cambio

    proceso_actual = None
    candidatos = []

    for p in procesos:
        if p["estado"] == "Ejecucion":
            proceso_actual = p
            break
    
    for id_proc in colaEjec:
        for p in procesos:
            if p["id"] == id_proc and p["estado"] == "Listo":
                candidatos.append(p)
                break
    
    if proceso_actual:
        candidatos.append(proceso_actual)

    if not candidatos:
        return

    proceso_a_ejecutar = min(candidatos, key=lambda x: x['tiempoRestante'])

    if proceso_actual and proceso_actual["id"] != proceso_a_ejecutar["id"]:
        proceso_actual["estado"] = "Listo"
        cambio = True
    
    if proceso_a_ejecutar["estado"] != "Ejecucion":
        proceso_a_ejecutar["estado"] = "Ejecucion"
        cambio = True


#  Mostrar Tablas  #

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
        if proceso["estado"] == "Ejecucion":
            matProcesos[1][1] = str(proceso["id"])
        elif proceso["estado"] == "Listo":
            listos += (str(proceso["id"])+' ')
        elif proceso["estado"] == "Listo/Suspendido":
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


def mostrarEstadisticas():
    num_procesos = len(procesos)
    promEspera = 0
    promRetorno = 0

    print('\nINFORME ESTADÍSTICO:')
    matEst = [['Proceso', 'TR', 'TE']]
    for proceso in procesos:
        tr = proceso["tiempoFinalizacion"] - proceso["tiempoArribo"]
        matEst.append([proceso["id"], tr, proceso["tiempoEspera"]])
        promEspera += proceso["tiempoEspera"]
        promRetorno += tr
    
    promEspera = round(promEspera / num_procesos, 2)
    promRetorno = round(promRetorno / num_procesos, 2)
    
    tiempo_total = max(p["tiempoFinalizacion"] for p in procesos)
    rendimiento = round(num_procesos / tiempo_total, 3)

    matEst.append(["Promedios", promRetorno, promEspera])
    matEst.append(["Rendimiento", str(rendimiento) + " proc/t", ""])

    print(tabulate(matEst, 
        headers='firstrow', 
        tablefmt='fancy_grid',
        stralign='center',
        numalign='center'))


#  Bucle principal (SIMULADOR)  #

def simulador() -> None:
    global memoria, procesos, disco, colaEjec, tiempo, cambio
    

    agregarProcesosInicio()

    while True:
        terminados = sum(1 for p in procesos if p["estado"] == "Terminado")
        if terminados == len(procesos):
            break

        cargarNuevosMemoria()
        cargarLSMemoria()
        cargarEjecMemoria()

        agregarListosEjec()   
        agregarLSEjec()       
        agregarNuevosEjec()   

        planificadorSRTF()
        
        if cambio:
            mostrarTablas()
            cambio = False
        
        avanzarTiempo()
    
    mostrarTablas()
    
    print(tabulate([["Simulación terminada."]], 
        tablefmt='fancy_grid',
        stralign='center'))

    mostrarEstadisticas()

    input("\nPulse para terminar...")
    return


#  Inicio del programa  #

os.system("cls")
menuPrincipal()