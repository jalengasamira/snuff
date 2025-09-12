import os
from datetime import datetime

FILE = "usuarios.txt"
REPORT_DIR = "informes"
ACUM_FILE = "acumulador.txt"
DETALLE_FILE = "detalle_partidas.txt"
COLISIONES_FILE = "detalle_colisiones.txt"


def load_users():
    users = []
    if not os.path.exists(FILE):
        return users
    with open(FILE, "r", encoding="utf-8") as f:
        for line in f:
            cod, nombre, usuario, clave, max_score = line.strip().split(",")
            users.append({
                "codigo": cod,
                "nombre": nombre,
                "usuario": usuario,
                "clave": clave,
                "max_score": int(max_score)
            })
    return users


def save_users(users):
    with open(FILE, "w", encoding="utf-8") as f:
        for u in users:
            f.write(f"{u['codigo']},{u['nombre']},{u['usuario']},{u['clave']},{u['max_score']}\n")


def login():
    users = load_users()
    usuario = input("Usuario: ")
    clave = input("Contraseña: ")
    nombre = input("Nombre y Apellido: ")

    for u in users:
        if u["usuario"] == usuario and u["clave"] == clave:
            print("Login correcto")
            return u

    nuevo_cod = str(len(users) + 1)
    nuevo = {
        "codigo": nuevo_cod,
        "nombre": nombre,
        "usuario": usuario,
        "clave": clave,
        "max_score": 0
    }
    users.append(nuevo)
    save_users(users)
    return nuevo


def save_score(user, score):
    users = load_users()
    for u in users:
        if u["usuario"] == user["usuario"]:
            if score > u["max_score"]:
                u["max_score"] = score
    save_users(users)


def generate_report(user, stats):
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"informe_{user['usuario']}_{stamp}.txt"
    path = os.path.join(REPORT_DIR, fname)

    lines = [
        "=== Snuff - Informe de Partida ===",
        f"Fecha/Hora: {stats.get('date')}",
        f"Usuario: {user['usuario']} ({user['nombre']})",
        f"Personaje: {stats.get('character', 'N/A')}",
        "",
        f"Puntaje: {stats.get('score', 0)}",
        f"Kills: {stats.get('kills', 0)} (Jefes: {stats.get('bosses_killed', 0)})",
        f"Disparos: {stats.get('shots_fired', 0)}",
        f"Impactos: {stats.get('hits', 0)}",
        f"Duración: {int(stats.get('duration_s', 0))} s",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    with open("ultima_partida.txt", "w", encoding="utf-8") as f:
        f.write(path)

    return path


def registrar_partida(user, num_partida, stats):
    # acumulador de partidas
    with open(ACUM_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user['codigo']},{num_partida}\n")

    # coso de las partidas
    with open(DETALLE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user['codigo']},{num_partida},{stats['score']},{stats['kills']},{stats['date']}\n")


def registrar_colision(user, num_partida, x, y, obs):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(COLISIONES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user['codigo']},{num_partida},{fecha},{x},{y},{obs}\n")


def get_ranking():
    users = load_users()
    ranking = sorted(users, key=lambda u: u["max_score"], reverse=True)
    return ranking

def informe_padron():
    users = load_users()
    os.makedirs(REPORT_DIR, exist_ok=True)
    fname = os.path.join(REPORT_DIR, "padron_usuarios.txt")

    lines = ["=== Padrón de Usuarios del Juego ===", ""]
    for u in users:
        lines.append(f"{u['codigo']}\t{u['nombre']}\t{u['usuario']}\t{u['clave']}")
    lines.append("")
    lines.append(f"Total Jugadores: {len(users)}")

    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fname


def informe_puntajes(): #todos los jugadores
    users = load_users()
    os.makedirs(REPORT_DIR, exist_ok=True)
    fname = os.path.join(REPORT_DIR, "puntajes_globales.txt")

    tot_general = 0
    mejor_user = None
    mejor_puntaje = -1

    lines = ["=== Planilla Puntaje de Jugadores ===", ""]
    for u in users:
        # para el puntaje a
        puntaje_a = u["max_score"]
        puntaje_b = 0
        total = puntaje_a + puntaje_b
        tot_general += total
        if total > mejor_puntaje:
            mejor_puntaje = total
            mejor_user = u
        lines.append(f"{u['codigo']}\t{u['nombre']}\t{puntaje_a}\t{puntaje_b}\t{total}")

    lines.append("")
    lines.append(f"TOTAL General: {tot_general}")
    if mejor_user:
        lines.append(f"El Mejor Usuario es: {mejor_user['nombre']} ({mejor_user['usuario']})")
        lines.append(f"Con el puntaje: {mejor_puntaje}")

    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fname


def informe_movimientos(cod_usuario, num_partida):
    """Consulta de movimientos (colisiones) por usuario y partida"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    fname = os.path.join(REPORT_DIR, f"movimientos_u{cod_usuario}_p{num_partida}.txt")

    # lo de las colisiones
    total_col = 0
    lines = [f"=== Informe de Movimientos - Usuario {cod_usuario} - Partida {num_partida} ===", ""]
    if os.path.exists(COLISIONES_FILE):
        with open(COLISIONES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                cod, partida, fecha, x, y, obs = line.strip().split(",")
                if cod == str(cod_usuario) and partida == str(num_partida):
                    lines.append(f"{fecha}\t({x},{y})\t{obs}")
                    total_col += 1
    lines.append("")
    lines.append(f"Total General Colisiones: {total_col}")

    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fname


def informe_ranking(): #pal ranking
    os.makedirs(REPORT_DIR, exist_ok=True)
    fname = os.path.join(REPORT_DIR, "ranking_partidas.txt")

    partidas = {}
    if os.path.exists(DETALLE_FILE):
        with open(DETALLE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                cod, partida, score, kills, fecha = line.strip().split(",")
                score = int(score)
                if cod not in partidas:
                    partidas[cod] = []
                partidas[cod].append((partida, score, fecha))

    lines = ["=== Ranking por Usuario ===", ""]
    for cod, plist in partidas.items():
        mejor = max(plist, key=lambda x: x[1])
        peor = min(plist, key=lambda x: x[1])
        tot = sum(p[1] for p in plist)
        lines.append(f"Usuario {cod}:")
        for p in plist:
            lines.append(f" Partida {p[0]} - Puntaje {p[1]} - Fecha {p[2]}")
        lines.append(f" TOTAL General: {tot}")
        lines.append(f" mejor Partida: {mejor[0]} con {mejor[1]} puntos")
        lines.append(f" peor Partida: {peor[0]} con {peor[1]} puntos")
        lines.append("")

    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fname

if __name__ == "__main__":
    print("..")
    informe_padron()
    informe_puntajes()
    informe_ranking()
    informe_movimientos()
    print("si")
