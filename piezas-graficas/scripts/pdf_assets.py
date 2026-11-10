"""Extrae recursos de un PDF de Illustrator (editable de agencia).

Para cada página:
  - inventario.txt: textos con fuente, tamaño, color y posición; imágenes con su caja.
  - img-p<pág>-x<xref>.png: fotos; si traen máscara (smask) salen como PNG con transparencia,
    recortadas al contenido.
  - fuentes/: las fuentes incrustadas (subconjuntos) y la lista de glifos con contorno.
  - vector-p<pág>.svg: todos los rellenos vectoriales de la página (para recortar logos con --caja).

Uso:
  python pdf_assets.py editable.pdf salida/
  python pdf_assets.py editable.pdf salida/ --pagina 2 --caja 58,63,185,203 --nombre logo
      (exporta solo los vectores dentro de esa caja, en puntos del PDF, como salida/logo.svg)

Requiere: pip install pymupdf fonttools pillow
"""
import argparse
import io
import os

import pymupdf
from PIL import Image


def fmt(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def path_d(d, ox, oy):
    out, cur = [], None
    for it in d['items']:
        op = it[0]
        if op == 'l':
            a, b = it[1], it[2]
            if cur is None or abs(cur.x - a.x) > .01 or abs(cur.y - a.y) > .01:
                out.append(f'M{fmt(a.x - ox)} {fmt(a.y - oy)}')
            out.append(f'L{fmt(b.x - ox)} {fmt(b.y - oy)}'); cur = b
        elif op == 'c':
            a, b, c, e = it[1:5]
            if cur is None or abs(cur.x - a.x) > .01 or abs(cur.y - a.y) > .01:
                out.append(f'M{fmt(a.x - ox)} {fmt(a.y - oy)}')
            out.append(f'C{fmt(b.x - ox)} {fmt(b.y - oy)} {fmt(c.x - ox)} {fmt(c.y - oy)} {fmt(e.x - ox)} {fmt(e.y - oy)}'); cur = e
        elif op == 're':
            r = it[1]; out.append(f'M{fmt(r.x0 - ox)} {fmt(r.y0 - oy)}H{fmt(r.x1 - ox)}V{fmt(r.y1 - oy)}H{fmt(r.x0 - ox)}Z'); cur = None
        elif op == 'qu':
            q = it[1]
            out.append(f'M{fmt(q.ul.x - ox)} {fmt(q.ul.y - oy)}L{fmt(q.ur.x - ox)} {fmt(q.ur.y - oy)}'
                       f'L{fmt(q.lr.x - ox)} {fmt(q.lr.y - oy)}L{fmt(q.ll.x - ox)} {fmt(q.ll.y - oy)}Z'); cur = None
    if d.get('closePath'):
        out.append('Z')
    return ''.join(out)


def color(c):
    return '#%02x%02x%02x' % tuple(round(v * 255) for v in c[:3])


def svg(page, box):
    x0, y0, x1, y1 = box
    paths = []
    for d in page.get_drawings():
        r = d['rect']
        if d['type'] in ('f', 'fs') and d.get('fill') and r.x0 >= x0 - .5 and r.y0 >= y0 - .5 and r.x1 <= x1 + .5 and r.y1 <= y1 + .5:
            rule = ' fill-rule="evenodd"' if d.get('even_odd') else ''
            paths.append(f'<path fill="{color(d["fill"])}"{rule} d="{path_d(d, x0, y0)}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(x1 - x0)} {fmt(y1 - y0)}">'
            f'{"".join(paths)}</svg>'), len(paths)


def glyphs(buf, ext):
    try:
        if ext == 'cff':
            from fontTools.cffLib import CFFFontSet
            c = CFFFontSet(); c.decompile(io.BytesIO(buf), None)
            return ' '.join(sorted(c[0].CharStrings.keys()))
        from fontTools.ttLib import TTFont
        t = TTFont(io.BytesIO(buf)); cm = t.getBestCmap() or {}; g = t['glyf']
        return ''.join(sorted(chr(u) for u, n in cm.items() if n in g and g[n].numberOfContours != 0))
    except Exception as e:
        return f'(no se pudo leer: {e})'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('salida')
    ap.add_argument('--pagina', type=int); ap.add_argument('--caja'); ap.add_argument('--nombre', default='vector')
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    doc = pymupdf.open(a.pdf)

    if a.caja:
        page = doc[(a.pagina or 1) - 1]
        s, n = svg(page, [float(v) for v in a.caja.split(',')])
        open(os.path.join(a.salida, a.nombre + '.svg'), 'w').write(s)
        print(f'{a.nombre}.svg: {n} trazados')
        return

    inv = []
    for pi, page in enumerate(doc, 1):
        inv.append(f'=== Página {pi}  {page.rect}')
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines', []):
                for sp in line['spans']:
                    if sp['text'].strip():
                        inv.append(f'  texto {[round(v) for v in sp["bbox"]]} base_y={sp["origin"][1]:.1f} '
                                   f'{sp["font"]} {sp["size"]:.1f}pt #{sp["color"]:06x}  {sp["text"]!r}')
        seen = set()
        for img in page.get_images(full=True):
            xref, smask = img[0], img[1]
            if xref in seen:
                continue
            seen.add(xref)
            inv.append(f'  imagen xref={xref} {img[2]}x{img[3]} smask={smask} en {page.get_image_rects(xref)}')
            pix = pymupdf.Pixmap(doc, xref)
            if pix.colorspace and pix.colorspace.n != 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            if smask:
                pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, smask))
            im = Image.open(io.BytesIO(pix.tobytes('png')))
            if im.mode == 'RGBA':
                bb = im.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox()
                if bb:
                    im = im.crop(bb)
            im.save(os.path.join(a.salida, f'img-p{pi}-x{xref}.png'))
        s, n = svg(page, tuple(page.rect))
        open(os.path.join(a.salida, f'vector-p{pi}.svg'), 'w').write(s)

    fdir = os.path.join(a.salida, 'fuentes'); os.makedirs(fdir, exist_ok=True)
    done = set()
    for page in doc:
        for fo in page.get_fonts(full=True):
            if fo[0] in done:
                continue
            done.add(fo[0])
            name, ext, _, buf = doc.extract_font(fo[0])
            if not buf:
                continue
            fn = f'{fo[0]}-{name.split("+")[-1]}.{ext}'
            open(os.path.join(fdir, fn), 'wb').write(buf)
            inv.append(f'fuente {fn}: {glyphs(buf, ext)}')
    open(os.path.join(a.salida, 'inventario.txt'), 'w').write('\n'.join(inv))
    print(f'Listo: {a.salida}/inventario.txt')


if __name__ == '__main__':
    main()
