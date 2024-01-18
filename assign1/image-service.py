import time
import os
from PIL import Image

while True:
    with open("image-service.txt", "r") as file:
        lineread = file.readline().strip()

        if lineread.isdigit() and 1 <= int(lineread) <= 5:
            with open("image-service.txt", "w") as file:
                img_format = 'jpg' if lineread in {'1', '2', '4'} else 'png'
                img_path = os.path.join("images", f'{lineread}.{img_format}')
                img = Image.open(img_path)
                print("Photo Found!")
                time.sleep(1)
                img.show()
                break
        
        else:
            print("Scanning for an integer to upload photo...")

        time.sleep(3)