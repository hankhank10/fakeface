from PIL import Image
import pathlib

maxsize = (350,350)

for input_img_path in pathlib.Path("input").iterdir():
    output_img_path = str(input_img_path).replace("classified/","thumb/thumb_")
    with Image.open(input_img_path) as im:
        im.thumbnail(maxsize)
        im.save(output_img_path, "JPEG", dpi=(300,300))
        print(f"processing file {input_img_path} done...")