"""Inventario y extracción por elementos de un PSD con varios artboards.

1) Listar artboards y capas:
     python psd_elements.py archivo.psd salida/ --listar
2) Exportar cada artboard tal como está guardado en el PSD (referencia visual + hoja de contacto):
     python psd_elements.py archivo.psd salida/ --originales
3) Extraer elementos agrupando capas visibles por zona, con transparencia:
     python psd_elements.py archivo.psd salida/ --zonas zonas.json

   zonas.json define, en coordenadas del artboard, a qué grupo va cada capa según su centro.
   Las capas que ocupan más del 50 % del artboard van a "fondo". Ejemplo:
     {"producto": [1290, 0, 99999, 99999],
      "logo":     [0, 0, 740, 500],
      "oferta":   [740, 0, 1290, 500],
      "comercio": [0, 500, 1290, 800],
      "beneficio":[0, 800, 1290, 99999]}

   Salida: <artboard>-<grupo>.png y meta.json con la caja de cada grupo relativa al artboard.
   El fondo sale con un margen extra (--margen) para poder recortarlo a formatos nuevos.

Requiere: pip install "psd-tools[composite]" pillow
"""
import argparse
import json
import os

from PIL import Image
from psd_tools import PSDImage


def leaves(group):
    for layer in group:
        if layer.is_group():
            yield from leaves(layer)
        else:
            yield layer


def artboards(psd):
    abs_ = [l for l in psd if l.kind == 'artboard']
    return abs_ or [psd]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('psd'); ap.add_argument('salida')
    ap.add_argument('--listar', action='store_true')
    ap.add_argument('--originales', action='store_true')
    ap.add_argument('--zonas')
    ap.add_argument('--margen', type=int, default=200)
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    psd = PSDImage.open(a.psd)
    base = os.path.splitext(os.path.basename(a.psd))[0].replace(' ', '-').lower()
    abs_ = artboards(psd)

    if a.listar:
        def walk(ls, ind=0):
            for l in ls:
                print('  ' * ind + f'- [{l.kind}] {l.name!r} visible={l.visible} bbox={l.bbox}')
                if l.is_group():
                    walk(l, ind + 1)
        print(f'{a.psd}: {psd.width}x{psd.height}, {len(abs_)} artboard(s)')
        walk(psd)
        return

    if a.originales:
        full = psd.topil()
        thumbs = []
        for i, ab in enumerate(abs_, 1):
            im = full.crop(ab.bbox).convert('RGB') if ab is not psd else full.convert('RGB')
            im.save(os.path.join(a.salida, f'{base}-{i:02d}.png'))
            t = im.copy(); t.thumbnail((480, 480)); thumbs.append(t)
        cols = 4; tw = max(t.width for t in thumbs); th = max(t.height for t in thumbs)
        sheet = Image.new('RGB', (cols * (tw + 10), ((len(thumbs) + cols - 1) // cols) * (th + 10)), 'white')
        for k, t in enumerate(thumbs):
            sheet.paste(t, ((k % cols) * (tw + 10), (k // cols) * (th + 10)))
        sheet.save(os.path.join(a.salida, f'{base}-contacto.png'))
        print(f'{len(abs_)} artboards exportados + {base}-contacto.png')
        return

    if a.zonas:
        zones = json.load(open(a.zonas))
        meta_path = os.path.join(a.salida, 'meta.json')
        meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
        for i, ab in enumerate(abs_, 1):
            name = f'{base}-{i:02d}'
            ox, oy, ox1, oy1 = ab.bbox
            aw, ah = ox1 - ox, oy1 - oy
            groups = {}
            for l in leaves(ab):
                if not l.is_visible():
                    continue
                x0, y0, x1, y1 = l.bbox
                if (x1 - x0) * (y1 - y0) > 0.5 * aw * ah or l.kind == 'solidcolorfill':
                    g = 'fondo'
                else:
                    cx, cy = (x0 + x1) / 2 - ox, (y0 + y1) / 2 - oy
                    g = next((k for k, (zx0, zy0, zx1, zy1) in zones.items() if zx0 <= cx < zx1 and zy0 <= cy < zy1), 'otros')
                groups.setdefault(g, []).append(l)
            meta[name] = {}
            for g, ls in groups.items():
                ids = {id(l) for l in ls}
                if g == 'fondo':
                    bb = (ox - a.margen, oy - a.margen, ox1 + a.margen, oy1 + a.margen)
                else:
                    bb = (min(l.bbox[0] for l in ls), min(l.bbox[1] for l in ls),
                          max(l.bbox[2] for l in ls), max(l.bbox[3] for l in ls))
                im = psd.composite(viewport=bb, force=True,
                                   layer_filter=lambda l: l.is_visible() and (l.is_group() or id(l) in ids))
                if im is None:
                    continue
                im = im.convert('RGBA')
                if g != 'fondo':
                    c = im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
                    if c:
                        im = im.crop(c); bb = (bb[0] + c[0], bb[1] + c[1], bb[0] + c[2], bb[1] + c[3])
                im.save(os.path.join(a.salida, f'{name}-{g}.png'))
                meta[name][g] = [bb[0] - ox, bb[1] - oy, bb[2] - ox, bb[3] - oy]
            print(name, {k: [layer.name for layer in v] for k, v in groups.items()}, flush=True)
        json.dump(meta, open(meta_path, 'w'), indent=1)


if __name__ == '__main__':
    main()
