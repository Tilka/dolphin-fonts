#!/usr/bin/env python3

# Author: flacs
# License: GPL v2+
# Based on documentation by:
# - org <kvzorganic@mail.ru> (SZP/Yay0 file format)
# - EkeEke <ekeeke31@gmail.com> (http://devkitpro.org/viewtopic.php?f=7&t=191)
# - groepaz <groepaz@gmx.net> (http://hitmen.c02.at/files/yagcd/yagcd/)

import struct
from PIL import Image


def u8(data, ofs):
    return struct.unpack('>B', data[ofs:ofs + 1])[0]
def u16(data, ofs):
    return struct.unpack('>H', data[ofs:ofs + 2])[0]
def u32(data, ofs):
    return struct.unpack('>I', data[ofs:ofs + 4])[0]


def deyay0(src):
    assert src[0:4] == b'Yay0'

    i = u32(src, 4)
    j = u32(src, 8)
    k = u32(src, 12)

    q = 0
    cnt = 0
    p = 16
    dst = bytearray(i)

    while q < i:
        if cnt == 0:
            r22 = u32(src, p)
            p += 4
            cnt = 32

        if r22 & 0x80000000:
            dst[q] = u8(src, k)
            k += 1
            q += 1
        else:
            r26 = u16(src, j)
            j += 2

            r25 = q - (r26 & 0xfff)

            r30 = r26 >> 12

            if r30 == 0:
                r5 = u8(src, k)
                k += 1
                r30 = r5 + 18
            else:
                r30 += 2

            r5 = r25

            for _ in range(r30):
                dst[q] = dst[r5 - 1]
                q += 1
                r5 += 1

        r22 <<= 1
        cnt -= 1

    return dst


def font_to_images(font):

    def decode_palette(src):
        dst = bytearray(sheet_size)
        for i in range(sheet_size // 2):
            v1 = (src[i] & 0b11000000) >> 6
            v2 = (src[i] & 0b00110000) >> 4
            v3 = (src[i] & 0b00001100) >> 2
            v4 = (src[i] & 0b00000011) >> 0
            dst[2 * i + 0] = (palette[v1] & 0xf0) | (palette[v2] & 0x0f)
            dst[2 * i + 1] = (palette[v3] & 0xf0) | (palette[v4] & 0x0f)
        return dst

    def decode_i4(src):
        # TODO: rewrite this to use source order
        dst = bytearray(width * height)
        for t in range(height):
            for s in range(width):
                sBlk = s >> 3
                tBlk = t >> 3
                widthBlks = width >> 3
                base = (tBlk * widthBlks + sBlk) << 5
                blkS = s & 7
                blkT = t & 7
                blkOff = (blkT << 3) + blkS
                rs = 0 if blkOff & 1 else 4
                offset = base + (blkOff >> 1)
                if offset >= sheet_size:
                    continue
                val = (src[offset] >> rs) & 0xf
                val |= val << 4
                dst[s + t * width] = val
        return bytes(dst)

    sheet_size = u32(font, 0x14)
    width = u16(font, 0x1e)
    height = u16(font, 0x20)
    ofs = u32(font, 0x24)
    full_size = u32(font, 0x28)
    palette = font[0x2c:0x2c + 4]

    font = font[ofs:]

    sheets = full_size // sheet_size

    for sheet in range(sheets):
        texels = decode_palette(font)
        pixels = decode_i4(texels)
        font = font[sheet_size // 2:]
        yield Image.frombytes('L', (width, height), pixels, 'raw')


if __name__ == '__main__':
    import os
    import sys
    path = sys.argv[1]
    root, _ = os.path.splitext(os.path.basename(path))
    in_data = open(path, 'rb').read()
    font = deyay0(in_data)
    open(root + '.font', 'wb+').write(font)

    for i, image in enumerate(font_to_images(font)):
        image.save(root + '_{}.png'.format(i))
