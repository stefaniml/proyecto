# Compila los dos programas del Modulo 1.
#   make -C modulo1_procesos/procesos_hilos          compila
#   make -C modulo1_procesos/procesos_hilos clean    borra los ejecutables
#
# Requiere Linux (o WSL en Windows): fork() y exec() son llamadas POSIX.

CC     = gcc
CFLAGS = -Wall -Wextra -O2

all: mostrador atender

mostrador: mostrador.c
	$(CC) $(CFLAGS) mostrador.c -o mostrador

atender: atender.c
	$(CC) $(CFLAGS) atender.c -o atender

clean:
	rm -f mostrador atender
