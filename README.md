# Simulador de Sistemas Operativos

Caso aplicado: **Hotel Las Estrellas** · SW407 Sistemas Operativos · UNI

El mostrador de recepción es la CPU y cada solicitud de un huésped es un
proceso. Sobre esa analogía se construyen los seis módulos del curso.

## Instalación

```
pip install -r requirements.txt        (matplotlib y pytest)
```

Python 3.11 o más nuevo. La parte en C (`fork`, `exec`, `wait`) necesita Linux
o WSL con `gcc` o `clang`; en Windows no aparece en el menú y no hace falta
ningún compilador.

## Cómo ejecutar

Todo se hace desde el menú:

```
python main.py          Windows
python3 main.py         Linux / WSL
```

```
1. Módulo 1 · Procesos, hilos y planificación   → abre un submenú:
      1. Procesos reales en C: fork, exec y wait  (solo Linux/WSL)
      2. Hilos: el mismo trámite con y sin hilos
      3. Planificación: FCFS, SJF, Round Robin, Prioridad
      0. Volver al menú principal
2. Módulo 2 · Sincronización: mutex, productor-consumidor, interbloqueo
3. Módulo 3 · Memoria: asignación contigua, MMU y reemplazo
4. Gráficos de todos los módulos
5. Pruebas automáticas (pytest)
0. Salir
```

Se escribe el número de una opción; al terminar, Enter vuelve al menú. En
Windows el submenú del Módulo 1 no muestra la opción en C, así que hilos y
planificación pasan a ser la 1 y la 2.

- **Procesos en C:** se compilan solos con `gcc` o `clang` la primera vez (o si
  cambia el código) y usan la jornada corta.
- **Planificación:** pide la jornada (`jornada_corta` o `jornada_dia`) y el
  quantum; con Enter usa los valores por defecto (jornada corta, quantum 4).

Las salidas (bitácoras, métricas, figuras) quedan en `resultados/` con el
prefijo de su módulo (`m1_…`). Los gráficos se dibujan con los datos de la
última ejecución de cada parte.

## Pruebas

Opción **5** del menú, o desde la terminal:

```
python -m pytest tests -v
```

| Archivo | Qué comprueba |
|---|---|
| `tests/test_modulo1.py` | Planificación: los promedios de la jornada corta coinciden con los calculados a mano; SJF tiene la menor espera y Round Robin la menor respuesta; no se pierde ninguna solicitud; las métricas se reconstruyen desde la bitácora. Hilos: con hilos las tareas van a la vez. Procesos: un hijo por solicitud, cada uno con su PID y atendidos en paralelo (solo en Linux/WSL; en Windows aparece como *skipped*). |
| `tests/test_modulo2.py` | (pendiente) |
| `tests/test_modulo3.py` | (pendiente) |

## Estructura

```
main.py                     menú principal; cada opción es una línea en OPCIONES
core/                       lo compartido por todos los módulos
  modelos.py                FichaHuesped (PCB) · EventoBitacora · EstadoProceso
  cargador.py               lee un escenario JSON
  bitacora.py · reloj.py    registro de eventos y tiempo lógico
  metricas.py               espera, respuesta y retorno promedio
escenarios/                 entradas: jornada_corta.json · jornada_dia.json · tareas.json
analisis/graficos.py        gráficos de TODOS los módulos, con un mismo estilo
modulo1_procesos/           Módulo 1 — procesos, hilos y planificación
  procesos/                 fork, exec y wait en C (Linux/WSL)
    padre_mostrador.c       el padre: fork() y wait()
    hijo_atender.c          el programa que cada hijo carga con exec()
  hilos/hilos.py            threading: crear, arrancar (start) y esperar (join)
  planificacion/            FCFS, SJF, Round Robin y Prioridad
    planificador.py         motor común: cola de listos, quantum, métricas
    fcfs.py · sjf.py · round_robin.py · prioridad.py
modulo2_sincronizacion/     Módulo 2 — registro, limpieza, interbloqueo
modulo3_memoria/            Módulo 3 — contigua/ y paginacion/
tests/                      pruebas con pytest
resultados/                 salidas generadas (no se versionan)
```

## Módulo 1 — Procesos, hilos y planificación

**Planificación (Semana 4).** Las cuatro políticas corren sobre la misma
jornada. Resultados con la jornada corta (5 solicitudes, quantum 4), verificados
a mano en las pruebas:

| Algoritmo           | Espera | Respuesta | Retorno |
|---------------------|--------|-----------|---------|
| FCFS                | 8.20   | 8.20      | 13.20   |
| SJF                 | 5.80   | 5.80      | 10.80   |
| Round Robin (q = 4) | 10.60  | 4.80      | 15.60   |
| Prioridad           | 10.40  | 10.40     | 15.40   |

Cada política deja su bitácora, y las pruebas comprueban que inicio y fin de
cada solicitud se pueden **reconstruir solo desde la bitácora**.

**Hilos (Semana 3).** Cronometra el mismo trámite sin hilos y con un hilo por
tarea. Las tareas de cada trámite están en `escenarios/tareas.json`.

**fork / exec / wait (Semana 3, C).** El mostrador lee la misma jornada JSON,
crea un proceso por solicitud con `fork()`, cada hijo carga `./hijo_atender` con
`exec()` y el padre los recoge con `wait()`. Al final compara la jornada en
paralelo con lo que habría durado uno tras otro (~0.9 s frente a ~2.5 s con la
jornada corta).
