"""生成所有组件变体缩略图（32px高，预着色，白色背景）
用法：python gen_thumbnails.py
输出：images/thumbnails/xxx.png
"""
import os
from PIL import Image

THUMB_H = 32
OUT_DIR = 'images/thumbnails'
os.makedirs(OUT_DIR, exist_ok=True)

# 默认色（从 index.html COLOR_GROUPS 提取）
DEFAULT_COLORS = {
    'skin': (255,213,184), 'hair': (74,44,26),
    'eye_pupil_left': (136,136,136), 'eye_pupil_right': (136,136,136),
    'eye_part_left': (51,51,51), 'eye_part_right': (51,51,51),
    'eyebrow': (74,55,40), 'mouth': (232,139,139),
    'blush': (232,120,120), 'eye_highlight': (153,153,153),
    'face_other': (51,51,51),
    'bloodline_skin': (0,0,0), 'bloodline_hair': (0,0,0),
    'bloodline_back': (0,0,0),
}

# 组件配置：id, color_group_key, half_side
COMPS = [
    ('eyebrow','eyebrow',None), ('mouth','mouth',None), ('blush','blush',None),
    ('eye_pupil_left','eye_pupil_left',None), ('eye_part_left','eye_part_left',None),
    ('eye_pupil_right','eye_pupil_right',None), ('eye_part_right','eye_part_right',None),
    ('eye_highlight_left','eye_highlight','left'), ('eye_highlight_right','eye_highlight','right'),
    ('skin_body','skin',None), ('clothing_bottom',None,None), ('clothing_top',None,None),
    ('hair_base','hair',None), ('ponytail','hair',None), ('hair_back','hair',None),
    ('wolftail','hair',None), ('chest_hair','hair',None),
    ('hair_front_base','hair',None), ('hair_front_strands','hair',None),
    ('bloodline_skin','bloodline_skin',None), ('bloodline_hair','bloodline_hair',None),
    ('bloodline_back','bloodline_back',None),
    ('skin_face','skin',None), ('hair_hairline','hair',None),
]

# 组件id → 文件名（从 images/ 扫描 *.png）
IMG_DIR = 'images'
all_pngs = [f for f in os.listdir(IMG_DIR) if f.endswith('.png')]

def find_files(comp_id):
    """根据组件id匹配变体文件列表"""
    # 特殊映射
    special = {
        'skin_body': ['skin_body_edit.png'],
        'skin_face': ['skin_face_edit.png'],
        'hair_base': ['hair_base_edit.png'],
        'hair_hairline': ['hair_hairline_edit.png'],
        'clothing_bottom': ['clothing_bottom_edit.png'],
        'clothing_top': ['clothing_top_edit.png'],
        'bloodline_skin': ['bloodline_skin.png'],
        'bloodline_hair': ['bloodline_hair.png'],
        'bloodline_back': ['hair_back_bloodline.png'],
        'ponytail': [],
        'wolftail': ['hair_special_wolftail_edit.png'],
        'chest_hair': ['hair_special_chest_edit.png'],
        'eyebrow': [], 'mouth': [], 'blush': [],
        'hair_back': [],
    }

    if comp_id in special and special[comp_id]:
        result = [f for f in special[comp_id] if f in all_pngs]
        if result:
            return result

    # 多数字变体（hair_back_edit* / face_*_edit* / hair_special_ponytail_edit*）
    prefixes = [comp_id]  # e.g. 'hair_back'
    # eye_* → face_eye_* mapping
    eye_map = {
        'eye_pupil_left': 'face_eye_left_pupil',
        'eye_part_left': 'face_eye_left_part',
        'eye_pupil_right': 'face_eye_right_pupil',
        'eye_part_right': 'face_eye_right_part',
        'eye_highlight_left': 'face_eye_highlight',
        'eye_highlight_right': 'face_eye_highlight',
    }
    if comp_id in eye_map:
        prefixes = [eye_map[comp_id]]
    elif comp_id.startswith('eye_') or comp_id in ('eyebrow','mouth','blush'):
        prefixes = ['face_' + comp_id]
    if comp_id == 'ponytail':
        prefixes = ['hair_special_ponytail']
    if comp_id == 'hair_back':
        prefixes = ['hair_back']

    result = []
    for f in sorted(all_pngs):
        if f in ('logo.png','tag.png','脸部定位备份.png'):
            continue
        for pfx in prefixes:
            name = f.replace('.png','')
            if name == pfx + '_edit':
                result.append(f)
                break
            if name.startswith(pfx + '_edit') and name[len(pfx + '_edit'):].isdigit():
                result.append(f)
                break
    return result

