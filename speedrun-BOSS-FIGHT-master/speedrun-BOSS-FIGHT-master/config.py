VIRTUAL_W = 1280
VIRTUAL_H = 720
GROUND_Y = 620

FPS = 60

WHITE = (240, 240, 240)
BLACK = (12, 12, 16)
RED = (200, 50, 50)
GREEN = (60, 200, 90)
BLUE = (70, 130, 220)
GOLD = (235, 195, 70)
PURPLE = (150, 80, 200)
DARKP = (30, 24, 40)
GREY = (90, 90, 100)

DIFFICULTIES = {
    "EASY":   {"hp": 20, "label": "ЛЁГКАЯ"},
    "MEDIUM": {"hp": 12, "label": "СРЕДНЯЯ"},
    "HARD":   {"hp": 7,  "label": "ТЯЖЁЛАЯ"},
}

REWARD_TUNING = {
    "EASY":   (1, 20, 1.5),
    "MEDIUM": (1, 15, 1.25),
    "HARD":   (0, 10, 1.1),
}

DODGE_CHANCE = {
    "EASY":   1 / 8,  # 1/8
    "MEDIUM": 1 / 7,  # 1/7
    "HARD":   1 / 4,  # 1/4
}

HIT_KNOCKBACK = 120

PLAYER_SCALE = 2.6
PLAYER_SPEED = 4.6
PLAYER_JUMP = 15.5
GRAVITY = 0.7
PLAYER_BASE_DAMAGE = 10
DASH_SPEED = 16
DASH_TIME = 12
DASH_COOLDOWN = 45
ATTACK_COOLDOWN = 60

WALL_MARGIN = 40
WALL_SLIDE_SPEED = 1.8
WALL_JUMP_VY = 15.0
WALL_JUMP_PUSH = 6.5
WALL_JUMP_DECAY = 0.82

BOSS_SCALE = 2.2
BOSS_FINAL_SCALE = 2.7

BOSSES = [
    {"name": "Страж Леса",       "hp": 35, "speed": 4, "cd": 70, "bg": "assets_bg/bg1.png", "type": "charger",  "art": "assets_boss1"},
    {"name": "Бамбуковый Дух",   "hp": 45, "speed": 2.3, "cd": 65, "bg": "assets_bg/bg2.png", "type": "jumper",   "art": "assets_boss2"},
    {"name": "Туманный Самурай", "hp": 55, "speed": 2.6, "cd": 60, "bg": "assets_bg/bg3.png", "type": "ranged",   "art": "assets_boss3"},
    {"name": "Алый Странник",    "hp": 65, "speed": 2.8, "cd": 55, "bg": "assets_bg/bg4.png", "type": "berserk",  "art": "assets_boss4"},
    {"name": "Хозяин Тории",     "hp": 75, "speed": 3.0, "cd": 52, "bg": "assets_bg/bg5.png", "type": "summoner", "art": "assets_boss5"},
    {"name": "Пламенный Сёгун",  "hp": 95, "speed": 3.2, "cd": 48, "bg": "assets_bg/bg6.png", "type": "ranged",   "art": "assets_boss6"},
    {"name": "ТЁМНЫЙ ДАЙМЁ",     "hp": 150, "speed": 3.4, "cd": 44, "bg": "assets_bg/bg7.png", "type": "demon",    "art": "assets_boss7"},
]

SHIELD_TIME = 75
SHIELD_COOLDOWN = 90

PARRY_TIME = 15
PARRY_COOLDOWN = 120

FIREBALL_COOLDOWN = 90

AURA_BUDGET = 3.0
AURA_OFF_TIME = 300
AURA_DPS = 0.04

HP_REGEN_FRAMES = 180
MANA_REGEN_FRAMES = 180

BOSS_PROJ_COLOR = {
    "ranged":   (120, 220, 160),
    "summoner": (200, 140, 240),
    "jumper":   (220, 200, 120),
    "demon":    (255, 120, 200),
}

BOSS_TINTS = [(255, 255, 255)] * 7

