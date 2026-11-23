"""Makes the Unity renders print well: thickens the 1-pixel lines and trims empty margins.
Usage: python prepare_figures.py <raw_dir> <out_dir>
"""
import glob, os, shutil, sys
from PIL import Image, ImageChops, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in glob.glob(os.path.join(src, "*.png")):
    im = Image.open(f).convert("RGB")
    bg = im.getpixel((2, 2))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L").point(lambda v: 255 if v > 12 else 0)
    ink = sum(1 for v in diff.getdata() if v) / (im.width * im.height)
    im = im.filter(ImageFilter.MinFilter(5 if ink < 0.03 else 3))
    box = diff.getbbox()
    if box:
        pad = 40
        crop = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
        s = min(im.width / crop.width, im.height / crop.height)
        crop = crop.resize((int(crop.width * s), int(crop.height * s)), Image.LANCZOS)
        canvas = Image.new("RGB", im.size, bg)
        canvas.paste(crop, ((im.width - crop.width) // 2, (im.height - crop.height) // 2))
        im = canvas
    im.save(os.path.join(dst, os.path.basename(f)))
shutil.copy(os.path.join(src, "stats.txt"), os.path.join(dst, "stats.txt"))
print("prepared", dst)
