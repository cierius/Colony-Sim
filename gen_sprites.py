"""
Generates pixel-art sprite sheets for Colony-Sim.
  terrain.png  — 10 tiles × 1 row, each 32×32:
    0=grassland 1=forest 2=trees 3=mountain 4=river
    5=hills 6=shore 7=desert 8=ocean 9=dirt/path

  sprites.png  — 7 tiles × 1 row, each 32×32:
    0=farmer 1=hunter 2=woodcutter 3=builder 4=caretaker 5=mystic
    6=cabin 7=farm_field 8=storehouse 9=workshop 10=infirmary
    11=schoolhouse 12=granary 13=tavern 14=monument 15=scaffold
"""
from PIL import Image, ImageDraw
import base64, io, os

S = 32  # sprite size

def img(w_tiles, h_tiles=1):
    im = Image.new("RGBA", (w_tiles * S, h_tiles * S), (0,0,0,0))
    return im, ImageDraw.Draw(im)

def rect(d, x,y,w,h,c): d.rectangle([x,y,x+w-1,y+h-1], fill=c)
def px(d, x,y,c): d.point((x,y), fill=c)

# ─── TERRAIN SHEET (10 tiles) ────────────────────────────────────────────────
TW = 10
terrain, td = img(TW)

def tile_xy(col): return col * S

# helpers
def fill_tile(d, tx, color):
    x = tile_xy(tx)
    rect(d, x, 0, S, S, color)

def add_noise(d, tx, color, freq=4):
    """sprinkle slight variation pixels"""
    import random; random.seed(tx * 99)
    x0 = tile_xy(tx)
    r,g,b,a = color
    for _ in range(18):
        px_ = random.randint(x0, x0+S-1)
        py_ = random.randint(0, S-1)
        v = random.randint(-18, 18)
        d.point((px_, py_), fill=(
            max(0,min(255,r+v)), max(0,min(255,g+v)), max(0,min(255,b+v)), a))

# 0 — GRASSLAND
fill_tile(td, 0, (86, 152, 70, 255))
add_noise(td, 0, (86, 152, 70, 255))
# grass tufts
for gx,gy in [(4,6),(10,14),(18,5),(24,20),(8,26),(28,10),(16,28),(2,22)]:
    x0=tile_xy(0)+gx
    rect(td,x0,gy,2,4,(62,120,48,255))
    td.point((x0+1,gy-1),(62,120,48,255))

