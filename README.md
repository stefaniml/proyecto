# SO-Sim · Simulador de Sistemas Operativos

Caso aplicado: **Hotel Las Estrellas** · SW407 Sistemas Operativos · UNI

El mostrador de recepción es la CPU y cada solicitud de un huésped es un
proceso. Sobre esa analogía se construyen los seis módulos del curso.

## Instalación

```
pip install -r requirements.txt
```

Python 3.11 o más nuevo. La parte en C (`fork`, `exec`, `wait`) necesita Linux
o WSL con `gcc` y `make`.

## Cómo ejecutar

```
python main.py                         todos los módulos disponibles
python main.py 1                       Módulo 1 completo
python main.py 1 planificacion         una parte: planificacion | hilos | graficos
python main.py 1 planificacion --jornada jornada_dia --quantum 2
python -m pytest tests -q              pruebas
```

Procesos reales en C (Linux/WSL):

```
make -C modulo1_procesos/procesos_hilos
./modulo1_procesos/procesos_hilos/mostrador                       # jornada corta
./modulo1_procesos/procesos_hilos/mostrador escenarios/jornada_dia.json
```

Las salidas (bitácoras, métricas, figuras) quedan en `resultados/` con el
prefijo de su módulo (`m1_…`).

## Estructura

```
main.py                     orden única; cada módulo se registra en MODULOS
core/                       lo compartido por todos los módulos
  modelos.py                FichaHuesped (PCB) · EventoBitacora · EstadoProceso
  cargador.py               lee un escenario JSON
  bitacora.py · reloj.py    registro de eventos y tiempo lógico
  metricas.py               espera, respuesta y retorno promedio
escenarios/                 entradas: jornada_corta.json · jornada_dia.json · tareas.json
modulo1_procesos/           Módulo 1 — procesos, hilos y planificación
  planificacion.py          FCFS, SJF, Round Robin y Prioridad con un mismo motor
  graficos.py               figuras del informe
  procesos_hilos/           hilos.py · mostrador.c · atender.c · Makefile
modulo2_sincronizacion/     Módulo 2 — registro, limpieza, interbloqueo
modulo3_memoria/            Módulo 3 — contigua/ y paginacion/
tests/                      pruebas con pytest
resultados/                 salidas generadas (no se versionan)
```

## Módulo 1 — Procesos, hilos y planificación

**Planificación (Semana 4).** Las cuatro políticas corren sobre la misma
jornada. La jornada corta es el caso de clase y reproduce sus promedios:

| Algoritmo           | Espera | Respuesta | Retorno |
|---------------------|--------|-----------|---------|
| FCFS                | 5.75   | 5.75      | 11.25   |
| SJF                 | 5.25   | 5.25      | 10.75   |
| Round Robin (q = 4) | 9.25   | 4.00      | 14.75   |
| Prioridad           | 7.75   | 7.75      | 13.25   |

Cada política deja su bitácora, y las pruebas comprueban que inicio y fin de
cada solicitud se pueden **reconstruir solo desde la bitácora**.

**Hilos (Semana 3).** Cronometra el mismo trámite sin hilos y con un hilo por
tarea. Las tareas de cada trámite están en `escenarios/tareas.json`.

**fork / exec / wait (Semana 3, C).** El mostrador lee la misma jornada JSON,
crea un proceso por solicitud con `fork()`, cada hijo carga `./atender` con
`exec()` y el padre los recoge con `wait()`. Al final compara la jornada en
paralelo con lo que habría durado uno tras otro (~0.8 s frente a ~2.2 s con la
jornada corta).
