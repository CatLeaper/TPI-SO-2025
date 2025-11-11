# TPI-SO-2025 - Simulador de Asignación de Memoria y Planificación de Procesos

Simulador de sistemas operativos según especificaciones del trabajo práctico:

## Especificaciones del TP

- **Asignación de memoria**: Particiones fijas con algoritmo **Best-Fit**
- **Planificación de CPU**: **SRTF** (Shortest Remaining Time First) - **ÚNICO ALGORITMO**
- **Grado de multiprogramación**: **5** procesos máximo en memoria
- **Particiones de memoria**:
  - 100K reservados para el Sistema Operativo
  - 250K para trabajos grandes
  - 150K para trabajos medianos
  - 50K para trabajos pequeños
- **Máximo de procesos**: 10 procesos
- **Estados**: Nuevo, Listo, Listo/Suspendido, Ejecución, Terminado

## Estructura del Proyecto

```
TPI-SO-2025-NUESTRO/
├── models/              # Modelos de datos
│   ├── __init__.py
│   ├── process.py      # Clase Process
│   └── partition.py    # Clase Partition
├── services/           # Lógica de negocio
│   ├── __init__.py
│   ├── file_reader.py  # Lectura de archivos CSV
│   ├── memory_manager.py  # Gestión de memoria
│   └── scheduler.py    # Planificación de procesos
├── ui/                 # Interfaz de usuario
│   ├── __init__.py
│   ├── display.py      # Visualización
│   └── menu.py         # Menús
├── simulator.py        # Simulador principal
├── main.py             # Punto de entrada
├── ArchivodeProcesos.csv  # Archivo de ejemplo
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecutar el simulador:
```bash
python main.py
```

### Formato del archivo CSV

El archivo CSV debe tener el siguiente formato:
```csv
ID,Tamano,TiempoArribo,TiempoIrrupcion
1,40,0,8
2,200,2,3
...
```

Donde:
- **ID**: Identificador único del proceso
- **Tamano**: Tamaño del proceso en KB
- **TiempoArribo**: Tiempo en que el proceso llega al sistema
- **TiempoIrrupcion**: Tiempo de ejecución del proceso

## Características

### Algoritmo de Planificación

**SRTF (Shortest Remaining Time First)**
- Prioriza procesos con menor tiempo restante
- Es preemptivo: si llega un proceso con menor tiempo restante, desaloja al actual
- Único algoritmo implementado según especificaciones del TP

### Gestión de Memoria

- **Particiones fijas**: 
  - 100K para Sistema Operativo
  - 250K para trabajos grandes
  - 150K para trabajos medianos
  - 50K para trabajos pequeños
- **Best-Fit**: Asigna procesos a la partición que mejor se ajuste (menor fragmentación interna)
- **Fragmentación interna**: Se calcula y muestra para cada partición
- **Grado de multiprogramación**: Máximo 5 procesos en memoria simultáneamente

### Estados de Procesos

- **Nuevo (New)**: Proceso recién creado, aún no ha llegado al sistema
- **Listo (Ready)**: Proceso listo para ejecutar, está en memoria
- **Listo/Suspendido (Suspended)**: Proceso listo pero suspendido (no cabe en memoria o DOM alcanzado)
- **Ejecución (Executing)**: Proceso actualmente en ejecución en la CPU
- **Terminado (Terminated)**: Proceso que finalizó su ejecución

## Estadísticas

Al finalizar la simulación se muestran:
- Tiempo de retorno (Turnaround Time)
- Tiempo de espera (Wait Time)
- Promedios de los tiempos
- Rendimiento del sistema (throughput)

## Ejemplo de Uso

1. Ejecutar `python main.py`
2. Seleccionar opción 1: "Cargar archivo de procesos"
3. Ingresar el nombre del archivo CSV (ej: `ArchivodeProcesos.csv`)
4. Confirmar la carga
5. Configurar la simulación (algoritmo, DOM, particiones)
6. Seleccionar modo de ejecución
7. Observar la simulación y estadísticas finales

## Arquitectura

El proyecto sigue una arquitectura modular con separación de responsabilidades:

- **Models**: Representan las entidades del sistema (Process, Partition)
- **Services**: Contienen la lógica de negocio (gestión de memoria, planificación, lectura de archivos)
- **UI**: Maneja la interacción con el usuario (menús, visualización)
- **Simulator**: Orquesta la simulación completa

Esta arquitectura facilita el mantenimiento, testing y extensión del código.

