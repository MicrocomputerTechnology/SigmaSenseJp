from PIL import Image, ImageOps, ImageFilter

def identity(image: Image.Image) -> Image.Image:
    """恒等射：画像を何も変更しない"""
    return image.copy()

def rotate_90(image: Image.Image) -> Image.Image:
    """画像を90度回転させる"""
    return image.rotate(90, expand=True)

def add_red_tint(image: Image.Image) -> Image.Image:
    """画像に赤い色合いを加える"""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    r, g, b = image.split()
    
    # 赤チャンネルを強調し、緑と青を少し減衰させる
    r = r.point(lambda i: i * 1.2 if i < 220 else 255)
    g = g.point(lambda i: i * 0.8)
    b = b.point(lambda i: i * 0.8)
    
    return Image.merge('RGB', (r, g, b))

def scale_50_percent(image: Image.Image) -> Image.Image:
    """画像を50%に縮小する"""
    new_size = (image.width // 2, image.height // 2)
    return image.resize(new_size)

def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """画像をグレースケールに変換する"""
    return ImageOps.grayscale(image).convert('RGB')

def shift_left(image: Image.Image, shift_pixels=50) -> Image.Image:
    """画像を左にずらす"""
    new_image = Image.new(image.mode, image.size, (255, 255, 255))
    new_image.paste(image, (-shift_pixels, 0))
    return new_image
