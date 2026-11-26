from PIL import Image
img = Image.open("../icons/icon192.png")
img.save("../icons/icon.ico", format="ICO", sizes=[(192, 192)])