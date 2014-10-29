#!/usr/bin/env python3


import freetype
import numpy as np
from PIL import Image

face = freetype.Face('arial.ttf')
face.set_char_size(20 * 64)
slot = face.glyph


def save(array, encoding, sheet):
    for x in range(512):
        for y in range(512):
            array[x, y] = int((array[x, y] >> 6) / 3 * 255)

    image = Image.fromarray(array, mode='L')
    image.save('font_{}_{}.png'.format(encoding, sheet))


fonts = {
        'windows-1252': range(0x20, 0x100),
        #'sjis': range(0x8140, 0x9873),
        }
for encoding, char_nums in fonts.items():
    charset = bytes(char_nums).decode(encoding, errors='replace').replace('\ufffd', ' ').replace('\x7f', ' ')

    sheet = 0
    x = x0 = 1
    y = y0 = -4
    dx = dy = 24
    cols = rows = 21
    Z = np.zeros((512, 512), dtype=np.ubyte)

    for i, c in enumerate(charset):
        face.load_char(c)
        bitmap = slot.bitmap
        h, w = bitmap.rows, bitmap.width
        top, left = slot.bitmap_top, slot.bitmap_left
        arr = np.array(bitmap.buffer).reshape(h, w)
        Z[y + dy - top:y + dy - top + h, x + left:x + left + w] += arr
        x += dx
        if (i + 1) % cols == 0:
            x = x0
            y += dy
            if (i + 1) == cols * rows:
                save(Z, encoding, sheet)
                y = y0
                Z = np.zeros((512, 512), dtype=np.ubyte)
                sheet += 1
    save(Z, encoding, sheet)
