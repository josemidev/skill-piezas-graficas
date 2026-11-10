---
name: piezas-graficas
description: Produce y adapta piezas gráficas publicitarias (banners de homepage, banners display, posts e historias de redes, fondos de carrusel) a partir de editables de agencia (PDF de Illustrator, PSD, presentaciones de Google Slides con key visuals) y entrega siempre una galería HTML de revisión para dar feedback. Úsala cada vez que el usuario pida crear, redimensionar, readaptar, corregir o reexportar banners, artes, piezas, key visuals o formatos de medios (970x250, 300x600, 320x50, 1080x1080, 1080x1920, 1920x1080, etc.), aunque no diga "skill" ni "galería": por ejemplo "hazme los banners de esta campaña", "pasa estos PSD a historia de Instagram", "corrige el precio en todas las piezas" o "el cliente pidió quitar el botón".
---

# Piezas gráficas publicitarias

Esta skill cubre el ciclo completo de una campaña de piezas: leer el material de la agencia, extraer los recursos reales (fotos, logos, tipografías, textos), componer cada formato, exportar y entregar todo en una **galería HTML de revisión** donde la persona ve todas las piezas juntas y responde con feedback. Las correcciones del cliente llegan en rondas, así que todo debe poder regenerarse rápido desde un origen editable.

## La regla central: siempre una galería HTML de revisión

Cada entrega, incluida cada ronda de correcciones, termina con un `index.html` que muestra todas las piezas exportadas, y se le envía a la persona (o se abre en Finder) junto con la carpeta `export/`. Así puede comparar formatos de un vistazo, detectar errores que en un archivo suelto no se ven y responder con capturas puntuales, que es como llega el feedback real ("aquí se superpone la letra", "en el 160x600 quita este beneficio").

La galería debe:
- agrupar por familia (Homepage / Display / Post / Historia…) y mostrar cada pieza a su tamaño real o escalada sin deformar;
- indicar debajo de cada pieza la medida, el nombre del archivo, el peso del JPG y enlaces al PNG y a la versión @2x;
- en formatos con zona segura (historias, fondos de carrusel), tener una casilla para superponer la zona segura y las áreas reservadas;
- funcionar con modo claro y oscuro, y abrirse con doble clic (rutas relativas a `export/`).

Usa `scripts/gallery.py`; regenera la galería cada vez que cambien las piezas.

## Flujo de trabajo

1. **Carpeta del proyecto.** Una carpeta por marca o campaña (`<marca>-<campaña>/`) con `src/` (origen editable, assets y scripts), `export/<familia>/` y `index.html`. No mezcles marcas: si llegan dos marcas a la vez, cada una va en su carpeta (y, si el usuario lo pide, en sesiones paralelas).
2. **Leer el material.** Ver `references/extraccion.md`:
   - Google Slides público: descarga `/export/pptx` y `/export/pdf`, renderiza las diapositivas para ver los key visuals y saca de los `.rels` los enlaces a editables ("EDITABLE", "DESCARGAR", "IMÁGENES").
   - PDF de Illustrator: fotos con su máscara (`smask`), logos como vectores (`get_drawings` → SVG), tipografías incrustadas y el texto legal real.
   - PSD: artboards y capas con `psd-tools`; cada elemento se compone por separado desde su capa.
3. **Inventario antes de componer.** Lista para la persona qué modelo, precio, beneficios, legal y logos lleva cada pieza, y de dónde salió cada dato. Si dos diapositivas se contradicen (dos precios para el mismo modelo), usa el editable más reciente y **señálalo**; no elijas en silencio.
4. **Componer.** Usa el origen que mejor se adapte:
   - **HTML + CSS** (`assets/banners-template.html`): un `div.ad[data-name]` por pieza, todo en posición absoluta, con las fuentes y los SVG extraídos. Es lo más rápido de corregir por rondas.
   - **Python (PIL) por capas** cuando el origen es un PSD y hay que reacomodar elementos ya rasterizados.
