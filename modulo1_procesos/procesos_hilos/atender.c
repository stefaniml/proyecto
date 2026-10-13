/* SO-Sim · Modulo 1 — El programa que cada hijo carga con exec().
 *
 * No se ejecuta a mano: lo lanza mostrador.c. Conserva el PID del hijo pero
 * corre este codigo. Un minuto del hotel equivale a 100 ms.
 *
 *   ./atender <id> <huesped> <tramite> <minutos>
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "uso: atender <id> <huesped> <tramite> <minutos>\n");
        return 1;
    }
    int minutos = atoi(argv[4]);

    printf("  -> [%s | PID %d] Atendiendo a %s: %s (%d min)\n",
           argv[1], getpid(), argv[2], argv[3], minutos);
    fflush(stdout);

    usleep(minutos * 100 * 1000);            /* el trabajo del tramite */

    printf("  -> [%s | PID %d] Atencion completada.\n", argv[1], getpid());
    return 0;                                /* lo recoge el padre con wait() */
}
