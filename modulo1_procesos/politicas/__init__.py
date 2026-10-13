"""Políticas de planificación. Cada una solo decide a quién atiende el
mostrador a continuación; el motor común está en planificacion.py."""
from modulo1_procesos.politicas import fcfs, prioridad, round_robin, sjf

POLITICAS = {"FCFS": fcfs, "SJF": sjf, "Round Robin": round_robin, "Prioridad": prioridad}
