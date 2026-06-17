"""将所有素材图缩放到编辑尺寸（最长边700px），存到 images/light/ """
import os
from PIL import Image

SRC = 'images'
DST = 'images/light'
EDIT_SIZE = 700
os.makedirs(DST, exist_ok=True)

all_files = []
for root, dirs, files in os.walk(SRC):
    for f in files:
        if not f.endswith('.png'): continue
        if 'thumbnails' in root or 'light' in root: continue
        if f in ('logo.png','tag.png','脸部定位备份.png'): continue
        all_files.append(os.path.join(root, f))

total = 0
for path in all_files:
    rel = os.path.relpath(path, SRC)
    dst_dir = os.path.join(DST, os.path.dirname(rel))
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(DST, rel)
    if os.path.exists(dst_path): continue

    img = Image.open(path).convert('RGBA')
    fw, fh = img.size
    scale = EDIT_SIZE / max(fw, fh)
    new_w = max(1, round(fw * scale))
    new_h = max(1, round(fh * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    img.save(dst_path, 'PNG')
    total += 1

print(f'生成 {total} 张轻量图 -> {DST}/')
