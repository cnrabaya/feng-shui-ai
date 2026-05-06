from PIL import Image, ImageOps

def fix_rotation(image_path):
    img = Image.open(image_path)
    return ImageOps.exif_transpose(img)

def prepare_for_upload(img, max_dimension=1920):
    # Only resize if actually oversized
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    return img
