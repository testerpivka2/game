"""Загрузка и нарезка спрайтов."""
import os
import pygame
import config as C

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

_cache = {}


def path(name):
    return os.path.join(ASSET_DIR, name)


def load_image(name):
    if name in _cache:
        return _cache[name]
    img = pygame.image.load(path(name)).convert_alpha()
    _cache[name] = img
    return img


def slice_strip(name, fw, fh, count=None, scale=1.0, row=0):
    """Нарезать горизонтальную полосу кадров (одна строка).

    Если count не задан — считается автоматически как ширина листа // fw.
    """
    sheet = load_image(name)
    if count is None:
        count = max(1, sheet.get_width() // fw)
    frames = []
    for i in range(count):
        rect = pygame.Rect(i * fw, row * fh, fw, fh)
        frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), rect)
        if scale != 1.0:
            frame = pygame.transform.scale(
                frame, (int(fw * scale), int(fh * scale)))
        frames.append(frame)
    return frames


def slice_grid(name, fw, fh, indices, scale=1.0):
    """Нарезать кадры из сетки по индексам (чтение слева-направо, сверху-вниз)."""
    sheet = load_image(name)
    cols = sheet.get_width() // fw
    frames = []
    for idx in indices:
        col = idx % cols
        rrow = idx // cols
        rect = pygame.Rect(col * fw, rrow * fh, fw, fh)
        frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), rect)
        if scale != 1.0:
            frame = pygame.transform.scale(
                frame, (int(fw * scale), int(fh * scale)))
        frames.append(frame)
    return frames


def tint(frames, color):
    """Подкрасить список кадров (умножение цвета), сохраняя альфу."""
    out = []
    for f in frames:
        nf = f.copy()
        overlay = pygame.Surface(f.get_size(), pygame.SRCALPHA)
        overlay.fill(color)
        nf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        out.append(nf)
    return out


def flip(frames):
    return [pygame.transform.flip(f, True, False) for f in frames]


def bottom_pad(surf):
    """Сколько полностью прозрачных строк снизу у кадра (отступ под ногами)."""
    try:
        m = pygame.mask.from_surface(surf, 1)
    except Exception:
        return 0
    w, h = surf.get_size()
    for y in range(h - 1, -1, -1):
        for x in range(0, w, 2):
            if m.get_at((x, y)):
                return h - 1 - y
    return 0


def scale_bg(name, size):
    img = load_image(name)
    return pygame.transform.scale(img, size)


# --------- Готовые наборы анимаций ----------
PLAYER_DIR = "assets_player"
BOSS_FALLBACK = "assets_boss1"   # заглушка для пустых папок боссов (боец 1-й лок.)


def load_player_anims():
    s = C.PLAYER_SCALE
    d = PLAYER_DIR + "/"
    return {
        "idle":    slice_grid(d + "idle.png", 60, 60, [0, 1, 2], s),
        "run":     slice_strip(d + "run.png", 60, 60, None, s),
        "attack":  slice_strip(d + "attack.png", 60, 60, None, s),
        "attack2": slice_strip(d + "attack2.png", 60, 60, None, s),
        "dash":    slice_strip(d + "dash.png", 60, 60, None, s),
    }


def load_grid_anim(folder, file, fw, fh, scale=1.0):
    """Нарезать лист СЕТКОЙ fw x fh построчно (cols*rows кадров) и масштабировать."""
    rel = folder + "/" + file
    sheet = load_image(rel)
    W, H = sheet.get_size()
    cols = max(1, W // fw)
    rows = max(1, H // fh)
    frames = []
    for r in range(rows):
        for c in range(cols):
            fr = pygame.Surface((fw, fh), pygame.SRCALPHA)
            fr.blit(sheet, (0, 0), pygame.Rect(c * fw, r * fh, fw, fh))
            if scale != 1.0:
                fr = pygame.transform.scale(
                    fr, (max(1, int(fw * scale)), max(1, int(fh * scale))))
            frames.append(fr)
    return frames


def load_boss_spec_anims(folder):
    """Загрузить словарь анимаций босса по config.BOSS_SPEC[folder]."""
    spec = C.BOSS_SPEC.get(folder) or C.BOSS_SPEC[BOSS_FALLBACK]
    scale = spec["scale"]
    out = {}
    for state, (file, fw, fh) in spec["anims"].items():
        try:
            out[state] = load_grid_anim(folder, file, fw, fh, scale)
        except Exception as e:
            print("anim load fail:", folder, file, e)
    return out


def load_boss1_anims(scale):
    """Демон boss7: ровная сетка 288x160, 22x5.

    Ряды: 0=idle, 1=walk(run), 2=attack, 3=cast(спец), 4=death(hurt).
    Берём только заполненные ячейки каждого ряда (хвост-пустышки отбрасываем).
    """
    sheet = load_image("assets_boss7/sheet.png")
    FW, FH = 288, 160
    cols = sheet.get_width() // FW
    rows = sheet.get_height() // FH
    mask = pygame.mask.from_surface(sheet, 1)

    def filled(c, r):
        for yy in range(r * FH, (r + 1) * FH, 6):
            for xx in range(c * FW, (c + 1) * FW, 6):
                if mask.get_at((xx, yy)):
                    return True
        return False

    def row_frames(r):
        cells = [c for c in range(cols) if filled(c, r)]
        out = []
        for c in cells:
            fr = pygame.Surface((FW, FH), pygame.SRCALPHA)
            fr.blit(sheet, (0, 0), pygame.Rect(c * FW, r * FH, FW, FH))
            if scale != 1.0:
                fr = pygame.transform.scale(
                    fr, (int(FW * scale), int(FH * scale)))
            out.append(fr)
        return out or [pygame.Surface((10, 10), pygame.SRCALPHA)]

    rf = {i: row_frames(i) for i in range(rows)}
    return {
        "idle":   rf.get(0),
        "run":    rf.get(1, rf[0]),
        "attack": rf.get(2, rf[0]),
        "cast":   rf.get(3, rf[0]),
        "death":  rf.get(4, rf[0]),
    }
