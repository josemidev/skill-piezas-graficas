# Extraer recursos del material de la agencia

## Contenido
1. Google Slides con key visuals
2. PDF de Illustrator (fotos, vectores, tipografías, textos)
3. PSD (artboards y capas)
4. Tipografías incompletas
5. Extender fondos para formatos nuevos
6. Placas y textos dentro de la foto

## 1. Google Slides con key visuals

Si la presentación es pública, no hace falta conector:

```bash
curl -sL -o deck.pptx "https://docs.google.com/presentation/d/<ID>/export/pptx"
curl -sL -o deck.pdf  "https://docs.google.com/presentation/d/<ID>/export/pdf"
pdftoppm -r 60 -png deck.pdf s      # una imagen por diapositiva para ver los KV
unzip -oq deck.pptx -d x            # x/ppt/media = imágenes, x/ppt/slides/_rels = enlaces
grep -ho 'Target="http[^"]*"' x/ppt/slides/_rels/*.rels | sort -u
```

Los enlaces de Drive a editables se descargan con:

```bash
curl -L -o editable.pdf "https://drive.usercontent.google.com/download?id=<FILE_ID>&export=download&confirm=t"
```

Pueden pesar cientos de MB: córrelo en segundo plano. Si la presentación es privada, usa el conector de Google Drive si está disponible.

Arma una contact sheet de todas las diapositivas (PIL) para ver de un vistazo modelos, precios y beneficios. El texto también se puede leer con `pdftotext -layout`.

## 2. PDF de Illustrator

`scripts/pdf_assets.py editable.pdf <salida>` hace lo básico:
- **Fotos**: `pdfimages -list` muestra si una imagen tiene `smask`; si la tiene, es un recorte con transparencia → PNG RGBA uniendo `Pixmap(doc,xref)` y `Pixmap(doc,smask)`. Recorta al contenido (alpha > 20).
- **Posición**: `page.get_image_rects(xref)` da dónde estaba la foto en el póster; sirve para mapear coordenadas del póster a píxeles de la foto (placa, auto).
- **Vectores**: `page.get_drawings()` → filtra por caja (logo, emblema, logo de la feria) → SVG. Los rellenos blancos suelen ser logos sobre foto.
- **Textos**: `page.get_text('dict')` da fuente, tamaño, color y posición de cada línea, incluido el texto legal completo. Úsalo literal; no inventes condiciones.
- **Interlineado**: compara el `origin` (línea base) de dos líneas consecutivas del titular y divide por el tamaño de fuente. Ese es el `line-height` a replicar.

## 3. PSD

`scripts/psd_elements.py <archivo.psd> <salida>`:
- `psd-tools` (con `psd-tools[composite]` para formas vectoriales) lista los artboards y su árbol de capas.
- `psd.topil()` da la imagen combinada guardada en el PSD: úsala como referencia de cómo debe verse cada artboard.
- Agrupa las capas visibles por zona de la composición (fondo, logo de campaña, oferta, comercio, beneficio, producto) y compón cada grupo por separado con `psd.composite(viewport=bbox, layer_filter=...)`. Así cada elemento sale con transparencia y se puede reubicar.
- Comprueba un artboard completo contra la imagen combinada (diferencia media < 2 de 255) antes de confiar en la extracción.
- Si un elemento estaba cortado por el borde del artboard original (por ejemplo, un podio), en el formato nuevo debe seguir saliendo por ese borde.

## 4. Tipografías incompletas

Los PDF solo traen el subconjunto de glifos usados en el póster.
- Si la fuente es de Google Fonts (OFL), descarga la versión completa desde `github.com/google/fonts`.
- Si es comercial, lista los glifos con contorno real (`glyf[n].numberOfContours != 0`) y escribe solo con esos. Se pueden **injertar** glifos de otro subconjunto del mismo PDF (por ejemplo, una versión CFF del mismo peso) convirtiendo con `Cu2QuPen`. Como último recurso, un glifo se puede **sintetizar** engrosando el peso regular con `skia-pathops` (stroke + unión).
- Quita del `cmap` los glifos vacíos para que el navegador use la fuente de respaldo en vez de dibujar huecos, y renombra la familia para no chocar con fuentes instaladas.
- Avisa siempre qué glifos se injertaron o sintetizaron, y pide los archivos de la fuente completa si hay licencia.

## 5. Extender fondos para formatos nuevos

Cuando la foto es vertical y el formato es ancho (970x90, 728x90, 1920x1080):
1. Calcula un perfil de color por fila tomado de los bordes de la foto (mediana) para cielo y mar; suaviza en vertical salvo en la línea del horizonte.
2. Para el suelo, toma un parche limpio, sácale el grano con un filtro paso alto (original − blur) y aplícalo en mosaico con volteos aleatorios sobre el perfil.
3. Funde el original con una máscara de rampas amplias (30 % del ancho en el lado de la extensión). Las rampas cortas dejan una costura visible.
4. Guarda un "master" grande y coloca el auto por su caja en cada formato.

Para adaptar una pieza **aprobada** sin tocarla (más lienzo arriba o abajo): renderiza la misma escena y los mismos degradados en el lienzo grande y pega encima, píxel a píxel, el PNG aprobado. Verifica que la zona de la pieza sea idéntica y que el borde difiera menos de 1 nivel.

## 6. Placas y textos dentro de la foto

- Localiza las esquinas reales de la placa (píxeles claros y poco saturados dentro de una caja aproximada; extremos de x+y y x−y).
- Rellena con un plano de color ajustado a los píxeles de fondo de la placa, con un poco de ruido para igualar el grano.
- Dibuja el texto en un lienzo plano con las proporciones de la placa y deformalo con una transformación de perspectiva hacia las 4 esquinas, con supermuestreo.
- Revisa ampliado: no deben asomar bordes ni letras de la placa original.
