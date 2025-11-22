from PIL import Image
import pillow_svg

# Load SVG directly in Pillow
img = Image.open("icons/icon.png")  # requires pillow-svg
img.save("icons/icon.ico", sizes=[(16,16),(32,32),(64,64)])
