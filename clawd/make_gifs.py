"""Generate pixel-art GIFs of Clawd's daily life.

Run: python3 clawd/make_gifs.py  (requires Pillow)
Output: clawd/gifs/*.gif
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 64, 48          # logical canvas (pixels)
SCALE = 6              # upscale factor
CAPTION_H = 40         # caption bar height (output pixels)
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs")

ORANGE = (217, 119, 87)
ORANGE_DK = (184, 92, 62)
BLACK = (30, 24, 22)
WHITE = (255, 255, 255)
CREAM = (250, 240, 225)


class Canvas:
    def __init__(self, bg):
        self.img = Image.new("RGB", (W, H), bg)
        self.d = ImageDraw.Draw(self.img)

    def rect(self, x, y, w, h, c):
        if w > 0 and h > 0:
            self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)

    def px(self, x, y, c):
        self.rect(x, y, 1, 1, c)

    def sprite(self, x, y, rows, palette):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in palette:
                    self.px(x + i, y + j, palette[ch])


def clawd(cv, x, y, eyes="open", arms="down", step=0, squash=0, legs=True):
    """Draw Clawd with top-left at (x, y). Size ~24x15."""
    y = y + squash
    bh = 12 - squash
    cv.rect(x + 2, y, 20, bh, ORANGE)
    # arms
    if arms in ("down", "left_up", "right_up"):
        if arms != "left_up":
            cv.rect(x, y + 5, 2, 4, ORANGE)
        if arms != "right_up":
            cv.rect(x + 22, y + 5, 2, 4, ORANGE)
    if arms in ("up", "left_up"):
        cv.rect(x, y + 1, 2, 4, ORANGE)
        cv.rect(x - 2, y - 2, 2, 4, ORANGE)
    if arms in ("up", "right_up"):
        cv.rect(x + 22, y + 1, 2, 4, ORANGE)
        cv.rect(x + 24, y - 2, 2, 4, ORANGE)
    # eyes
    ey = y + 3
    if eyes == "open":
        cv.rect(x + 6, ey, 2, 4, BLACK)
        cv.rect(x + 16, ey, 2, 4, BLACK)
    elif eyes == "closed":
        cv.rect(x + 5, ey + 3, 4, 1, BLACK)
        cv.rect(x + 15, ey + 3, 4, 1, BLACK)
    elif eyes == "happy":  # ^ ^
        for ex in (x + 5, x + 15):
            cv.px(ex, ey + 2, BLACK)
            cv.px(ex + 1, ey + 1, BLACK)
            cv.px(ex + 2, ey + 1, BLACK)
            cv.px(ex + 3, ey + 2, BLACK)
    elif eyes == "wide":
        cv.rect(x + 5, ey - 1, 3, 5, BLACK)
        cv.rect(x + 16, ey - 1, 3, 5, BLACK)
        cv.px(x + 5, ey - 1, WHITE)
        cv.px(x + 16, ey - 1, WHITE)
    # legs
    if legs:
        ly = y + bh
        for i, lx in enumerate((x + 3, x + 7, x + 15, x + 19)):
            lift = 1 if (step and (i % 2 == step % 2)) else 0
            cv.rect(lx, ly, 2, 3 - lift, ORANGE_DK)


def zzz(cv, x, y, t, color=(90, 90, 140)):
    z = ["111", "..1", ".1.", "1..", "111"]
    small = ["11", ".1", "1.", "11"]
    for k in range(3):
        phase = (t + k * 4) % 12
        zx, zy = x + k * 4 + phase // 3, y - phase
        cv.sprite(zx, zy, z if k == 1 else small, {"1": color})


def to_frame(cv, caption, font):
    big = cv.img.resize((W * SCALE, H * SCALE), Image.NEAREST)
    out = Image.new("RGB", (W * SCALE, H * SCALE + CAPTION_H), CREAM)
    out.paste(big, (0, 0))
    d = ImageDraw.Draw(out)
    tw = d.textlength(caption, font=font)
    d.text(((W * SCALE - tw) / 2, H * SCALE + 7), caption, fill=(80, 60, 50), font=font)
    return out


def save(name, frames, duration, caption, font):
    imgs = [to_frame(f, caption, font) for f in frames]
    pal = [im.convert("P", palette=Image.ADAPTIVE, colors=64) for im in imgs]
    path = os.path.join(OUT_DIR, name)
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=duration,
                loop=0, optimize=False, disposal=2)
    print("wrote", path, len(frames), "frames")
    return imgs


# ---------------------------------------------------------------- scenes

def window(cv, x, y, sky, sun=None, moon=False):
    cv.rect(x - 1, y - 1, 16, 14, (160, 120, 90))
    cv.rect(x, y, 14, 12, sky)
    if sun is not None:
        cv.rect(x + 4, y + sun, 5, 5, (255, 200, 60))
    if moon:
        cv.rect(x + 7, y + 2, 4, 4, (250, 240, 180))
        cv.rect(x + 9, y + 2, 2, 2, sky)
    cv.rect(x + 6, y, 2, 12, (160, 120, 90))
    cv.rect(x, y + 5, 14, 2, (160, 120, 90))


def bed(cv, blanket=(120, 150, 210)):
    cv.rect(4, 34, 40, 6, (150, 105, 75))      # frame
    cv.rect(4, 28, 3, 12, (130, 90, 60))       # headboard
    cv.rect(41, 31, 3, 9, (130, 90, 60))
    cv.rect(7, 30, 9, 4, WHITE)                # pillow
    return blanket


def scene_wake():
    frames = []
    for t in range(28):
        bg = (200, 220, 240) if t >= 10 else (150, 160, 200)
        cv = Canvas(bg)
        cv.rect(0, 40, W, 8, (190, 160, 130))
        sun = max(2, 12 - max(0, t - 8)) if t >= 8 else None
        window(cv, 46, 6, (255, 220, 170) if t >= 8 else (60, 70, 120), sun=sun)
        bed(cv)
        if t < 8:
            clawd(cv, 10, 20, eyes="closed", legs=False, squash=t % 4 // 2)
            cv.rect(14, 30, 30, 5, (120, 150, 210))
            zzz(cv, 30, 16, t)
        elif t < 14:
            clawd(cv, 10, 20, eyes="wide" if t >= 11 else "closed", legs=False)
            cv.rect(14, 30, 30, 5, (120, 150, 210))
            # alarm clock shaking
            sx = 50 + (1 if t % 2 else -1)
            cv.rect(sx, 28, 8, 7, (220, 60, 60))
            cv.rect(sx + 1, 29, 6, 5, WHITE)
            cv.px(sx + 4, 30, BLACK); cv.px(sx + 4, 31, BLACK); cv.px(sx + 5, 31, BLACK)
            cv.rect(sx - 1, 27, 2, 2, (220, 60, 60)); cv.rect(sx + 7, 27, 2, 2, (220, 60, 60))
            for k in (0, 1):
                cv.px(sx - 3 - k, 26 + k * 2, BLACK); cv.px(sx + 10 + k, 26 + k * 2, BLACK)
        else:
            k = t - 14
            jump = [0, 4, 7, 8, 7, 4, 0, 0, 0, 3, 5, 3, 0, 0][k]
            cv.rect(14, 33, 30, 2, (120, 150, 210))  # blanket kicked off
            cv.rect(50, 28, 8, 7, (220, 60, 60)); cv.rect(51, 29, 6, 5, WHITE)
            clawd(cv, 18, 19 - jump, eyes="happy", arms="up" if jump else "down")
            if k in (2, 3, 4, 10):
                for sx, sy in ((14, 12), (42, 14), (28, 6)):
                    cv.px(sx, sy - jump // 2, (255, 210, 60))
                    cv.px(sx + 1, sy + 1 - jump // 2, (255, 210, 60))
        frames.append(cv)
    return frames


def scene_coffee():
    frames = []
    for t in range(24):
        cv = Canvas((245, 225, 200))
        cv.rect(0, 38, W, 10, (170, 120, 85))   # table
        cv.rect(0, 37, W, 1, (140, 95, 65))
        sip = 8 <= t < 16
        cx, cy = 18, 23
        clawd(cv, cx, cy, eyes="happy" if sip else ("closed" if t == 20 else "open"),
              arms="right_up" if sip else "down")
        # mug
        mx, my = (43, 16) if sip else (46, 31)
        cv.rect(mx, my, 7, 7, WHITE)
        cv.rect(mx + 7, my + 2, 2, 3, WHITE)
        cv.rect(mx + 1, my + 1, 5, 1, (110, 70, 45))
        cv.rect(mx + 1, my + 3, 5, 2, ORANGE)  # logo band
        # steam
        if not sip:
            for k in range(3):
                off = (t * 1 + k * 3) % 9
                sx = mx + 1 + k * 2 + int(round(math.sin((t + k * 2) / 2)))
                sy = my - 2 - off
                if off < 7:
                    cv.px(sx, sy, (220, 220, 220))
        else:
            cv.px(mx + 3, my - 3 - t % 2, (220, 220, 220))
        if t >= 16 and t < 22:  # heart
            hy = 14 - (t - 16)
            cv.sprite(28, hy, [".1.1.", "11111", ".111.", "..1.."], {"1": (230, 80, 100)})
        frames.append(cv)
    return frames


def scene_code():
    frames = []
    code_colors = [(120, 200, 255), (255, 170, 90), (150, 230, 140), (230, 140, 230)]
    lines = [(2, 6), (4, 8), (4, 5), (2, 9), (6, 4), (4, 7), (2, 3)]
    for t in range(30):
        cv = Canvas((40, 44, 60))
        cv.rect(0, 38, W, 10, (90, 70, 60))
        # laptop
        lx, ly = 30, 14
        cv.rect(lx, ly, 26, 18, (180, 180, 190))
        cv.rect(lx + 1, ly + 1, 24, 16, (20, 22, 30))
        cv.rect(lx - 3, 32, 32, 3, (160, 160, 170))
        shown = min(len(lines), t // 3)
        scroll = max(0, shown - 6)
        for i in range(scroll, shown):
            ind, ln = lines[i]
            cv.rect(lx + 2 + ind, ly + 2 + (i - scroll) * 2, ln, 1, code_colors[i % 4])
        if t < 22 and t % 2 == 0:  # cursor
            cv.rect(lx + 2, ly + 2 + (shown - scroll) * 2, 1, 1, WHITE)
        done = t >= 22
        if done:
            cv.rect(lx + 1, ly + 1, 24, 16, (30, 120, 70))
            cv.sprite(lx + 8, ly + 4, ["........11", ".......11.", "1.....11..",
                                       "11...11...", ".11.11....", "..111.....",
                                       "...1......"], {"1": WHITE})
        jump = [0, 3, 5, 3, 0, 0, 3, 5][t - 22] if done else 0
        arms = "up" if done and jump else ("left_up" if t % 2 else "right_up")
        clawd(cv, 6, 23 - jump, eyes="happy" if done else "open", arms=arms)
        if not done:  # typing sparks
            cv.px(29 + (t % 3), 30 - (t % 2), (255, 230, 120))
        frames.append(cv)
    return frames


def scene_lunch():
    frames = []
    for t in range(30):
        cv = Canvas((255, 235, 210))
        cv.rect(0, 38, W, 10, (170, 120, 85))   # table
        cv.rect(0, 37, W, 1, (140, 95, 65))
        # wall clock at noon
        cv.d.ellipse([4, 4, 13, 13], fill=WHITE, outline=(140, 95, 65))
        cv.rect(8, 6, 1, 3, BLACK); cv.rect(9, 8, 1, 1, BLACK)
        # bowl of rice; the mound shrinks with each bite
        bites = min(4, t // 6)
        bx, by = 40, 31
        mound = 4 - bites
        if mound > 0:
            cv.d.ellipse([bx + 1, by - mound - 1, bx + 12, by + 2], fill=WHITE)
            if bites < 2:
                cv.rect(bx + 4, by - mound, 3, 2, (230, 100, 80))   # shrimp on top
            cv.rect(bx + 8, by - mound + 1, 2, 1, (90, 170, 80))    # greens
        cv.rect(bx, by, 14, 2, (90, 150, 200))
        cv.rect(bx + 1, by + 2, 12, 2, (90, 150, 200))
        cv.rect(bx + 3, by + 4, 8, 2, (70, 120, 170))
        cv.rect(bx + 2, by + 1, 10, 1, WHITE)                       # bowl pattern
        # little soup cup + steam
        cv.rect(56, 32, 5, 5, (200, 80, 70)); cv.rect(57, 32, 3, 1, (240, 190, 90))
        if t % 6 < 4:
            cv.px(58 + (t % 2), 29 - (t % 6) // 2, (220, 220, 220))
        full = t >= 24
        phase = t % 6
        eating = not full and phase in (2, 3, 4)
        clawd(cv, 12, 23,
              eyes="happy" if full or phase in (3, 4) else "open",
              arms="up" if full and t % 2 else ("right_up" if eating else "down"),
              squash=1 if phase == 4 and not full else 0)
        # chopsticks: dip into bowl, then lift a bite to the mouth
        if not full:
            if eating:
                cv.d.line([37, 20, 29, 15], fill=(150, 100, 60))
                cv.d.line([38, 22, 30, 17], fill=(150, 100, 60))
                if phase == 2:
                    cv.rect(27, 14, 3, 2, WHITE)          # rice in chopsticks
            else:
                cv.d.line([40, 29, 50, 22], fill=(150, 100, 60))
                cv.d.line([41, 30, 52, 24], fill=(150, 100, 60))
            if phase in (3, 4):                           # nom nom
                cv.sprite(16, 14 - phase + 3, ["1.1", ".1.", "1.1"], {"1": (230, 120, 60)})
                cv.px(6, 20, WHITE); cv.px(31, 19, WHITE)
        else:
            k = t - 24
            cv.sprite(22, 12 - k, [".1.1.", "11111", ".111.", "..1.."], {"1": (230, 80, 100)})
            cv.sprite(30, 14 - k // 2, [".1.1.", "11111", ".111.", "..1.."], {"1": (230, 80, 100)})
        frames.append(cv)
    return frames


def scene_garden():
    frames = []
    for t in range(28):
        cv = Canvas((200, 235, 255))
        cv.rect(0, 38, W, 10, (120, 180, 90))
        cv.rect(8 + t // 4, 6, 10, 3, WHITE); cv.rect(10 + t // 4, 4, 6, 2, WHITE)
        # pot
        px_, py = 44, 30
        cv.rect(px_, py, 10, 8, (190, 100, 70))
        cv.rect(px_ - 1, py, 12, 2, (170, 85, 60))
        # plant grows
        g = min(12, max(2, (t - 6) // 1 if t > 6 else 2))
        cv.rect(px_ + 4, py - g, 2, g, (60, 150, 60))
        if g > 5:
            cv.rect(px_ + 1, py - g + 3, 3, 2, (80, 180, 70))
            cv.rect(px_ + 6, py - g + 5, 3, 2, (80, 180, 70))
        if t >= 20:  # flower blooms
            fx, fy = px_ + 3, py - g - 3
            cv.sprite(fx, fy, [".1.", "121", ".1."], {"1": (255, 120, 160), "2": (255, 220, 60)})
            cv.px(fx - 1, fy + 1, (255, 120, 160)); cv.px(fx + 3, fy + 1, (255, 120, 160))
        # watering can held by Clawd
        tilt = 6 <= t < 20
        clawd(cv, 12, 23, eyes="happy" if t >= 20 else "open",
              arms="right_up" if tilt else "down", step=0)
        cx, cy = (36, 16) if tilt else (37, 28)
        cv.rect(cx, cy, 6, 5, (90, 140, 200))
        cv.rect(cx + 6, cy + (0 if tilt else 1), 3, 1, (90, 140, 200))
        cv.rect(cx + 1, cy - 2, 4, 1, (70, 110, 170))
        if tilt:
            for k in range(3):
                dy = (t * 2 + k * 3) % 10
                cv.px(cx + 9 + k, cy + 2 + dy, (80, 160, 240))
        frames.append(cv)
    return frames


def tree(cv, x, base):
    cv.rect(x + 3, base - 6, 2, 6, (120, 85, 55))
    cv.rect(x, base - 13, 8, 7, (70, 150, 80))
    cv.rect(x + 1, base - 15, 6, 2, (70, 150, 80))


def scene_walk():
    frames = []
    n = 24
    for t in range(n):
        cv = Canvas((255, 215, 180))
        cv.rect(46, 6, 7, 7, (255, 180, 90))  # sun
        hill_off = (t // 2) % 32
        for hx in range(-32, W + 32, 32):
            x0 = hx - hill_off
            cv.d.ellipse([x0, 28, x0 + 34, 50], fill=(230, 180, 150))
        cv.rect(0, 38, W, 10, (150, 190, 110))
        cv.rect(0, 41, W, 2, (200, 175, 130))
        tree_off = (t * 2) % 48
        for tx in (10, 58):
            tree(cv, tx - tree_off + (48 if tx - tree_off < -10 else 0), 39)
        bob = t % 2
        clawd(cv, 20, 24 - bob, eyes="open" if t % 12 else "closed", step=1 + t % 2)
        # musical notes
        nx, ny = 46 - (t % 8), 18 - (t % 8) // 2
        cv.sprite(nx, ny, ["..11", "..1.", "..1.", "111.", "11.."], {"1": (120, 80, 160)})
        frames.append(cv)
    return frames


def scene_sleep():
    frames = []
    stars = [(6, 5), (20, 3), (34, 8), (58, 4), (26, 12), (12, 14), (52, 16)]
    for t in range(24):
        cv = Canvas((40, 45, 85))
        for i, (sx, sy) in enumerate(stars):
            if (t // 2 + i) % 4:
                cv.px(sx, sy, (255, 245, 200))
            else:
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.px(sx + dx, sy + dy, (255, 245, 200))
        cv.d.ellipse([46, 5, 55, 14], fill=(250, 240, 180))
        cv.d.ellipse([49, 3, 58, 12], fill=(40, 45, 85))
        cv.rect(0, 40, W, 8, (70, 60, 90))
        bed(cv)
        breathe = 1 if (t // 4) % 2 else 0
        clawd(cv, 10, 20, eyes="closed", legs=False, squash=breathe)
        cv.rect(14, 30, 30, 5, (230, 150, 170))
        for k in range(0, 30, 6):
            cv.rect(14 + k, 31, 3, 1, (250, 200, 210))
        zzz(cv, 30, 18, t, color=(200, 200, 255))
        frames.append(cv)
    return frames


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    font = ImageFont.truetype(FONT_PATH, 22)
    scenes = [
        ("01_wake_up.gif", scene_wake, 140, "07:00 起床啦！"),
        ("02_coffee.gif", scene_coffee, 150, "08:00 来杯咖啡"),
        ("03_coding.gif", scene_code, 130, "10:00 认真敲代码"),
        ("04_lunch.gif", scene_lunch, 150, "12:00 干饭时间！"),
        ("05_garden.gif", scene_garden, 150, "14:00 给小花浇水"),
        ("06_walk.gif", scene_walk, 130, "18:00 傍晚散步"),
        ("07_sleep.gif", scene_sleep, 180, "23:00 晚安 Zzz"),
    ]
    day = []
    for name, fn, dur, cap in scenes:
        frames = fn()
        imgs = save(name, frames, dur, cap, font)
        # for the full-day montage, normalize timing to ~130ms frames
        reps = max(1, round(dur / 130))
        for im in imgs:
            day.extend([im] * reps)
    pal = [im.convert("P", palette=Image.ADAPTIVE, colors=64) for im in day]
    path = os.path.join(OUT_DIR, "00_clawd_day.gif")
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=130, loop=0, disposal=2)
    print("wrote", path, len(day), "frames")


if __name__ == "__main__":
    main()
