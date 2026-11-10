"""Convierte los PNG de una carpeta a JPG nítidos.

- Submuestreo 4:4:4 (sin pérdida de color en los bordes del texto).
- Perfil sRGB incrustado.
- Busca la mayor calidad (95 → 60) que cumpla el límite de peso, si se indica.

Uso:
  python to_jpg.py <carpeta> [--limite-kb 150] [--solo-1x]

  --limite-kb  límite de peso para los archivos @1x (los @2x no se limitan)
  --solo-1x    aplica el límite solo a los @1x (por defecto) — se deja por claridad
"""
import argparse
import glob
import io
import os

from PIL import Image, ImageCms

ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()


def convert(png, limit_kb=None):
    im = Image.open(png).convert('RGB')
    cap = limit_kb * 1024 if (limit_kb and '@2x' not in png) else None
    for q in range(95, 59, -1):
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=q, subsampling=0, optimize=True, progressive=True, icc_profile=ICC)
        if cap is None or buf.tell() <= cap:
            break
    out = png[:-4] + '.jpg'
    with open(out, 'wb') as f:
        f.write(buf.getvalue())
    ok = cap is None or buf.tell() <= cap
    return out, q, buf.tell() // 1024, ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta')
    ap.add_argument('--limite-kb', type=int, default=None)
    a = ap.parse_args()
    for png in sorted(glob.glob(os.path.join(a.carpeta, '*.png'))):
        out, q, kb, ok = convert(png, a.limite_kb)
        flag = '' if ok else '  ⚠ supera el límite incluso a calidad 60'
        print(f'{os.path.basename(out)}  q{q}  {kb} KB{flag}')
