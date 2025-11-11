# Guía de Ejecución del Simulador

## Requisitos Previos

- Python 3.6 o superior instalado
- Sistema operativo: Windows, Linux o macOS
- Terminal o consola de comandos

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   
   O si usa `pip3`:
   ```bash
   pip3 install -r requirements.txt
   ```

## Ejecución del Simulador

1. **Abrir una terminal/consola** y navegar a la carpeta del proyecto:
   ```bash
   cd TPI-SO-2025-NUESTRO
   ```

2. **Ejecutar el programa:**
   ```bash
   python main.py
   ```
   
   O si usa `python3`:
   ```bash
   python3 main.py
   ```

## Uso del Simulador

### Paso 1: Cargar Archivo de Procesos

1. Al iniciar el programa, verá un menú principal.
2. Seleccione la opción **1** para "Cargar archivo de procesos".
3. Ingrese el nombre del archivo CSV (por ejemplo: `ArchivodeProcesos.csv`).
   - El archivo debe estar en la misma carpeta que el programa.
   - Si no ingresa la extensión `.csv`, se agregará automáticamente.
4. Se mostrará una vista previa de los procesos cargados.
5. Confirme la carga escribiendo **s** o **si**.

### Paso 2: Configurar la Simulación

1. **Algoritmo de planificación:**
   - El simulador usa **SRTF** (Shortest Remaining Time First) únicamente.
   - No requiere selección.

2. **Grado de multiprogramación:**
   - Presione Enter para usar el valor por defecto (5).
   - O ingrese un valor personalizado.

3. **Particiones de memoria:**
   - Opción 1 (por defecto): Configuración del TP (250K, 150K, 50K)
   - Opción 2: Configuración alternativa
   - Opción 3: Configuración personalizada
   - Presione Enter para usar la opción 1.

### Paso 3: Ejecutar la Simulación

1. La simulación comenzará automáticamente.
2. **El simulador mostrará salida cuando:**
   - Llega un nuevo proceso al sistema
   - Termina un proceso en ejecución
3. **No hay corridas ininterrumpidas:** después de cada evento importante, debe presionar Enter para continuar.
4. Se mostrarán:
   - Tiempo actual de simulación
   - Distribución de memoria (particiones y procesos asignados)
   - Colas de procesos (Ejecución, Listo, Listo/Suspendido, Nuevo, Terminado)

### Paso 4: Ver Estadísticas Finales

Al finalizar la simulación, se mostrará:
- Estado final de la memoria
- Estado final de las colas
- **Informe estadístico** con:
  - Tiempo de retorno de cada proceso
  - Tiempo de espera de cada proceso
  - Promedios de tiempos
  - Rendimiento del sistema

## Formato del Archivo CSV

El archivo CSV debe tener el siguiente formato:

```csv
ID,Tamano,TiempoArribo,TiempoIrrupcion
1,40,0,8
2,200,2,3
3,100,3,4
```

**Columnas:**
- **ID**: Identificador único del proceso (número entero)
- **Tamano**: Tamaño del proceso en KB (número entero)
- **TiempoArribo**: Tiempo en que el proceso llega al sistema (número entero)
- **TiempoIrrupcion**: Tiempo de ejecución del proceso (número entero)

**Ejemplo de archivo válido:**
```csv
ID,Tamano,TiempoArribo,TiempoIrrupcion
1,40,0,8
2,200,2,3
3,100,3,4
4,300,5,6
5,140,7,2
```

## Características del Simulador

- **Máximo 10 procesos** por simulación
- **Particiones fijas:**
  - 100K para Sistema Operativo
  - 250K para trabajos grandes
  - 150K para trabajos medianos
  - 50K para trabajos pequeños
- **Algoritmo Best-Fit** para asignación de memoria
- **Algoritmo SRTF** para planificación de CPU
- **Grado de multiprogramación:** 5 procesos máximo en memoria

## Solución de Problemas

### Error: "No se encuentra el archivo"
- Verifique que el archivo CSV esté en la misma carpeta que `main.py`
- Verifique que el nombre del archivo sea correcto (incluyendo la extensión .csv)

### Error: "La librería 'tabulate' no está instalada"
- Ejecute: `pip install tabulate`
- O: `pip3 install tabulate`

### La simulación no muestra salida
- El simulador solo muestra salida cuando:
  - Llega un nuevo proceso
  - Termina un proceso
- Si no hay eventos, la simulación continúa sin mostrar salida hasta el siguiente evento

## Notas Importantes

- El simulador funciona **solo en máquinas de escritorio** (no online)
- No se permiten corridas ininterrumpidas
- La simulación se detiene automáticamente cuando todos los procesos terminan
- El límite máximo de tiempo es 1000 ticks (por seguridad)

## Contacto y Soporte

Para consultas sobre el funcionamiento del simulador, consulte el archivo `README.md` o contacte al equipo de desarrollo.

