import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH = 840
HEIGHT = 220
BG_COLOR = (10, 12, 16)
BAR_COLOR = (18, 22, 31)
BORDER_COLOR = (36, 43, 53)

FONT_REG = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"

font_sm = ImageFont.truetype(FONT_REG, 11)
font_mono = ImageFont.truetype(FONT_REG, 13)
font_bold = ImageFont.truetype(FONT_BOLD, 13)
font_name = ImageFont.truetype(FONT_BOLD, 18)

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

frame_idx = 0

def save_frame(img, count=1):
    global frame_idx
    for _ in range(count):
        img.save(f"{TMP_DIR}/frame_{frame_idx:04d}.png")
        frame_idx += 1

# Step 1: Initial Prompt & Type "whoami"
cmd1 = "whoami"
for c in range(len(cmd1) + 1):
    img, draw = draw_window_base()
    draw.text((24, 48), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 48), "~", font=font_bold, fill=(168, 85, 247))
    cursor = "_" if c < len(cmd1) else ""
    draw.text((60, 48), cmd1[:c] + cursor, font=font_mono, fill=(241, 245, 249))
    save_frame(img, count=1)

save_frame(img, count=2)

# Step 2: Resolve whoami -> Amish (BlackFeather)
img, draw = draw_window_base()
draw.text((24, 48), "➜", font=font_bold, fill=(56, 189, 248))
draw.text((42, 48), "~", font=font_bold, fill=(168, 85, 247))
draw.text((60, 48), "whoami", font=font_mono, fill=(241, 245, 249))
draw.text((24, 72), "Amish (BlackFeather)", font=font_name, fill=(34, 197, 94))
save_frame(img, count=3)

# Step 3: Type "cat /etc/profile"
cmd2 = "cat /etc/profile"
for c in range(len(cmd2) + 1):
    img, draw = draw_window_base()
    draw.text((24, 48), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 48), "~", font=font_bold, fill=(168, 85, 247))
    draw.text((60, 48), "whoami", font=font_mono, fill=(241, 245, 249))
    draw.text((24, 72), "Amish (BlackFeather)", font=font_name, fill=(34, 197, 94))
    
    draw.text((24, 106), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 106), "~", font=font_bold, fill=(168, 85, 247))
    cursor = "_" if c < len(cmd2) else ""
    draw.text((60, 106), cmd2[:c] + cursor, font=font_mono, fill=(241, 245, 249))
    save_frame(img, count=1)

save_frame(img, count=2)

# Step 4: Display clean, modern profile dossier
lines = [
    ("Focus   : ", (56, 189, 248), "Native Applications  •  Linux Kernel Modules  •  Fluid Motion", (226, 232, 240)),
    ("Design  : ", (56, 189, 248), "Expressive Material 3  •  Calibrated Physics  •  Zero Bloat", (226, 232, 240)),
    ("System  : ", (56, 189, 248), "Arch Linux / CachyOS (x86_64)  •  Hyprland (Wayland)  •  Rust / C / Python", (148, 163, 184)),
]

for blink in [True, False, True, False]:
    img, draw = draw_window_base()
    draw.text((24, 48), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 48), "~", font=font_bold, fill=(168, 85, 247))
    draw.text((60, 48), "whoami", font=font_mono, fill=(241, 245, 249))
    draw.text((24, 72), "Amish (BlackFeather)", font=font_name, fill=(34, 197, 94))
    
    y = 106
    for label, l_col, val, v_col in lines:
        draw.text((24, y), label, font=font_bold, fill=l_col)
        draw.text((105, y), val, font=font_mono, fill=v_col)
        y += 24
        
    draw.text((24, 184), "➜", font=font_bold, fill=(56, 189, 248))
    draw.text((42, 184), "~", font=font_bold, fill=(168, 85, 247))
    cursor = " █" if blink else ""
    draw.text((60, 184), "status --ready" + cursor, font=font_mono, fill=(34, 197, 94))
    save_frame(img, count=10)

print(f"Rendered {frame_idx} frames. Encoding GIF...")

out_gif = "/home/raven/Projects/BlackFeather-git/assets/header.gif"
cmd = (
    f"ffmpeg -y -framerate 12 -i {TMP_DIR}/frame_%04d.png "
    f"-vf 'fps=12,scale={WIDTH}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer' "
    f"{out_gif}"
)
subprocess.run(cmd, shell=True, check=True)
size = os.path.getsize(out_gif)
print(f"Generated {out_gif}: {size} bytes ({size / 1024:.1f} KB)")
