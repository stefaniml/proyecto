# Compila los dos programas de procesos del Modulo 1 (Linux o WSL).
#   make -C modulo1_procesos/procesos_c          compila
#   make -C modulo1_procesos/procesos_c clean    borra los ejecutables

CC     = gcc
CFLAGS = -Wall -Wextra -O2

all: padre_mostrador hijo_atender

padre_mostrador: padre_mostrador.c
	$(CC) $(CFLAGS) padre_mostrador.c -o padre_mostrador

hijo_atender: hijo_atender.c
	$(CC) $(CFLAGS) hijo_atender.c -o hijo_atender

clean:
	rm -f padre_mostrador hijo_atender
