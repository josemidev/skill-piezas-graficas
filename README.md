# Skill: piezas gráficas publicitarias

Una skill para Claude que produce y adapta piezas gráficas de campañas: banners de homepage, banners display (970x250, 300x600, 320x50…), posts e historias de redes y fondos de carrusel, a partir de los editables de la agencia (PDF de Illustrator, PSD o presentaciones de Google Slides con key visuals).

**Su regla central:** cada entrega, incluida cada ronda de correcciones, termina con una **galería HTML de revisión** (`index.html`) que muestra todas las piezas juntas, con medida, peso y enlaces a PNG y @2x. Así se puede revisar todo de un vistazo y responder con feedback puntual.

## Qué hace

- Lee el material de la agencia: descarga la presentación, ubica los editables y extrae fotos con transparencia, logos en vector, tipografías y el texto legal real.
- Compone cada formato con su propia composición: jerarquía explícita, aprovechamiento del espacio y zonas seguras de historias.
- Extiende fondos fotográficos para formatos anchos y corrige textos dentro de la foto (placas) en perspectiva.
- Exporta PNG @1x/@2x y JPG nítidos (color 4:4:4) dentro de los límites de peso de display.
- Revisa cada pieza con una checklist antes de entregar y aplica las rondas de correcciones desde el origen editable.

## Estructura

```
piezas-graficas/
├── SKILL.md                      # flujo de trabajo y principios
├── references/
│   ├── extraccion.md             # PDF, PSD, Slides, tipografías, fondos, placas
│   ├── formatos.md               # medidas, zonas seguras, exportación nítida
│   └── checklist-revision.md     # qué revisar antes de entregar
├── scripts/
│   ├── export_pieces.mjs         # HTML → PNG por pieza (Playwright)
│   ├── to_jpg.py                 # PNG → JPG 4:4:4 con límite de peso
│   ├── gallery.py                # galería index.html de revisión
│   ├── pdf_assets.py             # extrae imágenes, fuentes y vectores de un PDF
│   └── psd_elements.py           # artboards y capas de un PSD por elementos
└── assets/
    └── banners-template.html     # plantilla de maquetación por piezas
```

## Instalación

**Claude Code:** copia la carpeta `piezas-graficas/` a `~/.claude/skills/` (para todos tus proyectos) o a `.claude/skills/` dentro de un proyecto.

```bash
git clone https://github.com/josemidev/skill-piezas-graficas.git
cp -R skill-piezas-graficas/piezas-graficas ~/.claude/skills/
```

**Claude.ai:** comprime la carpeta `piezas-graficas/` en un `.zip` y súbela en Configuración → Capacidades → Skills.

## Dependencias de los scripts

```bash
pip install pymupdf fonttools pillow numpy "psd-tools[composite]" skia-pathops
npm i playwright && npx playwright install chromium
```

Además se usan `pdftoppm`, `pdfimages` y `pdftotext` de poppler (`brew install poppler` en macOS).

## Uso

Basta con pedirlo en lenguaje natural, por ejemplo:

- "Necesitamos los banners de homepage y el set display de esta campaña; los editables están en este link."
- "Readapta estos PSD a post 1080x1080 e historia de Instagram con zona segura."
- "El cliente pidió quitar el botón en homepage y cambiar el precio a US$30,900."
