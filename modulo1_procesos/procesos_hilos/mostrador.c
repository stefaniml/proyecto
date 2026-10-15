/* SO-Sim · Modulo 1 · Semana 3 — fork(), exec() y wait() reales
 * Hotel Las Estrellas · SW407 Sistemas Operativos · UNI
 *
 * El mostrador lee la jornada (el mismo JSON que usa Python) y crea un proceso
 * hijo por solicitud con fork(). Cada hijo se convierte en ./atender con
 * exec(), y el padre los recoge con wait(). Al final compara cuanto duro la
 * jornada en paralelo con lo que habria durado atendiendo uno tras otro.
 *
 * Requiere Linux o WSL.
 *   make -C modulo1_procesos/procesos_hilos
 *   ./modulo1_procesos/procesos_hilos/mostrador [escenarios/jornada_dia.json]
 */
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX 32
#define JORNADA "escenarios/jornada_corta.json"
#define ATENDER "modulo1_procesos/procesos_hilos/atender"

struct Solicitud {
    char id[8], huesped[48], tramite[64], minutos[8];
    pid_t pid;
    double fin_ms;
};

static double ahora_ms(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1000.0 + t.tv_nsec / 1e6;
}

/* Se coloca en la raiz del proyecto (dos carpetas arriba del binario), asi
   las rutas relativas funcionan se ejecute desde donde se ejecute. */
static void ir_a_la_raiz(void) {
    char ruta[1024];
    ssize_t n = readlink("/proc/self/exe", ruta, sizeof(ruta) - 16);
    if (n <= 0) return;
    ruta[n] = '\0';
    strcpy(strrchr(ruta, '/'), "/../..");
    if (chdir(ruta) != 0) perror("chdir");
}

/* Copia en dst el valor de "clave" de una linea JSON como
   {"pid": "P1", "huesped": "Sra. Ramirez", ..., "duracion": 5, ...} */
static int campo(const char *linea, const char *clave, char *dst, size_t n) {
    char patron[32];
    snprintf(patron, sizeof(patron), "\"%s\":", clave);
    const char *p = strstr(linea, patron);
    if (!p) return 0;
    p += strlen(patron);
    while (*p == ' ') p++;
    char fin = (*p == '"') ? *p++ : ',';      /* texto entre comillas o numero */
    size_t i = 0;
    while (*p && *p != fin && *p != '}' && i + 1 < n) dst[i++] = *p++;
    dst[i] = '\0';
    return 1;
}

/* Lee las solicitudes del JSON (una por linea). Devuelve cuantas leyo. */
static int leer_jornada(const char *ruta, struct Solicitud *s) {
    FILE *f = fopen(ruta, "r");
    if (!f) { perror(ruta); return -1; }
    char linea[512];
    int n = 0;
    while (n < MAX && fgets(linea, sizeof(linea), f)) {
        if (campo(linea, "pid", s[n].id, sizeof(s[n].id))
            && campo(linea, "huesped", s[n].huesped, sizeof(s[n].huesped))
            && campo(linea, "tramite", s[n].tramite, sizeof(s[n].tramite))
            && campo(linea, "duracion", s[n].minutos, sizeof(s[n].minutos)))
            n++;
    }
    fclose(f);
    return n;
}

