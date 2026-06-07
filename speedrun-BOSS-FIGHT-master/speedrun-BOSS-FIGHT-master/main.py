"""Самурай vs 7 Боссов — главный файл."""
import sys
import random
import pygame

import config as C
import assets
import music
from entities import Player, Boss, Fireball, Projectile, VFX

pygame.init()
pygame.display.set_caption("Путь Самурая")
music.init()

# Полноэкранный режим, отрисовка в виртуальный буфер 1280x720
_info = pygame.display.Info()
_dw, _dh = _info.current_w, _info.current_h
if _dw <= 0 or _dh <= 0:
    _dw, _dh = C.VIRTUAL_W, C.VIRTUAL_H
screen = pygame.display.set_mode((_dw, _dh), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = screen.get_size()
if SCREEN_W <= 0 or SCREEN_H <= 0:
    SCREEN_W, SCREEN_H = C.VIRTUAL_W, C.VIRTUAL_H
virt = pygame.Surface((C.VIRTUAL_W, C.VIRTUAL_H))
clock = pygame.time.Clock()

# Масштаб виртуального буфера под реальный экран (с сохранением пропорций)
_scale = min(SCREEN_W / C.VIRTUAL_W, SCREEN_H / C.VIRTUAL_H)
if _scale <= 0:
    _scale = 1.0
_blit_w = int(C.VIRTUAL_W * _scale)
_blit_h = int(C.VIRTUAL_H * _scale)
_blit_x = (SCREEN_W - _blit_w) // 2
_blit_y = (SCREEN_H - _blit_h) // 2


def to_virt(pos):
    """Координаты мыши экрана -> виртуальные."""
    mx, my = pos
    return ((mx - _blit_x) / _scale, (my - _blit_y) / _scale)


# ---------- Шрифты ----------
# SysFont ломается на Python 3.14, поэтому грузим .ttf напрямую.
import os as _os

_FONT_FILE = None
for _cand in ("arialbd.ttf", "arial.ttf", "segoeui.ttf", "calibri.ttf"):
    _p = _os.path.join(_os.environ.get("WINDIR", r"C:\Windows"), "Fonts", _cand)
    if _os.path.exists(_p):
        _FONT_FILE = _p
        break


def font(size, bold=True):
    if _FONT_FILE:
        f = pygame.font.Font(_FONT_FILE, size)
    else:
        f = pygame.font.Font(None, size)   # встроенный шрифт pygame
    f.set_bold(bold and _FONT_FILE is None)
    return f


F_HUGE = font(72)
F_BIG = font(48)
F_MED = font(32)
F_SMALL = font(24)
F_TINY = font(18)


def text(surf, s, fnt, color, center=None, topleft=None, midtop=None):
    img = fnt.render(s, True, color)
    r = img.get_rect()
    if center:
        r.center = center
    elif topleft:
        r.topleft = topleft
    elif midtop:
        r.midtop = midtop
    surf.blit(img, r)
    return r


def draw_bar(surf, x, y, w, h, frac, color, bg=(40, 40, 48)):
    pygame.draw.rect(surf, bg, (x, y, w, h), border_radius=4)
    pygame.draw.rect(surf, color, (x, y, int(w * max(0, frac)), h),
                     border_radius=4)
    pygame.draw.rect(surf, C.WHITE, (x, y, w, h), 2, border_radius=4)


# =====================================================================
#  СОСТОЯНИЕ ИГРЫ
# =====================================================================
class Game:
    def __init__(self):
        self.state = "MENU"
        self.player = None
        self.difficulty = "MEDIUM"
        self.boss_index = 0           # какой босс впереди (0..6)
        self.skill_order = []         # порядок выпадения умений
        self.boss = None
        self.fireballs = []
        self.boss_projectiles = []
        self.minions = []
        self.vfx = []         # одноразовые эффекты (поофы и т.п.)
        self.popups = []      # всплывающие надписи (MISS! и т.п.)
        self.total_time = 0.0         # общий таймер (мс)
        self.boss_start_time = 0.0    # время начала текущего боя
        self.boss_fight_time = 0.0
        self.hp_at_boss_start = 0
        self.bg_cache = {}

        self.last_reward = {}         # для экрана награды
        self.last_skill = None
        self.shop_msg = ""
        self.shop_costs = {}          # текущая цена каждого предмета
        self.princess_level = None
        self.menu_buttons = []
        self.shop_buttons = []

    # ---------- запуск новой игры ----------
    def start_new(self, difficulty):
        self.difficulty = difficulty
        hp = C.DIFFICULTIES[difficulty]["hp"]
        self.player = Player(hp)
        self.boss_index = 0
        self.total_time = 0.0
        self.fireballs = []
        # EASY/MEDIUM — фиксированный порядок умений; HARD — случайный
        if difficulty == "HARD":
            self.skill_order = C.SKILLS[:]
            random.shuffle(self.skill_order)
        else:
            self.skill_order = C.SKILL_ORDER_FIXED[:]
        self.shop_costs = {it["id"]: it["cost"] for it in C.SHOP_ITEMS}
        self.enter_shop()

    def get_bg(self, name, size):
        key = (name, size)
        if key not in self.bg_cache:
            self.bg_cache[key] = assets.scale_bg(name, size)
        return self.bg_cache[key]

    # ---------- магазин ----------
    def enter_shop(self):
        self.state = "SHOP"
        self.shop_msg = ""

    def buy(self, item):
        iid = item["id"]
        cost = self.shop_costs[iid]
        p = self.player
        if p.coins < cost:
            self.shop_msg = "Недостаточно монет!"
            return
        if iid == "speed":
            p.speed *= 1.12
        elif iid == "damage":
            p.damage += 0.5
        elif iid == "maxhp":
            p.max_hp += 1
            p.hp += 1
        elif iid == "maxmana":
            p.max_mana += 1
        elif iid == "healhp":
            if p.hp >= p.max_hp:
                self.shop_msg = "HP уже полное!"
                return
            p.hp = p.max_hp
        elif iid == "healmana":
            if p.max_mana == 0:
                self.shop_msg = "Мана ещё не открыта!"
                return
            if p.mana >= p.max_mana:
                self.shop_msg = "Мана уже полная!"
                return
            p.mana = p.max_mana
        p.coins -= cost
        self.shop_costs[iid] = cost + item["grow"]
        self.shop_msg = "Куплено: " + item["name"]

    # ---------- начать бой ----------
    def start_battle(self):
        self.state = "BATTLE"
        data = C.BOSSES[self.boss_index]
        is_final = (self.boss_index == 6)
        scale = C.BOSS_FINAL_SCALE if is_final else C.BOSS_SCALE
        tint = C.BOSS_TINTS[self.boss_index]
        self.boss = Boss(self.boss_index, data, scale, tint, is_final)
        self.fireballs = []
        self.boss_projectiles = []
        self.minions = []
        self.vfx = []
        self.popups = []
        self.player.x = 250
        self.player.y = C.GROUND_Y
        self.boss_fight_time = 0.0
        self.hp_at_boss_start = self.player.hp
        # выдать ману если файрбол уже есть
        if "fireball" in self.player.skills and self.player.max_mana < 1:
            self.player.max_mana = 1

    # ---------- победа над боссом ----------
    def add_popup(self, x, y, txt, color):
        self.popups.append({"x": x, "y": y, "txt": txt, "color": color,
                            "life": 48, "max": 48})

    def boss_defeated(self):
        p = self.player

        def rnd(x):                       # математическое округление (half-up)
            return int(x + 0.5)

        # границы награды для текущего босса (зависят от сложности)
        lo0, hi0, factor = C.REWARD_TUNING[self.difficulty]
        mult = factor ** self.boss_index
        lo = rnd(lo0 * mult)
        hi = rnd(hi0 * mult)

        # позиция внутри диапазона: быстрее убил и меньше получил урона = ближе к hi
        time_sec = self.boss_fight_time / 1000.0
        time_score = max(0.0, min(1.0, (60.0 - time_sec) / 50.0))  # 10с=1, 60с=0
        start_hp = max(1, self.hp_at_boss_start)
        hp_lost = self.hp_at_boss_start - p.hp
        hp_score = max(0.0, min(1.0, p.hp / start_hp))
        score = 0.5 * time_score + 0.5 * hp_score
        reward = rnd(lo + score * (hi - lo))
        reward = max(lo, min(hi, reward))
        p.coins += reward

        self.last_reward = {
            "coins": reward, "lo": lo, "hi": hi, "time": time_sec,
            "hp_lost": hp_lost, "score": score,
        }

        if self.boss_index < 6:
            skill = self.skill_order[self.boss_index]
            p.skills.add(skill)
            if skill == "fireball" and p.max_mana < 1:
                p.max_mana = 1
                p.mana = 1
            self.last_skill = skill
            self.state = "REWARD"
        else:
            # финал — принцесса
            self.compute_princess()
            self.state = "WIN"

    def compute_princess(self):
        t = self.boss_fight_time / 1000.0
        if t < 25:
            self.princess_level = ("ОБРАЗОВАННАЯ",
                                   "Принцесса умна и благодарна. Идеальный финал!")
        elif t < 50:
            self.princess_level = ("СТРАННОВАТАЯ",
                                   "Принцесса немного не от мира сего...")
        else:
            self.princess_level = ("ГЛУПЕНЬКАЯ",
                                   "Принцесса... ну, она хотя бы спасена.")

    def next_after_reward(self):
        self.boss_index += 1
        self.enter_shop()


GAME = Game()


# =====================================================================
#  ЭКРАНЫ
# =====================================================================
def draw_menu(surf, mouse):
    bg = GAME.get_bg("assets_bg/bg5.png", (C.VIRTUAL_W, C.VIRTUAL_H))
    surf.blit(bg, (0, 0))
    overlay = pygame.Surface((C.VIRTUAL_W, C.VIRTUAL_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surf.blit(overlay, (0, 0))

    text(surf, "ПУТЬ САМУРАЯ", F_HUGE, C.GOLD, center=(C.VIRTUAL_W // 2, 90))
    lines = [
        "Победи всех 7 боссов за минимальное время!",
        "Перед каждым боссом — магазин улучшений.",
        "За каждого босса: монеты (за скорость и HP) + новое умение.",
        "7-й босс хранит Принцессу — чем быстрее победишь, тем она умнее.",
        "",
        "A / D — ход,  W/Space — прыжок,  S — присесть,  F — атака (комбо)",
        "G — щит (блок одного удара),  E — файрбол,  Shift — рывок",
        "Прыжок в стену — цепляешься и сползаешь; прыжок от стены — лезешь выше",
        "У каждого босса своя способность — следи за снарядами!",
        "",
        "Выбери сложность:",
    ]
    y = 150
    for ln in lines:
        text(surf, ln, F_SMALL, C.WHITE, center=(C.VIRTUAL_W // 2, y))
        y += 30

    # кнопки сложности
    GAME.menu_buttons = []
    diffs = [("EASY", C.GREEN), ("MEDIUM", C.GOLD), ("HARD", C.RED)]
    bw, bh = 280, 70
    total = len(diffs) * bw + (len(diffs) - 1) * 30
    x0 = (C.VIRTUAL_W - total) // 2
    by = 480
    for i, (d, col) in enumerate(diffs):
        r = pygame.Rect(x0 + i * (bw + 30), by, bw, bh)
        hover = r.collidepoint(mouse)
        pygame.draw.rect(surf, (col if hover else (50, 50, 60)), r,
                         border_radius=10)
        pygame.draw.rect(surf, col, r, 3, border_radius=10)
        label = "%s — %d HP" % (C.DIFFICULTIES[d]["label"],
                                C.DIFFICULTIES[d]["hp"])
        text(surf, label, F_MED, C.WHITE, center=r.center)
        GAME.menu_buttons.append((r, d))

    text(surf, "Кликни по сложности, чтобы начать.  ESC — выход",
         F_TINY, C.WHITE, center=(C.VIRTUAL_W // 2, 600))


def draw_shop(surf, mouse):
    bg = GAME.get_bg("assets_ui/shopbackground.jpg", (C.VIRTUAL_W, C.VIRTUAL_H))
    surf.blit(bg, (0, 0))
    overlay = pygame.Surface((C.VIRTUAL_W, C.VIRTUAL_H), pygame.SRCALPHA)
    overlay.fill((10, 5, 20, 150))
    surf.blit(overlay, (0, 0))

    # картинка магазина
    shop_img = assets.load_image("assets_ui/shop.png")
    shop_img = pygame.transform.scale(shop_img, (260, 260))
    surf.blit(shop_img, (60, 120))

    nb = GAME.boss_index + 1
    text(surf, "МАГАЗИН  (перед боссом %d/7)" % nb, F_BIG, C.GOLD,
         center=(C.VIRTUAL_W // 2, 50))
    text(surf, "Монеты: %d" % GAME.player.coins, F_MED, C.GOLD,
         center=(C.VIRTUAL_W // 2, 100))

    GAME.shop_buttons = []
    cols = 2
    cw, ch = 460, 90
    gap = 24
    x0 = 360
    y0 = 150
    for i, item in enumerate(C.SHOP_ITEMS):
        cx = x0 + (i % cols) * (cw + gap)
        cy = y0 + (i // cols) * (ch + gap)
        r = pygame.Rect(cx, cy, cw, ch)
        hover = r.collidepoint(mouse)
        cost = GAME.shop_costs[item["id"]]
        afford = GAME.player.coins >= cost
        base_col = (45, 50, 70) if afford else (40, 30, 30)
        pygame.draw.rect(surf, (70, 80, 110) if hover and afford else base_col,
                         r, border_radius=10)
        pygame.draw.rect(surf, C.GOLD if afford else C.GREY, r, 3,
                         border_radius=10)
        text(surf, item["name"], F_MED, C.WHITE, topleft=(cx + 16, cy + 10))
        text(surf, item["desc"], F_TINY, (200, 200, 210),
             topleft=(cx + 16, cy + 50))
        text(surf, "%d" % cost, F_MED, C.GOLD if afford else C.GREY,
             center=(cx + cw - 50, cy + ch // 2))
        GAME.shop_buttons.append((r, item))

    # кнопка "В бой"
    fight = pygame.Rect(C.VIRTUAL_W // 2 - 160, 620, 320, 70)
    hover = fight.collidepoint(mouse)
    pygame.draw.rect(surf, C.RED if hover else (120, 40, 40), fight,
                     border_radius=12)
    pygame.draw.rect(surf, C.WHITE, fight, 3, border_radius=12)
    text(surf, "В БОЙ!", F_BIG, C.WHITE, center=fight.center)
    GAME.shop_buttons.append((fight, {"id": "__fight__"}))

    if GAME.shop_msg:
        text(surf, GAME.shop_msg, F_SMALL, C.GOLD,
             center=(C.VIRTUAL_W // 2, 590))


def draw_hud(surf):
    p = GAME.player
    # HP — полоска с числом справа сверху
    bar_w, bar_h = 280, 26
    bx = C.VIRTUAL_W - bar_w - 30
    by = 28
    draw_bar(surf, bx, by, bar_w, bar_h, p.hp / p.max_hp, C.RED)
    text(surf, "HP %d/%d" % (p.hp, p.max_hp), F_SMALL, C.WHITE,
         center=(bx + bar_w // 2, by + bar_h // 2))
    # монеты
    text(surf, "Монеты: %d" % p.coins, F_MED, C.GOLD,
         topleft=(C.VIRTUAL_W - 240, 66))
    # мана — полоска с числом слева сверху (как HP)
    if p.max_mana > 0:
        mbw, mbh = 240, 22
        mbx, mby = 30, 30
        draw_bar(surf, mbx, mby, mbw, mbh, p.mana / p.max_mana, C.BLUE)
        text(surf, "MANA %d/%d" % (int(p.mana), int(p.max_mana)),
             F_SMALL, C.WHITE, center=(mbx + mbw // 2, mby + mbh // 2))

    # статусы способностей слева снизу (стопкой)
    yb = C.VIRTUAL_H - 40
    if p.shield_up:
        sh_txt, sh_col = "ЩИТ: АКТИВЕН", (140, 210, 255)
    elif p.shield_cd > 0:
        sh_txt, sh_col = "ЩИТ: %.1fс" % (p.shield_cd / 60.0), C.GREY
    else:
        sh_txt, sh_col = "ЩИТ (G): готов", (140, 210, 255)
    text(surf, sh_txt, F_SMALL, sh_col, topleft=(30, yb))
    yb -= 28
    if "fireball" in p.skills:
        if p.fire_cd > 0:
            fb_txt, fb_col = "ФАЙРБОЛ: %.1fс" % (p.fire_cd / 60.0), C.GREY
        elif p.mana < 1:
            fb_txt, fb_col = "ФАЙРБОЛ: нет маны", C.GREY
        else:
            fb_txt, fb_col = "ФАЙРБОЛ (E): готов", (255, 160, 80)
        text(surf, fb_txt, F_SMALL, fb_col, topleft=(30, yb))
        yb -= 28
    if "fire_aura" in p.skills:
        if p.aura_off > 0:
            au_txt, au_col = "АУРА: пауза %.1fс" % (p.aura_off / 60.0), C.GREY
        else:
            au_txt, au_col = "АУРА: активна", (255, 150, 70)
        text(surf, au_txt, F_SMALL, au_col, topleft=(30, yb))
        yb -= 28

    # индикатор бессмертия
    if p.god_mode:
        text(surf, "БЕССМЕРТИЕ (P)", F_SMALL, (120, 255, 160),
             topleft=(30, yb))

    # таймер по центру (общий)
    t = GAME.total_time / 1000.0
    mm = int(t // 60)
    ss = int(t % 60)
    ms = int((t * 1000) % 1000)
    tstr = "%02d:%02d.%03d" % (mm, ss, ms)
    text(surf, tstr, F_BIG, C.WHITE, midtop=(C.VIRTUAL_W // 2, 16))

    # имя и hp босса
    b = GAME.boss
    if b:
        text(surf, b.name, F_MED, C.WHITE, midtop=(C.VIRTUAL_W // 2, 80))
        bw2, bh2 = 600, 26
        bx2 = C.VIRTUAL_W // 2 - bw2 // 2
        draw_bar(surf, bx2, 120, bw2, bh2, b.hp / b.max_hp, C.RED)
        cur = max(0, int(b.hp + 0.999))   # округление вверх
        text(surf, "%d / %d" % (cur, int(b.max_hp)), F_SMALL, C.WHITE,
             center=(bx2 + bw2 // 2, 120 + bh2 // 2))


def update_battle(dt, keys):
    p = GAME.player
    b = GAME.boss
    GAME.total_time += dt
    GAME.boss_fight_time += dt

    p.update(keys)
    b.update(p)

    # удар игрока мечом (с шансом уворота босса)
    if p.attacking and not p.hit_done and 4 <= p.attack_timer <= 12:
        if p.attack_hitbox().colliderect(b.rect):
            chance = C.DODGE_CHANCE.get(GAME.difficulty, 0.25)
            if b.can_dodge() and random.random() < chance:
                b.do_dodge(p)
                GAME.add_popup(b.x, b.y - b.h - 8, "MISS!", (255, 235, 120))
            else:
                b.take_damage(p.damage)
                b.knockback(p.x)            # отброс при попадании
                b.end_flight()             # сбить с летающего портала
            p.hit_done = True

    # аура огня: снимает до AURA_BUDGET HP за цикл, затем пауза 5 сек
    aura = p.aura_hitbox()
    if aura and aura.colliderect(b.rect):
        dmg = C.AURA_DPS
        b.take_damage(dmg)
        p.aura_dealt += dmg
        if p.aura_dealt >= C.AURA_BUDGET:
            p.aura_dealt = 0.0
            p.aura_off = C.AURA_OFF_TIME

    # файрболы
    for f in GAME.fireballs:
        f.update()
        if f.alive and f.rect.colliderect(b.rect):
            b.take_damage(f.damage)
            b.knockback(f.x)
            f.alive = False
    GAME.fireballs = [f for f in GAME.fireballs if f.alive]

    # атака босса по игроку (ближний бой — активная фаза полного взмаха)
    if b.melee_active and not b.hit_done:
        if b.attack_hitbox().colliderect(p.rect):
            dmg = 2 if b.is_final else 1
            if p.take_damage(dmg, direct=True):
                b.hit_done = True

    # луч босса (beam)
    if b.beam_active:
        hb = b.beam_hitbox()
        if hb and hb.colliderect(p.rect):
            p.take_damage(2 if b.is_final else 1, direct=True)

    # новые снаряды от босса
    if b.new_projectiles:
        GAME.boss_projectiles.extend(b.new_projectiles)
        b.new_projectiles = []
    # обновление снарядов босса
    for pr in GAME.boss_projectiles:
        pr.update()
        if pr.alive and pr.rect.colliderect(p.rect):
            dmg = 2 if b.is_final else 1
            p.take_damage(dmg, direct=True)
            pr.alive = False
    GAME.boss_projectiles = [pr for pr in GAME.boss_projectiles if pr.alive]

    # миньоны (призыв) + эффекты появления
    if b.new_minions:
        GAME.minions.extend(b.new_minions)
        b.new_minions = []
    if b.new_vfx:
        GAME.vfx.extend(b.new_vfx)
        b.new_vfx = []
    for m in GAME.minions:
        m.update(p)
        # меч игрока убивает слизня
        if (p.attacking and 4 <= p.attack_timer <= 12
                and p.attack_hitbox().colliderect(m.rect)):
            m.alive = False
        # контакт со слизнем — снимает HP (с откатом, слизень живёт дальше)
        elif m.alive and m.hit_cd <= 0 and m.rect.colliderect(p.rect):
            p.take_damage(m.damage, direct=True)
            m.hit_cd = 45
        # поф при гибели слизня
        if not m.alive and getattr(m, "death_frames", None):
            GAME.vfx.append(VFX(m.x, C.GROUND_Y, m.death_frames))
    GAME.minions = [m for m in GAME.minions if m.alive]

    # одноразовые эффекты
    for fx in GAME.vfx:
        fx.update()
    GAME.vfx = [fx for fx in GAME.vfx if fx.alive]

    # всплывающие надписи
    for pop in GAME.popups:
        pop["y"] -= 0.8
        pop["life"] -= 1
    GAME.popups = [pp for pp in GAME.popups if pp["life"] > 0]

    # смерть босса
    if b.dead and b.death_timer <= 0:
        GAME.boss_defeated()

    # смерть игрока
    if p.hp <= 0:
        GAME.state = "GAMEOVER"


def draw_battle(surf):
    data = C.BOSSES[GAME.boss_index]
    bg = GAME.get_bg(data["bg"], (C.VIRTUAL_W, C.VIRTUAL_H))
    surf.blit(bg, (0, 0))
    # пол-тень
    pygame.draw.rect(surf, (0, 0, 0, 0), (0, C.GROUND_Y, C.VIRTUAL_W, 4))

    # лёгкая маркировка стен (где можно цепляться)
    wm = C.WALL_MARGIN
    wall = pygame.Surface((wm, C.GROUND_Y), pygame.SRCALPHA)
    for i in range(wm):
        a = int(70 * (1 - i / wm))
        pygame.draw.line(wall, (210, 230, 255, a), (i, 0), (i, C.GROUND_Y))
    surf.blit(wall, (0, 0))
    rwall = pygame.transform.flip(wall, True, False)
    surf.blit(rwall, (C.VIRTUAL_W - wm, 0))

    GAME.boss.draw(surf)
    for m in GAME.minions:
        m.draw(surf)
    for fx in GAME.vfx:
        fx.draw(surf)
    GAME.player.draw(surf)
    for f in GAME.fireballs:
        f.draw(surf)
    for pr in GAME.boss_projectiles:
        pr.draw(surf)
    # всплывающие надписи (MISS! и т.п.)
    for pop in GAME.popups:
        img = F_SMALL.render(pop["txt"], True, pop["color"])
        img.set_alpha(int(255 * pop["life"] / pop["max"]))
        surf.blit(img, img.get_rect(center=(int(pop["x"]), int(pop["y"]))))
    draw_hud(surf)


def draw_reward(surf):
    surf.fill(C.DARKP)
    text(surf, "БОСС ПОВЕРЖЕН!", F_HUGE, C.GOLD,
         center=(C.VIRTUAL_W // 2, 90))
    r = GAME.last_reward
    lines = [
        "Время боя: %.2f сек" % r["time"],
        "Потеряно HP: %d" % r["hp_lost"],
        "",
        "Награда: %d монет  (из %d–%d)" % (r["coins"], r["lo"], r["hi"]),
    ]
    y = 200
    for ln in lines:
        text(surf, ln, F_MED, C.WHITE, center=(C.VIRTUAL_W // 2, y))
        y += 46

    sk = GAME.last_skill
    text(surf, "НОВОЕ УМЕНИЕ:", F_MED, C.PURPLE,
         center=(C.VIRTUAL_W // 2, 470))
    text(surf, C.SKILL_NAMES[sk], F_BIG, C.GOLD,
         center=(C.VIRTUAL_W // 2, 520))
    text(surf, C.SKILL_DESC[sk], F_SMALL, C.WHITE,
         center=(C.VIRTUAL_W // 2, 565))
    text(surf, "Нажми ПРОБЕЛ, чтобы продолжить", F_SMALL, (180, 180, 190),
         center=(C.VIRTUAL_W // 2, 650))


def draw_win(surf):
    bg = GAME.get_bg("assets_bg/bg7.png", (C.VIRTUAL_W, C.VIRTUAL_H))
    surf.blit(bg, (0, 0))
    overlay = pygame.Surface((C.VIRTUAL_W, C.VIRTUAL_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surf.blit(overlay, (0, 0))
    text(surf, "ПОБЕДА!", F_HUGE, C.GOLD, center=(C.VIRTUAL_W // 2, 80))
    text(surf, "Все 7 боссов повержены. Принцесса спасена!",
         F_MED, C.WHITE, center=(C.VIRTUAL_W // 2, 160))

    lvl, desc = GAME.princess_level
    text(surf, "Принцесса: " + lvl, F_BIG, C.PURPLE,
         center=(C.VIRTUAL_W // 2, 280))
    text(surf, desc, F_SMALL, C.WHITE, center=(C.VIRTUAL_W // 2, 330))

    t = GAME.total_time / 1000.0
    text(surf, "Общее время: %.2f сек" % t, F_MED, C.GOLD,
         center=(C.VIRTUAL_W // 2, 420))
    text(surf, "Монет собрано: %d" % GAME.player.coins, F_MED, C.GOLD,
         center=(C.VIRTUAL_W // 2, 460))
    text(surf, "Нажми ПРОБЕЛ — в меню", F_SMALL, (200, 200, 200),
         center=(C.VIRTUAL_W // 2, 600))


def draw_gameover(surf):
    surf.fill((20, 8, 8))
    text(surf, "ТЫ ПАЛ В БОЮ", F_HUGE, C.RED, center=(C.VIRTUAL_W // 2, 250))
    text(surf, "Дошёл до босса %d/7" % (GAME.boss_index + 1), F_MED, C.WHITE,
         center=(C.VIRTUAL_W // 2, 350))
    text(surf, "Нажми ПРОБЕЛ — в меню", F_SMALL, (200, 200, 200),
         center=(C.VIRTUAL_W // 2, 450))


# =====================================================================
#  ОБРАБОТКА СОБЫТИЙ
# =====================================================================
def handle_event(e):
    if e.type == pygame.QUIT:
        pygame.quit(); sys.exit()
    if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()
        if GAME.state == "BATTLE":
            p = GAME.player
            if e.key in (pygame.K_SPACE, pygame.K_w):
                p.jump()
            if e.key == pygame.K_f:
                p.start_attack()
            if e.key == pygame.K_LSHIFT or e.key == pygame.K_RSHIFT:
                p.start_dash()
            if e.key == pygame.K_g:
                p.start_shield()
            if e.key == pygame.K_p:
                p.god_mode = not p.god_mode   # чит: бессмертие
            if e.key == pygame.K_e:
                fb = p.try_fireball()
                if fb:
                    GAME.fireballs.append(fb)
        elif GAME.state == "REWARD":
            if e.key == pygame.K_SPACE:
                GAME.next_after_reward()
        elif GAME.state in ("WIN", "GAMEOVER"):
            if e.key == pygame.K_SPACE:
                GAME.state = "MENU"

    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        mv = to_virt(e.pos)
        if GAME.state == "MENU":
            for r, d in GAME.menu_buttons:
                if r.collidepoint(mv):
                    GAME.start_new(d)
        elif GAME.state == "SHOP":
            for r, item in GAME.shop_buttons:
                if r.collidepoint(mv):
                    if item["id"] == "__fight__":
                        GAME.start_battle()
                    else:
                        GAME.buy(item)


# =====================================================================
#  ГЛАВНЫЙ ЦИКЛ
# =====================================================================
def main():
    while True:
        dt = clock.tick(C.FPS)
        for e in pygame.event.get():
            handle_event(e)

        keys = pygame.key.get_pressed()
        mouse_v = to_virt(pygame.mouse.get_pos())

        # курсор виден только там, где нужно кликать (меню/магазин)
        pygame.mouse.set_visible(GAME.state in ("MENU", "SHOP"))

        # музыка по состоянию
        if GAME.state == "BATTLE":
            music.play("battle", 0.45)
        else:
            music.play("calm", 0.4)

        if GAME.state == "BATTLE":
            update_battle(dt, keys)

        # отрисовка
        virt.fill(C.BLACK)
        if GAME.state == "MENU":
            draw_menu(virt, mouse_v)
        elif GAME.state == "SHOP":
            draw_shop(virt, mouse_v)
        elif GAME.state == "BATTLE":
            draw_battle(virt)
        elif GAME.state == "REWARD":
            draw_reward(virt)
        elif GAME.state == "WIN":
            draw_win(virt)
        elif GAME.state == "GAMEOVER":
            draw_gameover(virt)

        # масштаб на экран
        screen.fill(C.BLACK)
        scaled = pygame.transform.scale(virt, (_blit_w, _blit_h))
        screen.blit(scaled, (_blit_x, _blit_y))
        pygame.display.flip()


if __name__ == "__main__":
    main()
