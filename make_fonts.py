#!/usr/bin/env python3


import freetype
import numpy as np
from PIL import Image


class BaseFont:
    def save(self, array, sheet):
        # quantize
        # FIXME: use actual palette
        for x in range(512):
            for y in range(512):
                array[x, y] = int((array[x, y] >> 6) / 3 * 255)

        image = Image.fromarray(array, mode='L')
        file_name = 'font_{}_{}.png'.format(self.name, sheet)
        image.save(file_name)
        print('Saved sheet {} to {}.'.format(sheet, file_name))

    def run(self):
        face = freetype.Face(self.font)
        face.set_char_size(20 * 64)
        slot = face.glyph
        sheet = 0
        x = x0 = 1
        y = y0 = -4
        dx = dy = 24
        cols = rows = 21
        Z = np.zeros((512, 512), dtype=np.ubyte)

        for i, c in enumerate(self.charset):
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
                    self.save(Z, sheet)
                    y = y0
                    Z = np.zeros((512, 512), dtype=np.ubyte)
                    sheet += 1
        self.save(Z, sheet)


class ANSIFont(BaseFont):
    name = 'ansi'
    font = '/usr/share/fonts/TTF/arial.ttf'
    palette = [0, 0x99, 0xEE, 0xFF]

    @property
    def charset(self):
        yield from bytes(range(0x20, 0x100)).decode('windows-1252', errors='replace').replace('\ufffd', ' ').replace('\x7f', ' ')


class ShiftJISFont(BaseFont):
    name = 'sjis'
    # FIXME: find better font
    # distinctive: g, 山
    # Hiragino Maru Gothic?
    # TODO: render most characters in monochrome
    font = '/usr/share/fonts/OTF/ipagp.ttf'
    palette = [0x00, 0xDD, 0xEE, 0xFF]

    @property
    def charset(self):
        for i in range(0x8140, 0x9873):
            b = bytes([i >> 8, i & 0xff])
            try:
                c = b.decode('sjis')
            except UnicodeDecodeError:
                continue
            yield c


if __name__ == '__main__':
    ANSIFont().run()
    ShiftJISFont().run()
