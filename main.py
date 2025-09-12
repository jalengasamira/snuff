import pygame
import random
import math
from datetime import datetime
from player import Player
from enemy import Zombie, Boss
from user_system import login, save_score, generate_report, registrar_partida, registrar_colision, get_ranking, informe_padron, informe_puntajes, informe_ranking

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snuff")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# Colores
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 100, 200)


def draw_button(text, x, y, w, h, active):
    color = BLUE if active else DARK_BLUE
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))
    return rect


def pantalla_ranking():
    ranking = get_ranking()
    running = True
    while running:
        screen.fill((20, 20, 20))
        title = font.render("Ranking de Jugadores", True, WHITE)
        screen.blit(title, (400 - title.get_width() // 2, 40))

        y = 100
        for i, u in enumerate(ranking[:10], start=1):
            text = f"{i}. {u['usuario']} ({u['nombre']}) - {u['max_score']} pts"
            label = font.render(text, True, WHITE)
            screen.blit(label, (100, y))
            y += 40

        back_btn = draw_button("Volver", 300, 500, 200, 50, False)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    running = False
    return


def elegir_personaje():
    personajes = ["Lau L", "Facu", "Lau S", "Samira"]
    running = True
    seleccionado = None
    while running:
        screen.fill((10, 10, 40))
        title = font.render("Elige tu personaje", True, WHITE)
        screen.blit(title, (400 - title.get_width() // 2, 80))

        mx, my = pygame.mouse.get_pos()
        botones = []
        y = 180
        for p in personajes:
            rect = draw_button(p, 300, y, 200, 50, pygame.Rect(300, y, 200, 50).collidepoint(mx, my))
            botones.append((rect, p))
            y += 70

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, p in botones:
                    if rect.collidepoint(event.pos):
                        seleccionado = p
                        running = False
    return seleccionado


def jugar(usuario):
    personaje = elegir_personaje()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player = Player(400, 300, personaje)
    all_sprites.add(player)

    score = 0
    kills = 0
    bosses_killed = 0
    hits = 0
    boss_active = False
    next_boss_score = 200
    running = True
    start_ticks = pygame.time.get_ticks()
    num_partida = int(datetime.now().timestamp())  # simplificado

    def make_stats():
        elapsed_s = (pygame.time.get_ticks() - start_ticks) / 1000.0
        acc = (hits / player.shots_fired * 100.0) if player.shots_fired else 0.0
        return {
            "score": score,
            "kills": kills,
            "bosses_killed": bosses_killed,
            "shots_fired": player.shots_fired,
            "hits": hits,
            "accuracy": acc,
            "duration_s": elapsed_s,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "character": personaje,
        }

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shoot(pygame.mouse.get_pos())

        if random.randint(1, 50) == 1 and not boss_active:
            enemy = Zombie()
            enemies.add(enemy)
            all_sprites.add(enemy)

        keys = pygame.key.get_pressed()
        player.update(keys)
        player.bullets.update()
        player.explosives.update()
        all_sprites.add(player.bullets)
        all_sprites.add(player.explosives)


        for explosive in list(player.explosives):
            if explosive.exploded and explosive.exploded_at:
                ex, ey = explosive.exploded_at
                
                
                pygame.draw.circle(screen, (255, 0, 0), (ex, ey), explosive.radius, 2)

                for enemy in list(enemies):
                    dx = enemy.rect.centerx - ex
                    dy = enemy.rect.centery - ey
                    dist = math.hypot(dx, dy)
                    if dist <= explosive.radius:
                        enemy.health -= explosive.damage
                        hits += 1
                        registrar_colision(usuario, num_partida, ex, ey, f"C4 vs {enemy.__class__.__name__}")

                        if enemy.health <= 0:
                            enemy.kill()
                            kills += 1
                            if isinstance(enemy, Zombie):
                                score += 10
                            else:
                                score += 100
                                bosses_killed += 1
                                boss_active = False
                                next_boss_score += 200

                explosive.kill()





        for enemy in enemies:
            enemy.update(player)

        collisions = pygame.sprite.groupcollide(enemies, player.bullets, False, True)
        for enemy, bullets in collisions.items():
            for b in bullets:
                enemy.health -= b.damage
                hits += 1
                registrar_colision(usuario, num_partida, b.rect.centerx, b.rect.centery, f"Bala vs {enemy.__class__.__name__}")
            if enemy.health <= 0:
                enemy.kill()
                kills += 1
                if isinstance(enemy, Zombie):
                    score += 10
                else:
                    score += 100
                    bosses_killed += 1
                    boss_active = False
                    next_boss_score += 200

        if pygame.sprite.spritecollide(player, enemies, False):
            running = False

        if score >= next_boss_score and not boss_active:
            boss = Boss()
            enemies.add(boss)
            all_sprites.add(boss)
            boss_active = True

        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        hud = [
            f"Puntos: {score}",
            f"Kills: {kills} (Jefes: {bosses_killed})",
            f"Disparos: {player.shots_fired} Impactos: {hits}",
            f"Personaje: {personaje}",
        ]
        y = 10
        for line in hud:
            text = font.render(line, True, WHITE)
            screen.blit(text, (10, y))
            y += 25
        pygame.display.flip()

    stats = make_stats()
    save_score(usuario, score)
    generate_report(usuario, stats)
    registrar_partida(usuario, num_partida, stats)
    informe_padron()
    informe_puntajes()
    informe_ranking()

def menu_principal():
    usuario = login()
    running = True
    while running:
        screen.fill((10, 10, 30))
        title = font.render("Snuff", True, WHITE)
        screen.blit(title, (400 - title.get_width() // 2, 100))

        mx, my = pygame.mouse.get_pos()
        btn_jugar = draw_button("Jugar", 300, 250, 200, 60, pygame.Rect(300, 250, 200, 60).collidepoint(mx, my))
        btn_ranking = draw_button("Ranking", 300, 340, 200, 60, pygame.Rect(300, 340, 200, 60).collidepoint(mx, my))
        btn_salir = draw_button("Salir", 300, 430, 200, 60, pygame.Rect(300, 430, 200, 60).collidepoint(mx, my))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_jugar.collidepoint(event.pos):
                    jugar(usuario)
                elif btn_ranking.collidepoint(event.pos):
                    pantalla_ranking()
                elif btn_salir.collidepoint(event.pos):
                    running = False

    pygame.quit()


if __name__ == "__main__":
    menu_principal()
