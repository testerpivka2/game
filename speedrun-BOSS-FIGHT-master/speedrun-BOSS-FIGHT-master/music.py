"""Менеджер фоновой музыки.

Ожидает готовые файлы в папке music:
- music/main.(ogg|mp3|wav)
- music/battle.(ogg|mp3|wav)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(HERE, "music")


# ---------------- менеджер ----------------
_inited = False
_current = None


def _find(name):
    # Совместимость со старым названием трека.
    if name == "calm":
        name = "main"
    for ext in (".ogg", ".mp3", ".wav"):
        p = os.path.join(MUSIC_DIR, name + ext)
        if os.path.exists(p):
            return p
    return None


def ensure_tracks_exist():
    os.makedirs(MUSIC_DIR, exist_ok=True)
    if not _find("main"):
        print("music missing: expected music/main.(ogg|mp3|wav)")
    if not _find("battle"):
        print("music missing: expected music/battle.(ogg|mp3|wav)")


def init():
    global _inited
    import pygame
    try:
        pygame.mixer.init()
        _inited = True
    except Exception as e:
        print("mixer init fail:", e)
        _inited = False
    ensure_tracks_exist()


def play(name, volume=0.1):
    """name: 'main' или 'battle' (также поддерживается алиас 'calm')."""
    global _current
    if not _inited:
        return
    if _current == name:
        return
    path = _find(name)
    if not path:
        return
    import pygame
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        _current = name
    except Exception as e:
        print("music play fail:", e)


def stop():
    global _current
    if _inited:
        import pygame
        pygame.mixer.music.stop()
    _current = None