# 1 — FOREST (pine trees, dark)
fill_tile(td, 1, (42, 90, 40, 255))
add_noise(td, 1, (42, 90, 40, 255))
def pine(d, x0, tx_off, ty_off, scale=1):
    bx = tile_xy(tx_off) + x0
    # trunk
    rect(d, bx+2*scale, ty_off+7*scale, 2*scale, 3*scale, (101,67,33,255))
    # layers
    for i,(w,y) in enumerate([(4,4),(6,2),(8,0)]):
        w_=w*scale; y_=y*scale
        rect(d, bx+(8-w)//2*scale, ty_off+y_, w_,3*scale, (34+i*8,100+i*5,34,255))
pine(td, 4, 1, 2, scale=1)
pine(td, 18, 1, 4, scale=1)

# 2 — TREES (deciduous, lighter)
fill_tile(td, 2, (60, 130, 50, 255))
add_noise(td, 2, (60, 130, 50, 255))
def tree(d, x0, tx_off, ty_off):
    bx = tile_xy(tx_off) + x0
    rect(d, bx+3, ty_off+9, 2, 5, (101,67,33,255))  # trunk
    # canopy — blob
    for dy in range(8):
        for dx in range(8):
            if (dx-3.5)**2+(dy-3)**2 < 14:
                c = (50+dy*5, 140+dx*3, 40+dy*4, 255)
                d.point((bx+dx,ty_off+dy+2), c)
tree(td, 4, 2, 2)
tree(td, 19, 2, 6)

# 3 — MOUNTAIN
fill_tile(td, 3, (100, 85, 70, 255))
add_noise(td, 3, (100, 85, 70, 255))
x0m = tile_xy(3)
# base ground
rect(td, x0m, 20, S, 12, (120, 100, 70, 255))
# mountain body
pts = [(x0m+16,1),(x0m+4,20),(x0m+28,20)]
td.polygon(pts, fill=(130,115,100,255))
# snow cap
pts2 = [(x0m+16,1),(x0m+11,9),(x0m+21,9)]
td.polygon(pts2, fill=(230,235,240,255))
td.line([(x0m+14,6),(x0m+18,6)], fill=(200,210,220,255), width=1)

# 4 — RIVER
fill_tile(td, 4, (65, 110, 175, 255))
add_noise(td, 4, (65, 110, 175, 255))
x0r = tile_xy(4)
# banks
rect(td, x0r, 0, S, 6, (90,150,70,255))
rect(td, x0r, 26, S, 6, (90,150,70,255))
# water ripples
for ry in range(6, 26, 4):
    for rx in range(0, 32, 6):
        td.arc([x0r+rx, ry, x0r+rx+5, ry+3], 180, 360, fill=(100,155,210,255), width=1)

# 5 — HILLS
fill_tile(td, 5, (80, 145, 65, 255))
add_noise(td, 5, (80, 145, 65, 255))
x0h = tile_xy(5)
# rolling hill shapes
for hx, ht in [(2,12),(10,8),(20,14),(24,6)]:
    pts_h = []
    for i in range(14):
        import math
        hpx = x0h + hx + i
        hpy = 18 - int(ht * math.sin(math.pi * i / 13))
        pts_h.append((hpx, hpy))
    pts_h += [(x0h+hx+13, 32),(x0h+hx, 32)]
    if len(pts_h) >= 3: td.polygon(pts_h, fill=(65,125,50,255))

# 6 — SHORE
fill_tile(td, 6, (70,140,200,255))
x0sh = tile_xy(6)
# sand
for sy in range(16, S):
    alpha = min(255, int((sy-16)*15))
    sand_c = (210, 190, 140, 255)
    rect(td, x0sh, sy, S, 1, sand_c)
# water top half
for sy in range(0, 16):
    rect(td, x0sh, sy, S, 1, (55+sy*2, 120+sy, 190, 255))
# wave line
for wx in range(0, 32, 5):
    td.arc([x0sh+wx, 13, x0sh+wx+4, 17], 180, 360, fill=(150,210,240,255), width=1)

# 7 — DESERT
fill_tile(td, 7, (210, 180, 110, 255))
add_noise(td, 7, (210, 180, 110, 255))
x0d = tile_xy(7)
# sand ripples
for dry in range(4, 32, 6):
    td.line([(x0d+2, dry),(x0d+28, dry+2)], fill=(195,165,95,255), width=1)
# cactus
cx = x0d + 20; cy = 8
rect(td, cx+2, cy+5, 2, 14, (50,120,50,255))   # stem
rect(td, cx, cy+8, 6, 2, (50,120,50,255))        # arm base
rect(td, cx, cy+5, 2, 4, (50,120,50,255))        # arm up
# small rock
rect(td, x0d+5, 22, 4, 3, (160,145,120,255))

# 8 — OCEAN
fill_tile(td, 8, (35, 90, 165, 255))
add_noise(td, 8, (35, 90, 165, 255))
x0o = tile_xy(8)
for oy in range(0, S, 5):
    for ox in range(0, S, 7):
        td.arc([x0o+ox, oy, x0o+ox+6, oy+3], 180,360, fill=(60,120,190,255), width=1)
# white foam line
for ox in range(0, 32, 8):
    rect(td, x0o+ox, 10, 5, 1, (180,215,240,255))
    rect(td, x0o+ox+3, 20, 6, 1, (160,205,235,255))

# 9 — DIRT / PATH
fill_tile(td, 9, (155, 120, 80, 255))
add_noise(td, 9, (155, 120, 80, 255))
x0dp = tile_xy(9)
for dy in range(3, 32, 5):
    td.line([(x0dp+2, dy),(x0dp+28, dy+1)], fill=(130,100,65,255), width=1)

# ─── SPRITES SHEET (16 tiles) ─────────────────────────────────────────────────
SW = 16
sprites, sd = img(SW)

def stile(col): return col * S

# skin tones
SKIN = (220, 170, 120, 255)
SKIN_D = (190, 140, 95, 255)
HAIR_BR = (80, 50, 25, 255)
HAIR_BL = (30, 20, 15, 255)
WHITE = (240, 240, 230, 255)

def draw_person(d, col, body_color, hair_color, accessory=None):
    x = stile(col)
    # shadow
    rect(d, x+8, 27, 16, 4, (0,0,0,40))
    # legs
    rect(d, x+10, 21, 4, 7, body_color)
    rect(d, x+18, 21, 4, 7, body_color)
    # body
    rect(d, x+8, 13, 16, 10, body_color)
    # arms
    rect(d, x+4, 14, 5, 8, body_color)
    rect(d, x+23, 14, 5, 8, body_color)
    # head
    rect(d, x+10, 5, 12, 10, SKIN)
    # hair
    rect(d, x+10, 5, 12, 4, hair_color)
    # eyes
    d.point((x+13, 9), HAIR_BL)
    d.point((x+18, 9), HAIR_BL)
    if accessory: accessory(d, x)

def farmer_hat(d, x):
    rect(d, x+8, 2, 16, 2, (160,120,50,255))   # brim
    rect(d, x+11, 0, 10, 4, (140,100,40,255))   # crown
    # hoe
    rect(d, x+25, 10, 2, 18, (120,80,40,255))
    rect(d, x+22, 9, 7, 2, (160,120,50,255))

def hunter_acc(d, x):
    # spear
    rect(d, x+3, 5, 2, 20, (120,80,40,255))
    rect(d, x+2, 4, 4, 4, (180,180,180,255))
    # bag
    rect(d, x+21, 16, 5, 5, (150,110,60,255))

def woodcutter_acc(d, x):
    # axe
    rect(d, x+24, 12, 2, 14, (120,80,40,255))
    rect(d, x+21, 10, 5, 6, (160,155,150,255))
    # belt
    rect(d, x+8, 19, 16, 2, (80,55,30,255))

def builder_acc(d, x):
    # hammer
    rect(d, x+24, 14, 2, 12, (120,80,40,255))
    rect(d, x+21, 12, 7, 4, (100,100,105,255))
    # apron
    rect(d, x+10, 15, 12, 8, (160,130,90,255))

def caretaker_acc(d, x):
    # satchel
    rect(d, x+21, 16, 6, 6, (80,140,100,255))
    rect(d, x+21, 14, 6, 2, (60,110,80,255))
    # green cross on body
    rect(d, x+15, 14, 2, 6, (60,190,100,255))
    rect(d, x+13, 16, 6, 2, (60,190,100,255))

def mystic_acc(d, x):
    # robe overlay (purple)
    rect(d, x+6, 12, 20, 12, (120,60,180,255))
    rect(d, x+8, 13, 16, 16, (120,60,180,255))
    # hood
    rect(d, x+9, 4, 14, 6, (100,50,160,255))
    # orb
    rect(d, x+25, 13, 5, 5, (150,200,255,255))
    rect(d, x+26, 14, 3, 3, (200,230,255,255))

# 0 — FARMER
draw_person(sd, 0, (160,120,60,255), HAIR_BR, farmer_hat)

# 1 — HUNTER
draw_person(sd, 1, (100,75,45,255), HAIR_BR, hunter_acc)

# 2 — WOODCUTTER
draw_person(sd, 2, (110,80,50,255), HAIR_BL, woodcutter_acc)

# 3 — BUILDER
draw_person(sd, 3, (130,95,55,255), (90,60,25,255), builder_acc)

# 4 — CARETAKER
draw_person(sd, 4, (80,140,90,255), (180,140,80,255), caretaker_acc)

# 5 — MYSTIC
draw_person(sd, 5, (120,60,180,255), HAIR_BL, mystic_acc)

# 6 — CABIN
def draw_cabin(d, col):
    x = stile(col)
    # ground shadow
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    # walls
    rect(d, x+4, 12, 24, 16, (120,80,45,255))
    # door
    rect(d, x+13, 20, 6, 8, (80,50,25,255))
    rect(d, x+15, 22, 2, 2, (180,140,70,255))  # knob
    # window
    rect(d, x+6, 15, 6, 5, (140,200,230,255))
    rect(d, x+9, 14, 1, 7, (80,60,30,255))
    rect(d, x+6, 17, 6, 1, (80,60,30,255))
    rect(d, x+20, 15, 6, 5, (140,200,230,255))
    rect(d, x+23, 14, 1, 7, (80,60,30,255))
    rect(d, x+20, 17, 6, 1, (80,60,30,255))
    # roof
    pts = [(x+2,12),(x+16,2),(x+30,12)]
    d.polygon(pts, fill=(160,110,50,255))
    pts2 = [(x+2,12),(x+16,4),(x+30,12),(x+28,14),(x+16,6),(x+4,14)]
    d.polygon(pts2, fill=(140,95,40,255))
    # chimney
    rect(d, x+21, 4, 4, 6, (110,90,75,255))
    # smoke
    for si, (sx,sy) in enumerate([(22,1),(24,0),(23,-1)]):
        d.ellipse([x+sx,sy+2,x+sx+3,sy+5], fill=(200,200,200,120))
draw_cabin(sd, 6)

# 7 — FARM FIELD
def draw_farm(d, col):
    x = stile(col)
    rect(d, x, 0, S, S, (100,70,35,255))  # soil
    # soil rows
    for fy in range(2, S, 5):
        rect(d, x, fy, S, 2, (85,58,28,255))
    # crops
    for fx in range(3, S, 5):
        for fy in range(0, S, 5):
            stem_h = 8
            rect(d, x+fx+1, fy, 2, stem_h, (80,140,50,255))
            # leaf
            rect(d, x+fx-1, fy+2, 3, 2, (70,160,50,255))
            rect(d, x+fx+2, fy+4, 3, 2, (70,160,50,255))
            # flower/grain
            d.point((x+fx+1, fy-1), (230,200,50,255))
            d.point((x+fx+2, fy-1), (230,200,50,255))
draw_farm(sd, 7)

# 8 — STOREHOUSE
def draw_storehouse(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    rect(d, x+3, 14, 26, 14, (140,105,60,255))
    # big door
    rect(d, x+10, 16, 12, 12, (90,60,30,255))
    rect(d, x+10, 16, 12, 2, (70,45,20,255))
    # roof (flat with slight overhang)
    rect(d, x+1, 11, 30, 4, (115,85,45,255))
    rect(d, x+1, 10, 30, 2, (95,70,35,255))
    # sign
    rect(d, x+7, 5, 18, 6, (160,130,80,255))
draw_storehouse(sd, 8)

# 9 — WORKSHOP
def draw_workshop(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    rect(d, x+3, 13, 26, 15, (100,80,55,255))
    rect(d, x+12, 20, 8, 8, (70,50,28,255))  # door
    # window with glow
    rect(d, x+4, 16, 7, 6, (255,200,80,180))
    rect(d, x+21, 16, 7, 6, (255,200,80,180))
    # roof
    pts = [(x+1,13),(x+16,4),(x+31,13)]
    d.polygon(pts, fill=(80,65,45,255))
    # anvil
    rect(d, x+5, 24, 6, 3, (100,100,110,255))
    rect(d, x+4, 26, 8, 1, (120,120,130,255))
draw_workshop(sd, 9)

# 10 — INFIRMARY
def draw_infirmary(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    rect(d, x+3, 13, 26, 15, (220,215,205,255))
    rect(d, x+12, 20, 8, 8, (180,160,140,255))
    rect(d, x+14, 15, 4, 10, (180,180,180,255))  # window tall
    # red cross on wall
    rect(d, x+6, 16, 4, 8, (200,40,40,255))
    rect(d, x+4, 20, 8, 4, (200,40,40,255))
    # roof
    pts = [(x+1,13),(x+16,4),(x+31,13)]
    d.polygon(pts, fill=(180,50,50,255))
draw_infirmary(sd, 10)

# 11 — SCHOOLHOUSE
def draw_school(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    rect(d, x+3, 13, 26, 15, (200,185,140,255))
    rect(d, x+12, 20, 8, 8, (120,90,55,255))
    rect(d, x+5, 15, 7, 6, (140,200,230,255))
    rect(d, x+20, 15, 7, 6, (140,200,230,255))
    pts = [(x+1,13),(x+16,4),(x+31,13)]
    d.polygon(pts, fill=(160,130,70,255))
    # bell tower
    rect(d, x+14, 0, 4, 5, (180,150,80,255))
    rect(d, x+13, 4, 6, 2, (150,120,60,255))
draw_school(sd, 11)

# 12 — GRANARY
def draw_granary(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    # round silo shape
    rect(d, x+5, 10, 22, 18, (190,155,90,255))
    # curved top
    d.ellipse([x+5, 4, x+27, 16], fill=(200,165,100,255))
    rect(d, x+13, 22, 6, 6, (130,100,55,255))  # door
    # bands
    for by in [12,17,22]:
        rect(d, x+5, by, 22, 1, (155,120,65,255))
draw_granary(sd, 12)

# 13 — TAVERN
def draw_tavern(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    rect(d, x+3, 12, 26, 16, (110,75,45,255))
    rect(d, x+12, 20, 8, 8, (80,50,25,255))
    rect(d, x+5, 15, 8, 6, (255,200,100,160))
    rect(d, x+19, 15, 8, 6, (255,200,100,160))
    # sign hanging
    rect(d, x+10, 4, 12, 6, (140,100,50,255))
    rect(d, x+10, 3, 1, 3, (100,70,30,255))
    rect(d, x+21, 3, 1, 3, (100,70,30,255))
    # roof
    pts = [(x+1,12),(x+16,2),(x+31,12)]
    d.polygon(pts, fill=(90,60,35,255))
draw_tavern(sd, 13)

# 14 — MONUMENT
def draw_monument(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    # base steps
    rect(d, x+4, 24, 24, 4, (160,155,145,255))
    rect(d, x+6, 20, 20, 4, (175,170,160,255))
    rect(d, x+8, 16, 16, 4, (185,180,170,255))
    # obelisk
    pts = [(x+14,2),(x+18,2),(x+20,16),(x+12,16)]
    d.polygon(pts, fill=(200,195,185,255))
    # tip gold
    pts2 = [(x+16,0),(x+14,4),(x+18,4)]
    d.polygon(pts2, fill=(210,175,50,255))
    # engravings
    rect(d, x+14, 8, 4, 1, (170,165,155,255))
    rect(d, x+14, 11, 4, 1, (170,165,155,255))
draw_monument(sd, 14)

# 15 — SCAFFOLD (construction)
def draw_scaffold(d, col):
    x = stile(col)
    rect(d, x+2, 26, 28, 5, (0,0,0,40))
    # poles
    rect(d, x+4, 6, 3, 22, (140,110,70,255))
    rect(d, x+25, 6, 3, 22, (140,110,70,255))
    # crossbeams
    for by in [6, 14, 21]:
        rect(d, x+4, by, 24, 2, (160,125,80,255))
    # diagonal braces
    td2 = d
    td2.line([(x+7,8),(x+25,20)], fill=(120,90,55,255), width=1)
    td2.line([(x+25,8),(x+7,20)], fill=(120,90,55,255), width=1)
    # partial wall behind
    rect(d, x+8, 10, 16, 14, (150,130,105,100))
draw_scaffold(sd, 15)

# ─── SAVE & ENCODE ────────────────────────────────────────────────────────────
OUT = "/home/user/Colony-Sim"

def to_b64(im):
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

terrain.save(f"{OUT}/terrain.png")
sprites.save(f"{OUT}/sprites.png")

tb64 = to_b64(terrain)
sb64 = to_b64(sprites)

# Write a JS snippet that can be pasted / imported
with open(f"{OUT}/sprite_data.js", "w") as f:
    f.write(f"const TERRAIN_B64='data:image/png;base64,{tb64}';\n")
    f.write(f"const SPRITES_B64='data:image/png;base64,{sb64}';\n")

print(f"terrain.png  {terrain.width}x{terrain.height}")
print(f"sprites.png  {sprites.width}x{sprites.height}")
print(f"sprite_data.js written ({os.path.getsize(OUT+'/sprite_data.js')//1024} KB)")
