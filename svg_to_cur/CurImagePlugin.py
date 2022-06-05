from io import BytesIO

from PIL import Image, ImageFile, CurImagePlugin
from PIL._binary import o8
from PIL._binary import o16le as o16
from PIL._binary import o32le as o32

_MAGIC = b"\0\0\2\0"

def _save(im, fp, filename):
    fp.write(_MAGIC)  # (2+2)
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

Image.register_save(CurImagePlugin.CurImageFile.format, _save)