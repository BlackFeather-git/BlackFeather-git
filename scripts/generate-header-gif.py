import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH = 840
HEIGHT = 260
BG_COLOR = (10, 12, 16)
BAR_COLOR = (18, 22, 31)
BORDER_COLOR = (36, 43, 53)

FONT_PATH = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
BOLD_FONT_PATH = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"

font_sm = ImageFont.truetype(FONT_PATH, 11)
font_mono = ImageFont.truetype(FONT_PATH, 13)
font_bold = ImageFont.truetype(BOLD_FONT_PATH, 13)
font_ascii = ImageFont.truetype(BOLD_FONT_PATH, 13)
font_title = ImageFont.truetype(BOLD_FONT_PATH, 24)

TMP_DIR = "/tmp/header_frames"
os.makedirs(TMP_DIR, exist_ok=True)

def draw_window_base():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([0, 0, WIDTH, 34], fill=BAR_COLOR)
    
    # Window controls
    draw.ellipse([14, 12, 24, 22], fill=(239, 68, 68))
    draw.ellipse([30, 12, 40, 22], fill=(234, 179, 8))
    draw.ellipse([46, 12, 56, 22], fill=(34, 197, 94))
    
    # Title text
    draw.text((68, 10), "amish@cachyos-hyprland ~ (wayland)", font=font_sm, fill=(100, 116, 139))
    
    # Border
    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=BORDER_COLOR, width=1)
    return img, draw

frames = []
frame_idx = 0

def save_frame(img, count=1):
    global frame_idx
    for _ in range(count):
        img.save(f"{TMP_DIR}/frame_{frame_idx:04d}.png")
        frame_idx += 1

# Phase 1: Boot Sequence
boot_lines = [
    ("[  0.000000] ", (56, 189, 248), "Linux cachyos-x86_64 booting...", (226, 232, 240)),
    ("[  0.041892] ", (56, 189, 248), "Hyprland: Wayland Compositor initialised", (148, 163, 184)),
    ("[  0.089104] ", (56, 189, 248), "ACPI: HP Omen WMI & HyperX platform driver loaded", (148, 163, 184)),
    ("[  0.112040] ", (56, 189, 248), "Network: Qualcomm MDM9607 modem link established", (148, 163, 184)),
    ("[    OK    ] ", (34, 197, 94), "Reached target Multi-User System.", (226, 232, 240)),
]

for i in range(1, len(boot_lines) + 1):
    img, draw = draw_window_base()
    y = 50
    for prefix, p_col, text, t_col in boot_lines[:i]:
        draw.text((24, y), prefix, font=font_mono, fill=p_col)
        draw.text((150, y), text, font=font_mono, fill=t_col)
        y += 24
    save_frame(img, count=2)

save_frame(img, count=4)

# Phase 2: Shell Prompt & Typing whoami
cmd1 = "whoami"
for c_len in range(len(cmd1) + 1):
    img, draw = draw_window_base()
    # Prompt
    draw.text((24, 52), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 52), "~", font=font_bold, fill=(168, 85, 247))
    draw.text((60, 52), cmd1[:c_len] + ("_" if c_len < len(cmd1) else ""), font=font_mono, fill=(241, 245, 249))
    save_frame(img, count=1)

# Response to whoami
img, draw = draw_window_base()
draw.text((24, 52), "➜", font=font_bold, fill=(56, 189, 248))
draw.text((42, 52), "~", font=font_bold, fill=(168, 85, 247))
draw.text((60, 52), "whoami", font=font_mono, fill=(241, 245, 249))
draw.text((24, 76), "Amish (BlackFeather)", font=font_bold, fill=(34, 197, 94))
save_frame(img, count=3)

# Phase 3: Typing init --profile
cmd2 = "init --profile"
for c_len in range(len(cmd2) + 1):
    img, draw = draw_window_base()
    draw.text((24, 52), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 52), "~", font=font_bold, fill=(168, 85, 247))
    draw.text((60, 52), "whoami", font=font_mono, fill=(241, 245, 249))
    draw.text((24, 76), "Amish (BlackFeather)", font=font_bold, fill=(34, 197, 94))
    
    draw.text((24, 106), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 106), "~", font=font_bold, fill=(168, 85, 247))
    draw.text((60, 106), cmd2[:c_len] + ("_" if c_len < len(cmd2) else ""), font=font_mono, fill=(241, 245, 249))
    save_frame(img, count=1)

save_frame(img, count=2)

# Phase 4: AMISH Page Resolution
ascii_art = [
    r"    ___   __  __ _____ ____  __  __ ",
    r"   / _ \ |  \/  |_   _/ ___||  \/  |",
    r"  / /_\ \| |\/| | | | \___ \| |\/| |",
    r"  |  _  || |  | | | |  ___) | |  | |",
    r"  |_| |_||_|  |_| |_| |____/|_|  |_|",
]

for blink in [True, False, True, False]:
    img, draw = draw_window_base()
    # Draw ASCII banner
    y = 48
    for line in ascii_art:
        draw.text((24, y), line, font=font_ascii, fill=(56, 189, 248))
        y += 18
    
    # Subheader
    draw.text((24, 150), "Systems Architecture  •  Hardware Reverse Engineering  •  Native Fluid UI", font=font_bold, fill=(241, 245, 249))
    draw.text((24, 174), "Arch Linux / CachyOS (Hyprland)  •  Linux Kernel C  •  Rust  •  Material 3", font=font_mono, fill=(148, 163, 184))
    
    # Prompt at bottom
    draw.text((24, 214), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 214), "~", font=font_bold, fill=(168, 85, 247))
    draw.text((60, 214), "ready" + (" █" if blink else ""), font=font_mono, fill=(34, 197, 94))
    save_frame(img, count=10)

print(f"Rendered {frame_idx} frames. Assembling GIF with ffmpeg...")

# Encode GIF using high-quality two-pass palette ffmpeg
out_gif = "/home/raven/Projects/BlackFeather-git/assets/header.gif"
cmd = (
    f"ffmpeg -y -framerate 12 -i {TMP_DIR}/frame_%04d.png "
    f"-vf 'fps=12,scale={WIDTH}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer' "
    f"{out_gif}"
)
subprocess.run(cmd, shell=True, check=True)

size = os.path.getsize(out_gif)
print(f"Generated {out_gif}: {size} bytes ({size / 1024:.1f} KB)")