BOSS_SPEC = {
    "assets_boss1": {
        "scale": 3.4,
        "anims": {
            "idle": ("idle.png", 96, 96), "run": ("run.png", 96, 96),
            "attack": ("attack.png", 96, 96),
            "flinch": ("hurt.png", 96, 96), "death": ("hurt.png", 96, 96)},
        "abilities": [
            {"kind": "charge", "cd": 140},
            {"kind": "jump", "cd": 160}],
    },
    "assets_boss2": {
        "scale": 2.2,
        "anims": {
            "idle": ("idle.png", 100, 100), "run": ("idle.png", 100, 100),
            "float": ("idle2.png", 100, 100),
            "attack": ("attacking.png", 100, 100),
            "death": ("death.png", 100, 100),
            "cast": ("summon.png", 100, 100),
            "spin": ("skill1.png", 100, 100)},
        "blink": {"cd": 180, "chance": 0.5, "offset": 95},
        "abilities": [
            {"kind": "spin", "min_dur": 240, "max_dur": 480, "cd": 420,
             "spin_frames": [6, 7, 8]},
            {"kind": "summon", "anim": "cast", "fire_frame": 4,
             "minion": ("summonIdle.png", 50, 50, 2.0),
             "appear": ("summonAppear.png", 50, 50, 2.0),
             "death_fx": ("summonDeath.png", 50, 50, 2.0),
             "count": 3, "cd": 200}],
    },
    "assets_boss3": {
        "scale": 1.7,
        "anims": {
            "idle": ("Idle.png", 128, 128), "run": ("Walk.png", 128, 128),
            "charge": ("Run.png", 128, 128),
            "attack": ("Attack_1.png", 128, 128),
            "attack2": ("Attack_2.png", 128, 128),
            "flinch": ("Hurt.png", 128, 128), "death": ("Dead.png", 128, 128),
            "jump": ("Jump.png", 128, 128),
            "cast_ball": ("Light_ball.png", 128, 128),
            "cast_beam": ("Light_charge.png", 128, 128)},
        "abilities": [
            {"kind": "projectile", "anim": "cast_ball", "fire_frame": 5,
             "proj": ("Charge.png", 64, 64, 1.6), "speed": 7, "radius": 22,
             "cd": 130},
            {"kind": "beam", "anim": "cast_beam", "fire_frame": 6,
             "reach": 540, "cd": 220},
            {"kind": "charge", "anim": "charge", "cd": 160},
            {"kind": "jump", "cd": 160}],
    },
    "assets_boss4": {
        "scale": 1.7,
        "anims": {
            "idle": ("Idle.png", 128, 128), "run": ("Walk.png", 128, 128),
            "charge": ("Run.png", 128, 128),
            "attack": ("Attack_1.png", 128, 128),
            "flinch": ("Hurt.png", 128, 128), "death": ("Dead.png", 128, 128),
            "jump": ("Jump.png", 128, 128),
            "cast_sphere": ("Magic_sphere.png", 128, 128),
            "cast_arrow": ("Magic_arrow.png", 128, 128),
            "cast_volley": ("Attack_2.png", 128, 128)},
        "time_scaling": {"period": 420, "speed_mul": 0.18, "max_level": 6},
        "flight": {"cd": 300, "proj": ("Charge_1.png", 128, 128, 0.7),
                   "interval": 65, "speed": 6, "radius": 20,
                   "color": (120, 170, 255)},
        "abilities": [
            {"kind": "projectile", "anim": "cast_sphere", "fire_frame": 10,
             "proj": ("Charge_1.png", 128, 128, 0.7), "speed": 5, "radius": 22,
             "cd": 150},
            {"kind": "projectile", "anim": "cast_arrow", "fire_frame": 4,
             "proj": ("Charge_2.png", 128, 128, 0.7), "speed": 9, "radius": 15,
             "spin": True, "cd": 110},
            {"kind": "volley", "anim": "cast_volley", "fire_frame": 7,
             "proj": ("Charge_2.png", 128, 128, 0.6), "count": 3, "spread": 0.32,
             "speed": 8, "radius": 13, "spin": True, "cd": 170},
            {"kind": "charge", "anim": "charge", "cd": 170},
            {"kind": "jump", "cd": 160}],
    },
    "assets_boss5": {
        "scale": 2.4,
        "anims": {
            "idle": ("idle.png", 247, 87), "run": ("walk.png", 247, 87),
            "attack": ("Attack 1.png", 247, 87),
            "attack2": ("Attack 2.png", 247, 87),
            "flinch": ("hit.png", 247, 87), "death": ("death.png", 247, 87),
            "cast_saw": ("Pre-Attack 3.png", 247, 87),
            "nova": ("end-Attack 3.png", 247, 87)},
        "abilities": [
            {"kind": "projectile", "anim": "cast_saw", "fire_frame": 2,
             "proj": ("mid-Attack 3.png", 247, 87, 1.0), "speed": 6,
             "radius": 26, "cd": 150},
            {"kind": "aoe", "anim": "nova", "fire_frame": 3, "radius": 175,
             "cd": 220},
            {"kind": "charge", "cd": 140},
            {"kind": "jump", "cd": 160}],
    },
    "assets_boss6": {
        "scale": 1.7,
        "anims": {
            "idle": ("Idle.png", 128, 128), "run": ("Walk.png", 128, 128),
            "charge": ("Run.png", 128, 128),
            "attack": ("Attack_2.png", 128, 128),
            "attack2": ("Attack_1.png", 128, 128),
            "flinch": ("Hurt.png", 128, 128), "death": ("Dead.png", 128, 128),
            "jump": ("Jump.png", 128, 128),
            "cast_fire": ("Fireball.png", 128, 128),
            "cast_jet": ("Flame_jet.png", 128, 128)},
        "abilities": [
            {"kind": "projectile", "anim": "cast_fire", "fire_frame": 5,
             "proj": ("Charge.png", 64, 64, 1.6), "speed": 7, "radius": 22,
             "spin": True, "cd": 130},
            {"kind": "beam", "anim": "cast_jet", "fire_frame": 5,
             "reach": 500, "cd": 220},
            {"kind": "charge", "anim": "charge", "cd": 170},
            {"kind": "jump", "cd": 160}],
    },
}

