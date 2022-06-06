import os, builtins

from io import BytesIO
from typing import BinaryIO
from PIL import Image, CurImagePlugin
from PIL._binary import o8
from PIL._binary import o16le as o16
from PIL._binary import o32le as o32

_MAGIC_CUR = b"\0\0\2\0"

def _save_cur(im, fp, filename):
    fp.write(_MAGIC_CUR)  # (2+2)
    width, height = im.size

    hotspot = im.encoderinfo.get(
        "hotspot",
        (0, 0),
    )
    hotspotX = hotspot[0] / width
    hotspotY = hotspot[1] / height

    sizes = im.encoderinfo.get(
        "sizes",
        [(32, 32), (48, 48), (64, 64), (96, 96), (128, 128), (256, 256)],
    )
    frames = []
    for size in sorted(set(sizes)):
        if size[0] > width or size[1] > height or size[0] > 256 or size[1] > 256:
            continue

        if im.size == size:
            frames.append(im)
        else:
            # TODO: invent a more convenient method for proportional scalings
            frame = im.copy()
            frame.thumbnail(size, Image.Resampling.LANCZOS, reducing_gap=None)
            frames.append(frame)
    fp.write(o16(len(frames)))  # idCount(2)
    offset = fp.tell() + len(frames) * 16
    for frame in frames:
        width, height = frame.size
        # 0 means 256
        fp.write(o8(width if width < 256 else 0))  # bWidth(1)
        fp.write(o8(height if height < 256 else 0))  # bHeight(1)

        fp.write(b"\0")  # bColorCount(1)
        fp.write(b"\0")  # bReserved(1)

        fp.write(o16(round(hotspotX * width)))  # hotspotHorizontal(2)
        fp.write(o16(round(hotspotY * height)))  # hotspotVertical(2)

        image_io = BytesIO()
        frame.save(image_io, "png")
        image_io.seek(0)
        image_bytes = image_io.read()
        bytes_len = len(image_bytes)
        fp.write(o32(bytes_len))  # dwBytesInRes(4)
        fp.write(o32(offset))  # dwImageOffset(4)
        current = fp.tell()
        fp.seek(offset)
        fp.write(image_bytes)
        offset = offset + bytes_len
        fp.seek(current)

Image.register_save(CurImagePlugin.CurImageFile.format, _save_cur)

def _save_ani(fp: BinaryIO, frames, seconds_per_frame: float, hotspot):
    # RIFF struct
    fp.write(b"RIFF") # ID(4)
    riff_size_offset = fp.tell()
    fp.write(o32(0)) # headerSize(4)
    fp.write(b"ACON") # headerID(4)

    # 'anih' chunk
    fp.write(b"anih") # chunkHeader(4)
    fp.write(o32(36)) # chunkHeaderSize(4)

    fp.write(o32(36)) # headerSize(4)
    fp.write(o32(len(frames))) # numFrames(4)
    fp.write(o32(len(frames))) # numSteps(4)
    fp.write(o32(0)) # width(4)
    fp.write(o32(0)) # height(4)
    fp.write(o32(0)) # bitCount(4)
    fp.write(o32(0)) # numPlanes(4)
    fp.write(o32(round(seconds_per_frame * 60))) # displayRate(4)
    fp.write(o32(1)) # flags(4)

    # LIST struct
    fp.write(b"LIST") # ID(4)
    list_size_offset = fp.tell()
    fp.write(o32(0)) # headerSize(4)
    fp.write(b"fram") # headerID(4)

    for frame in frames:
        # 'icon' chunk
        image_io = BytesIO()
        frame.save(image_io, "cur", hotspot=hotspot)
        image_io.seek(0)
        image_bytes = image_io.read()

        fp.write(b"icon") # chunkHeader(4)
        fp.write(o32(len(image_bytes))) # chunkHeaderSize(4)
        fp.write(image_bytes)

        # padding
        if fp.tell() & 1:
            fp.write(o8(0))
    
    current = fp.tell()

    list_size = current - (list_size_offset + 4)
    fp.seek(list_size_offset)
    fp.write(o32(list_size))

    riff_size = current - (riff_size_offset + 4)
    fp.seek(riff_size_offset)
    fp.write(o32(riff_size))

def save_ani(filename, frames, seconds_per_frame: float, hotspot=(0,0)):
    created = not os.path.exists(filename)
    fp = builtins.open(filename, "w+b")
    try:
        _save_ani(fp, frames, seconds_per_frame, hotspot)
    except Exception:
        fp.close()
        if created:
            try:
                os.remove(filename)
            except PermissionError:
                pass
        raise
    fp.close()