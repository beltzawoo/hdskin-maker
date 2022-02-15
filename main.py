from PIL import Image
import json

def rgb2hex(rgb: tuple) -> str:
    #return f"#{hex(rgb[0])}{hex(rgb[1])}{hex(rgb[2])}".replace("0x", "")
    if rgb[3] == 0:
        return "transparent"
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def open_skin(filename: str) -> Image:
    with Image.open(filename) as skin:
        skin = skin.convert("RGBA")
        return skin

def get_colors(base_skin: Image) -> dict:
    colors = base_skin.getcolors()
    colors = [x[1] for x in colors]
    colors = {rgb2hex(x): "block" for x in colors}
    return colors

def dump_colors(colors: dict, filename="colors.json") -> None:
    with open(filename, "w") as file:
        file.write(json.dumps(colors, indent=2))

def load_colors(filename="colors.json") -> dict:
    with open(filename, "r") as file:
        colors = json.loads(file.read())
        return colors

def transform_coordinates(x, y) -> tuple:
    return (x*16, y*16)

def get_block_image(color:str, colors: dict, folder=".") -> Image:
    block = colors[color] + ".png"
    block_image = Image.open(f"{folder}/{block}") 
    return block_image

def transform_skin(base_skin, colors: dict, blocks_folder="blocks") -> Image:
    transformed_skin = Image.new(mode="RGBA", size=(1024, 1024))
    for x in range(64):
        for y in range(64):
            pixel_color = base_skin.getpixel((x, y))
            pixel_color = rgb2hex(pixel_color)
            if not pixel_color == "transparent":
                block_image = get_block_image(pixel_color, colors, blocks_folder)
                transformed_skin.paste(block_image, box=transform_coordinates(x, y))
    return transformed_skin

def preparation(skin_filename: str) -> None:
    base_skin = open_skin(skin_filename)
    colors = get_colors(base_skin)
    dump_colors(colors)

def transformation(base_skin_filename: str, output_filename: str):
    base_skin = open_skin(base_skin_filename)
    colors = load_colors()
    transformed_skin = transform_skin(base_skin, colors)
    transformed_skin.save(output_filename)

if __name__ == "__main__":
    print("HDSkin-maker by charmante")
    choice = input("""1/ Preparation phase: dump colors
2/ Transformation phase: create skins from colors file
Choice: """)
    if choice == '1':
        skin_filename = input("Enter input skin filename: ")
        preparation(skin_filename)
        print("Done! Go fill colors.json with your blocks and come back with phase 2 :D")
    if choice == '2':
        base_skin_filename = input("Enter input skin filename: ")
        output_filename = input("Enter output skin filename: ")
        transformation(base_skin_filename, output_filename)
        print("Done! Check your output skin now :3")