def gen_thumb(in_path, out_path, color_rgb, comp_id, half_side):
    img = Image.open(in_path).convert('RGBA')
    fw, fh = img.size

    # 缩放到400px用于alpha扫描
    analyze_scale = 400 / max(fw, fh)
    aw = max(1, round(fw * analyze_scale))
    ah = max(1, round(fh * analyze_scale))
    small = img.resize((aw, ah), Image.LANCZOS)

    # 找非透明bbox
    alpha = small.split()[-1]
    bbox = alpha.getbbox()
    if bbox is None:
        blank = Image.new('RGB', (4, THUMB_H), (255,255,255))
        blank.save(out_path)
        return
    cx, cy, cmx, cmy = bbox

    # halfSide 处理（高光左右拆分）
    if half_side == 'left':
        mid_x = (cx + cmx) // 2
        cmx = min(cmx, mid_x)
    elif half_side == 'right':
        mid_x = (cx + cmx) // 2
        cx = max(cx, mid_x)

    cw = cmx - cx + 1; ch = cmy - cy + 1
    pad_x = round(cw * 0.05); pad_y = round(ch * 0.05)
    cx = max(0, cx - pad_x); cy = max(0, cy - pad_y)
    cmx = min(aw - 1, cmx + pad_x); cmy = min(ah - 1, cmy + pad_y)

    # 映射回全分辨率
    crop_x = round(cx / analyze_scale); crop_y = round(cy / analyze_scale)
    crop_w = round((cmx - cx + 1) / analyze_scale); crop_h = round((cmy - cy + 1) / analyze_scale)

    # 裁剪原图
    cropped = img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

    # half_split（eyebrow/blush 图片左右两半，取左半）
    if comp_id in ('eyebrow', 'blush'):
        crop_w = round(crop_w / 2)
        cropped = img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

    # multiply着色
    if color_rgb:
        r_ch, g_ch, b_ch, a_ch = cropped.split()
        cr, cg, cb = color_rgb
        r_ch = r_ch.point(lambda x: min(255, x * cr // 255))
        g_ch = g_ch.point(lambda x: min(255, x * cg // 255))
        b_ch = b_ch.point(lambda x: min(255, x * cb // 255))
        cropped = Image.merge('RGBA', (r_ch, g_ch, b_ch, a_ch))

    # 缩放到32px高
    thumb_scale = THUMB_H / crop_h
    thumb_w = max(1, round(crop_w * thumb_scale))

    # 白色背景 + 内容
    thumb = Image.new('RGBA', (thumb_w, THUMB_H), (255, 255, 255, 255))
    resized = cropped.resize((thumb_w, THUMB_H), Image.LANCZOS)
    thumb.paste(resized, (0, 0), resized)

    thumb.save(out_path, 'PNG')

# 主循环
total = 0
for comp_id, color_key, half_side in COMPS:
    files = find_files(comp_id)
    if not files:
        print(f'  SKIP {comp_id}: no files')
        continue

    color_rgb = DEFAULT_COLORS.get(color_key) if color_key else None
    for f in files:
        in_path = os.path.join(IMG_DIR, f)
        out_path = os.path.join(OUT_DIR, f)
        if os.path.exists(out_path):
            continue
        try:
            gen_thumb(in_path, out_path, color_rgb, comp_id, half_side)
            total += 1
            print(f'  OK {f}')
        except Exception as e:
            print(f'  ERR {f}: {e}')

print(f'\n生成 {total} 张缩略图 → {OUT_DIR}/')
