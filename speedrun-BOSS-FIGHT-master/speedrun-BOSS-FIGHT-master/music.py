"""Процедурная чиптюн-музыка + менеджер воспроизведения.

Генерирует music/calm.wav и music/battle.wav при первом запуске.
Если положить свой файл music/calm.(ogg|mp3|wav) или music/battle.* —
игра возьмёт его вместо сгенерированного.
"""
import os
import math
import wave
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(HERE, "music")
SR = 22050


# ---------------- синтез ----------------
def _midi_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


def _env(i, total, atk, rel):
    """Огибающая 0..1 (атака/спад) для убирания щелчков."""
    if i < atk:
        return i / atk
    if i > total - rel:
        return max(0.0, (total - i) / rel)
    return 1.0


def _square(phase, duty=0.5):
    return 1.0 if (phase % 1.0) < duty else -1.0


def _tri(phase):
    p = phase % 1.0
    return 4.0 * abs(p - 0.5) - 1.0


def _render(events, length_s, drums=None):
    """events: список (start_s, dur_s, midi, amp, wave) -> буфер float."""
    n = int(length_s * SR)
    buf = [0.0] * n
    for (start, dur, midi, amp, wav) in events:
        f = _midi_freq(midi)
        s0 = int(start * SR)
        d = int(dur * SR)
        atk = max(1, int(0.01 * SR))
        rel = max(1, int(min(0.12, dur * 0.4) * SR))
        for i in range(d):
            idx = s0 + i
            if idx >= n:
                break
            phase = f * (i / SR)
            if wav == "sq":
                v = _square(phase)
            elif wav == "sq25":
                v = _square(phase, 0.25)
            else:
                v = _tri(phase)
            buf[idx] += v * amp * _env(i, d, atk, rel)
    # ударные (battle)
    if drums:
        for (t, kind) in drums:
            idx0 = int(t * SR)
            if kind == "kick":
                d = int(0.12 * SR)
                for i in range(d):
                    if idx0 + i >= n:
                        break
                    ph = 90 * (i / SR) * math.exp(-6 * i / d)
                    buf[idx0 + i] += math.sin(2 * math.pi * ph) * \
                        0.5 * math.exp(-5 * i / d)
            else:  # hat — короткий шум
                d = int(0.03 * SR)
                seed = idx0
                for i in range(d):
                    if idx0 + i >= n:
                        break
                    seed = (seed * 1103515245 + 12345) & 0x7fffffff
                    nz = (seed / 0x3fffffff) - 1.0
                    buf[idx0 + i] += nz * 0.12 * math.exp(-30 * i / d)
    return buf


def _write_wav(path, buf):
    # нормализация
    peak = max(1e-6, max(abs(x) for x in buf))
    g = 0.9 / peak
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for x in buf:
            v = int(max(-1.0, min(1.0, x * g)) * 32767)
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


def _gen_calm(path):
    bpm = 84
    beat = 60.0 / bpm
    bar = beat * 4
    # прогрессия Am F C G (в C мажоре), 2 круга = 8 тактов
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    prog = chords + chords
    length = len(prog) * bar
    ev = []
    for bi, ch in enumerate(prog):
        t0 = bi * bar
        # пад — выдержанный аккорд
        for note in ch:
            ev.append((t0, bar, note + 12, 0.10, "tri"))
        # арпеджио восьмыми
        seq = [ch[0], ch[1], ch[2], ch[1]] * 2
        for k, note in enumerate(seq):
            ev.append((t0 + k * (beat / 2), beat / 2 * 0.9,
                       note + 24, 0.16, "tri"))
        # бас
        ev.append((t0, beat * 2, ch[0], 0.18, "sq25"))
        ev.append((t0 + beat * 2, beat * 2, ch[0], 0.18, "sq25"))
    _write_wav(path, _render(ev, length))


def _gen_battle(path):
    bpm = 150
    beat = 60.0 / bpm
    bar = beat * 4
    # Em C G D
    chords = [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]]
    prog = chords + chords
    length = len(prog) * bar
    ev = []
    drums = []
    for bi, ch in enumerate(prog):
        t0 = bi * bar
        # бас восьмыми (драйв)
        for k in range(8):
            ev.append((t0 + k * (beat / 2), beat / 2 * 0.95,
                       ch[0] - 12, 0.22, "sq"))
        # арп шестнадцатыми
        arp = [ch[0], ch[1], ch[2], ch[1]] * 4
        for k, note in enumerate(arp):
            ev.append((t0 + k * (beat / 4), beat / 4 * 0.9,
                       note + 12, 0.13, "sq25"))
        # ударные
        for k in range(4):
            drums.append((t0 + k * beat, "kick"))
            drums.append((t0 + k * beat + beat / 2, "hat"))
    _write_wav(path, _render(ev, length, drums))


# ---------------- менеджер ----------------
_inited = False
_current = None


def _find(name):
    for ext in (".ogg", ".mp3", ".wav"):
        p = os.path.join(MUSIC_DIR, name + ext)
        if os.path.exists(p):
            return p
    return None


def ensure_generated():
    os.makedirs(MUSIC_DIR, exist_ok=True)
    if not _find("calm"):
        try:
            _gen_calm(os.path.join(MUSIC_DIR, "calm.wav"))
        except Exception as e:
            print("calm gen fail:", e)
    if not _find("battle"):
        try:
            _gen_battle(os.path.join(MUSIC_DIR, "battle.wav"))
        except Exception as e:
            print("battle gen fail:", e)


def init():
    global _inited
    import pygame
    try:
        pygame.mixer.init()
        _inited = True
    except Exception as e:
        print("mixer init fail:", e)
        _inited = False
    ensure_generated()


def play(name, volume=0.5):
    """name: 'calm' или 'battle'."""
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