5. **Exportar.** `scripts/export_pieces.mjs` (Playwright) captura cada `.ad` a @1x y @2x en PNG; `scripts/to_jpg.py` genera los JPG con color completo y con el límite de peso por familia. Ver `references/formatos.md`.
6. **Revisar uno por uno antes de entregar.** Mira cada pieza exportada (y ampliada en las zonas críticas), siguiendo `references/checklist-revision.md`. Corrige e itera; no entregues lo que no viste.
7. **Entregar.** Galería + carpeta abierta en Finder + un resumen corto: qué se hizo, qué decisiones tomaste y qué quedó por confirmar.

## Principios de composición

- **Jerarquía explícita.** Pregunta o deduce el orden de prioridad y respétalo en todos los formatos. Un orden habitual en promociones: 1) la oferta (precio o porcentaje), 2) el logo del comercio o la marca, 3) lo demás al mismo nivel (logo de campaña, beneficios, producto).
- **Aprovechar el espacio.** Cada formato tiene su propia composición; no basta con escalar. Si el producto es ancho, dale el ancho completo y pon la información en una fila; si es alto, ponlo en columna junto al texto. Revisa que no queden huecos grandes ni elementos diminutos.
- **No regenerar el producto.** Usa la foto real del vehículo o producto, sin cambiar color, llantas ni diseño. Si falta escena para un formato nuevo, extiende cielo, mar o suelo de forma natural (ver `references/extraccion.md`, "Extender fondos").
- **Matrículas y textos dentro de la foto.** Si hay que cambiar el texto de una placa, redibújala en perspectiva sobre el contorno real, nunca con un rectángulo plano encima.
- **Contraste.** Texto blanco sobre fotografía: degradados suaves hasta alcanzar al menos 4.5:1 en todo el bloque de texto, y mídelo.
- **Interlineado.** Mide el interlineado en el editable y replícalo; las tipografías condensadas con interlineado muy cerrado hacen que las líneas se toquen.

## Rondas de correcciones

Las correcciones llegan como capturas o correos del cliente. Para cada una:
- aplica el cambio en el **origen** (no retoques el PNG) y reexporta todas las piezas afectadas;
- si el pedido dice "todas las piezas de X tamaño", busca ese tamaño en **todas las marcas** del proyecto y avisa cuáles tocaste y cuáles no aplicaban;
- vuelve a revisar visualmente las piezas tocadas (un cambio de texto suele romper un corte de línea en los formatos estrechos);
- actualiza la galería.

Errores que ya ocurrieron y conviene prevenir: nombre de modelo incompleto (el modelo sin su versión, cuando el key visual la incluye), precio de otra versión, botón donde el cliente no lo quiere (homepage sin botón, display con botón), beneficios del banco en formatos donde no van, palabras sueltas al final de un párrafo ("LLENO" solo, "90%" solo).

## Archivos de esta skill

- `references/extraccion.md`: cómo sacar fotos, vectores, tipografías y textos de PDF, PSD y Slides; extender fondos; placas.
- `references/formatos.md`: medidas habituales, zonas seguras, límites de peso y exportación nítida.
- `references/checklist-revision.md`: qué mirar en cada pieza antes de entregar.
- `scripts/export_pieces.mjs`: exporta cada `.ad` del HTML a PNG @1x/@2x.
- `scripts/to_jpg.py`: PNG → JPG sRGB 4:4:4 con límite de peso.
- `scripts/gallery.py`: genera la galería `index.html` de revisión.
- `scripts/pdf_assets.py`: extrae imágenes con máscara, fuentes y vectores (SVG) de un PDF de Illustrator.
- `scripts/psd_elements.py`: lista artboards y capas de un PSD y extrae cada grupo de capas como PNG con transparencia.
- `assets/banners-template.html`: plantilla de maquetación por piezas.
