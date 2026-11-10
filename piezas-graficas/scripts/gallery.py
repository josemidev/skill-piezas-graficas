"""Genera la galería HTML de revisión (index.html) de un proyecto de piezas.

Estructura esperada:
  <proyecto>/export/<familia>/<nombre>.jpg  (+ .png y opcionalmente @2x)

Cada subcarpeta de export/ es una sección de la galería (Homepage, Display, 1080x1920…).
Las piezas con proporción 9:16 muestran, con una casilla, la zona segura de historias
(y 250–1580 sobre 1920). Se puede pasar otra zona con --zona-segura familia=top,bottom
en píxeles del alto original.

Uso:
  python gallery.py <proyecto> --titulo "Marca · Campaña" [--descripcion "..."]
         [--orden 970x250,970x90,728x90,...] [--zona-segura 1080x1920=250,340]
"""
import argparse
import html
import os

from PIL import Image

DEFAULT_SAFE = {'9:16': (250, 340)}  # px tapados arriba y abajo en 1080x1920


def ratio_key(w, h):
    return '9:16' if abs(w / h - 9 / 16) < 0.01 else None


def card(proj, folder, f, safe_cfg):
    n = f[:-4]
    path = f'export/{folder}/{f}'
    w, h = Image.open(os.path.join(proj, path)).size
    kb = os.path.getsize(os.path.join(proj, path)) // 1024
    links = []
    for ext, label in (('.png', 'PNG'), ('@2x.png', 'PNG @2x'), ('@2x.jpg', 'JPG @2x')):
        if os.path.exists(os.path.join(proj, f'export/{folder}/{n}{ext}')):
            links.append(f'<a href="export/{folder}/{n}{ext}">{label}</a>')
    safe = safe_cfg.get(folder) or DEFAULT_SAFE.get(ratio_key(w, h))
    overlay = ''
    if safe:
        top, bottom = safe
        overlay = (f'<div class="safe" style="top:{top / h * 100:.3f}%;bottom:{bottom / h * 100:.3f}%"></div>')
    return (f'<figure style="--w:{w}px"><div class="fr" style="aspect-ratio:{w}/{h}">'
            f'<img src="{path}" alt="{html.escape(n)}" loading="lazy">{overlay}</div>'
            f'<figcaption><b>{w}×{h}</b><span>{html.escape(n)}</span>'
            f'<span>JPG {kb} KB{" · " if links else ""}{" · ".join(links)}</span></figcaption></figure>')


def build(proj, title, desc, order, safe_cfg):
    exp = os.path.join(proj, 'export')
    sections = []
    has_safe = False
    for folder in sorted(d for d in os.listdir(exp) if os.path.isdir(os.path.join(exp, d))):
        files = [f for f in os.listdir(os.path.join(exp, folder)) if f.endswith('.jpg') and '@2x' not in f]
        if not files:
            continue
        files.sort(key=lambda f: (next((i for i, o in enumerate(order) if o in f), 99), f))
        cards = [card(proj, folder, f, safe_cfg) for f in files]
        has_safe = has_safe or any('class="safe"' in c for c in cards)
        sections.append(f'<h2>{html.escape(folder.replace("-", " ").title())}</h2><div class="grid">{"".join(cards)}</div>')
    toggle = ('<label><input type="checkbox" onchange="document.body.classList.toggle(\'showsafe\',this.checked)">'
              ' Mostrar zona segura</label>') if has_safe else ''
    page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>
:root{{--bg:#f2f2f0;--fg:#14181d;--mut:#6b7178;--card:#fff;--line:#e2e2df}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#111315;--fg:#ecedee;--mut:#9aa0a6;--card:#1b1e21;--line:#2a2e33}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif;padding:40px 16px}}
main{{max-width:1960px;margin:0 auto}} h1{{font-size:28px;margin:0 0 4px}}
h2{{font-size:18px;margin:44px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--line)}}
p{{color:var(--mut);margin:0;max-width:820px}} label{{display:inline-flex;gap:6px;margin-top:14px;cursor:pointer}}
.grid{{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px;width:min(var(--w),100%,640px)}}
.fr{{position:relative}} .fr img{{display:block;width:100%;height:100%}}
.safe{{position:absolute;left:0;right:0;outline:2px dashed #ff3cf0;outline-offset:-2px;display:none}}
body.showsafe .safe{{display:block}}
figcaption{{display:flex;flex-direction:column;font-size:12px;color:var(--mut);margin-top:8px}}
figcaption b{{color:var(--fg);font-size:13px}} a{{color:inherit}}
</style></head><body><main>
<h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p>{toggle}
{"".join(sections)}
</main></body></html>'''
    out = os.path.join(proj, 'index.html')
    with open(out, 'w') as f:
        f.write(page)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('proyecto')
    ap.add_argument('--titulo', required=True)
    ap.add_argument('--descripcion', default='')
    ap.add_argument('--orden', default='', help='medidas en el orden en que deben aparecer, separadas por coma')
    ap.add_argument('--zona-segura', action='append', default=[],
                    help='familia=top,bottom en px del alto original (ej. 1080x1920=250,340)')
    a = ap.parse_args()
    safe = {}
    for s in a.zona_segura:
        k, v = s.split('=')
        t, b = v.split(',')
        safe[k] = (int(t), int(b))
    print(build(a.proyecto, a.titulo, a.descripcion, [o for o in a.orden.split(',') if o], safe))