int main(int argc, char *argv[]) {
    /* La jornada recibida se resuelve ANTES de cambiar de carpeta, para que
       una ruta relativa se entienda desde donde se ejecuto el programa. */
    char ruta_absoluta[PATH_MAX];
    const char *ruta = JORNADA;
    if (argc > 1) {
        if (!realpath(argv[1], ruta_absoluta)) { perror(argv[1]); return 1; }
        ruta = ruta_absoluta;
    }
    ir_a_la_raiz();

    struct Solicitud s[MAX];
    int n = leer_jornada(ruta, s);
    if (n <= 0) return 1;
    if (access(ATENDER, X_OK) != 0) {
        fprintf(stderr, "Falta %s. Compila con: make -C modulo1_procesos/procesos_hilos\n", ATENDER);
        return 1;
    }

    printf("=== Hotel Las Estrellas - Modulo 1: fork() y exec() ===\n");
    printf("Mostrador abierto (PID %d). Llegaran %d solicitudes.\n\n", getpid(), n);
    fflush(stdout);   /* sin esto, cada hijo heredaria y repetiria el texto pendiente */

    const double t0 = ahora_ms();
    for (int i = 0; i < n; i++) {
        /* ① FORK: el mostrador se duplica; nace un proceso hijo por solicitud */
        pid_t pid = fork();
        if (pid < 0) { perror("fork"); return 1; }

        if (pid == 0) {
            /* ② EXEC: el hijo deja de ser una copia del mostrador y carga el
                   programa ./atender, pasandole huesped, tramite y minutos */
            execl(ATENDER, "atender", s[i].id, s[i].huesped, s[i].tramite,
                  s[i].minutos, (char *)NULL);
            perror("execl");                  /* solo llega aqui si exec() fallo */
            _exit(127);
        }

        /* el padre anota al hijo y sigue creando los demas, sin esperarlo */
        s[i].pid = pid;
        printf("[Mostrador] Solicitud %s creada -> proceso hijo PID %d\n", s[i].id, pid);
        fflush(stdout);
    }

    /* ③ WAIT: el padre espera a cada hijo, en el orden en que van terminando */
    for (int k = 0; k < n; k++) {
        int estado;
        pid_t pid = wait(&estado);
        double fin = ahora_ms() - t0;
        for (int i = 0; i < n; i++)
            if (s[i].pid == pid) {
                s[i].fin_ms = fin;
                printf("[Mostrador] Proceso PID %d (%s) finalizo en %.0f ms "
                       "(codigo de salida %d)\n", pid, s[i].id, fin, WEXITSTATUS(estado));
            }
    }

    double paralelo = ahora_ms() - t0, suma = 0;
    for (int i = 0; i < n; i++) suma += s[i].fin_ms;

    /* Esperado: lo que pide el tramite (1 min = 100 ms). Medido: lo que tardo
       de verdad; la diferencia es el costo de fork(), exec() y wait(). */
    printf("\nMostrador cerrado: %d/%d solicitudes atendidas.\n\n", n, n);
    printf("  %-5s %-20s %9s %9s %8s\n", "Sol.", "Huesped", "Esperado", "Medido", "Costo");
    printf("  ----------------------------------------------------------\n");
    for (int i = 0; i < n; i++) {
        double esperado = atoi(s[i].minutos) * 100.0;
        printf("  %-5s %-20.20s %6.0f ms %6.0f ms %5.1f ms\n",
               s[i].id, s[i].huesped, esperado, s[i].fin_ms, s[i].fin_ms - esperado);
    }
    printf("  ----------------------------------------------------------\n");
    printf("  Con fork (en paralelo)  : %6.0f ms   dura lo que la solicitud mas larga\n", paralelo);
    printf("  Sin fork (uno tras otro): %6.0f ms   la suma de todas\n", suma);
    printf("  Ahorro                  : %6.1f x    mas rapido atendiendo a la vez\n", suma / paralelo);

    mkdir("resultados", 0775);
    FILE *f = fopen("resultados/m1_traza_fork.json", "w");
    if (f) {
        fprintf(f, "[\n");
        for (int i = 0; i < n; i++)
            fprintf(f, "  {\"pid\": \"%s\", \"huesped\": \"%s\", \"pid_so\": %d, \"duracion_ms\": %.1f}%s\n",
                    s[i].id, s[i].huesped, s[i].pid, s[i].fin_ms, i + 1 < n ? "," : "");
        fprintf(f, "]\n");
        fclose(f);
        printf("\nTraza en resultados/m1_traza_fork.json  ->  opcion Graficos del menu\n");
    }
    return 0;
}
