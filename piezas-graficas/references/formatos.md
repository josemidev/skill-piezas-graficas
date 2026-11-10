# Formatos, zonas seguras y exportación

## Medidas habituales

| Familia | Medidas | Notas |
|---|---|---|
| Display (IAB) | 970x250, 970x90, 728x90, 300x600, 160x600, 300x250, 320x50, 550x480 | JPG @1x ≤ 150 KB (Google Ads). Suelen llevar botón (CTA). |
| Homepage web | 1920x720 desktop, 750x1000 móvil (confirmar con el sitio) | Por lo general sin botón: el sitio pone sus propios enlaces. |
| Carrusel home | 1920x1080 desktop, 750x1200 móvil | Reservar cabecera del sitio y flechas del carrusel. |
| Post redes | 1080x1080 (1:1), 1080x1350 (4:5) | |
| Historia / Reel | 1080x1920 (9:16) | Zona segura y 250–1580: Instagram tapa ~250 px arriba y ~340 px abajo. Solo fondo fuera de esa franja. |

Si la persona no da medidas de homepage, asume las de la tabla y dilo explícitamente para que las confirme.

## Formatos estrechos

- **Leaderboards (970x90, 728x90, 320x50):** todo en una sola fila: logo · producto · titular · oferta · CTA. El titular en una línea y el modelo debajo necesitan espacio medido: deja al menos 4–6 px entre la línea base del titular y la parte superior del texto siguiente.
- **Skyscrapers (160x600):** textos de 6–7 px son ilegibles; corta las líneas a mano para que no queden palabras sueltas y reduce los beneficios a los imprescindibles.

## Exportación nítida

- Exporta PNG con Playwright (`scripts/export_pieces.mjs`) a @1x y @2x.
- Genera los JPG desde el PNG con `scripts/to_jpg.py`: **submuestreo 4:4:4** (`subsampling=0`), perfil sRGB incrustado y la mayor calidad que entre en el límite de peso. Con 4:2:0 (el valor por defecto de los navegadores), los bordes de texto negro sobre rojo o blanco sobre color se ven borrosos.
- Si la persona dice que el texto se ve pixelado, compara el @1x y el @2x ampliados antes de cambiar nada. Casi siempre es el @1x visto en una pantalla retina: recomienda subir el @2x donde el sitio lo permita, agrandar el texto pequeño o hacer versiones HTML5.

## Nombres de archivo

`<marca>-<campaña>-<modelo o comercio>-<medida>[@2x].<ext>`, en minúsculas, con guiones y sin espacios. Usa el nombre del comercio o del modelo, no un índice interno ("psd1-07").
