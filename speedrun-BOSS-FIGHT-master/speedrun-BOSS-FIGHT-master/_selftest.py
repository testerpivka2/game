"""Прогон без окна: проверяем загрузку ассетов, музыку и отрисовку."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

import config as C
import assets
import music
from entities import Player, Boss, Fireball, Projectile

surf = pygame.Surface((C.VIRTUAL_W, C.VIRTUAL_H))

# музыка генерируется
music.ensure_generated()
print("music files:", os.listdir(os.path.join(os.path.dirname(__file__), "music")))

# ассеты
pa = assets.load_player_anims()
print("player anims:", {k: len(v) for k, v in pa.items()})
b1 = assets.load_boss1_anims(C.BOSS_FINAL_SCALE)
print("boss1 anims:", {k: len(v) for k, v in b1.items()})

# прогон каждого типа босса
for i, data in enumerate(C.BOSSES):
    is_final = (i == 6)
    scale = C.BOSS_FINAL_SCALE if is_final else C.BOSS_SCALE
    b = Boss(i, data, scale, C.BOSS_TINTS[i], is_final)
    p = Player(3)
    p.skills = set(C.SKILLS)
    p.max_mana = 3; p.mana = 3
    projectiles = []
    for fr in range(400):
        if fr % 15 == 0:
            p.start_attack(); p.start_dash(); p.jump()
            p.start_shield()
            fb = p.try_fireball()
            p.mana = 3
        p.update(pygame.key.get_pressed())
        b.update(p)
        if b.new_projectiles:
            projectiles += b.new_projectiles
            b.new_projectiles = []
        for pr in projectiles:
            pr.update()
            if pr.rect.colliderect(p.rect):
                p.take_damage(pr.damage, direct=True)
        projectiles = [pr for pr in projectiles if pr.alive]
        # отрисовка
        b.draw(surf); p.draw(surf)
        for pr in projectiles:
            pr.draw(surf)
        # урон боссу
        if fr % 10 == 0:
            b.take_damage(2)
    print("boss %d (%s/%s): dead=%s proj_spawned~%d  player_hp=%d shield_cd=%d"
          % (i, data["name"], data["type"], b.dead, len(projectiles), p.hp,
             p.shield_cd))

print("ALL OK")