SKILLS = ["dash", "parry", "resist", "mana", "fireball", "double_jump"]

SKILL_ORDER_FIXED = [
    "dash",
    "parry",
    "resist",
    "mana",
    "fireball",
    "double_jump",
]
SKILL_NAMES = {
    "fireball":    "ФАЙРБОЛ (Q)",
    "dash":        "РЫВОК (Shift)",
    "double_jump": "ДВОЙНОЙ ПРЫЖОК",
    "parry":       "ПАРИРОВАНИЕ (E)",
    "resist":      "СОПРОТИВЛЕНИЕ",
    "mana":        "ИСТОЧНИК МАНЫ",
}
SKILL_DESC = {
    "fireball":    "Бросай огонь во врага. Стоит 1 ману.",
    "dash":        "Быстрый рывок с неуязвимостью.",
    "double_jump": "Второй прыжок в воздухе.",
    "parry":       "Защита в точный момент окна атаки.",
    "resist":      "Снижает весь получаемый урон на 20%.",
    "mana":        "Открывает доступ к мане.",
}

SHOP_ITEMS = [
    {"id": "speed",    "name": "Скорость +",    "desc": "+12% к скорости бега",   "cost": 5,  "grow": 3},
    {"id": "damage",   "name": "Урон +",        "desc": "+0.5 к урону меча",      "cost": 6,  "grow": 4},
    {"id": "maxhp",    "name": "Макс. HP +1",   "desc": "Увеличить макс. HP",     "cost": 7,  "grow": 5},
    {"id": "maxmana",  "name": "Макс. мана +1", "desc": "Увеличить макс. ману",   "cost": 6,  "grow": 4},
    {"id": "healhp",   "name": "Зелье HP",      "desc": "Восстановить 5 HP",      "cost": 3,  "grow": 2},
    {"id": "healmana", "name": "Зелье маны",    "desc": "Восстановить всю ману",  "cost": 3,  "grow": 2},
]
