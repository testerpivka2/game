"""Сквозной прогон всех экранов через настоящие функции main.py (без окна)."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import main          # инициализирует дисплей/шрифты/музыку
import config as C

G = main.GAME
v = main.virt
mouse = (100, 100)

# MENU
main.draw_menu(v, mouse)
assert G.menu_buttons, "нет кнопок меню"

# старт игры (EASY) -> SHOP
G.start_new("EASY")
assert G.state == "SHOP"
main.draw_shop(v, mouse)
# купить все предметы по разу (денег накинем)
G.player.coins = 999
for r, item in list(G.shop_buttons):
    if item["id"] != "__fight__":
        G.buy(item)
main.draw_shop(v, mouse)

# пройти все 7 боссов автоматически
keys = pygame.key.get_pressed()
for n in range(7):
    G.start_battle()
    assert G.state == "BATTLE"
    # бьём босса насмерть, имитируя кадры
    guard = 0
    while G.state == "BATTLE" and guard < 5000:
        main.update_battle(16, keys)
        main.draw_battle(v)
        G.boss.take_damage(3)        # ускоряем убийство
        G.player.hp = G.player.max_hp  # не даём умереть
        guard += 1
    assert guard < 5000, "бой не завершился на боссе %d" % n
    if G.state == "REWARD":
        main.draw_reward(v)
        G.next_after_reward()
    elif G.state == "WIN":
        main.draw_win(v)

assert G.state == "WIN", "ожидали WIN, получили " + G.state
print("Принцесса:", G.princess_level[0])
print("Монет:", G.player.coins, " Время: %.1fс" % (G.total_time/1000))

# GAMEOVER экран
G.state = "GAMEOVER"
main.draw_gameover(v)

print("SMOKE OK — все экраны и 7 боссов отработали без ошибок")
