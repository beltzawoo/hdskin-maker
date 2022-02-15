from PIL import Image
import json
import glob

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
    block_rgbs = load_block_rgbs()
    colors = base_skin.getcolors()
    colors = [x[1] for x in colors]
    colors = {rgb2hex(x): find_closest_block(x, block_rgbs) for x in colors}
    #colors = {rgb2hex(x): "block" for x in colors}
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

def weighted_average(items: list, weights: list) -> int:
    numerator = sum([items[i]*weights[i] for i in range(len(items))])
    denominator = sum(weights)
    return round(numerator/denominator)

def average_rgb(block, folder='blocks') -> list:
    block_image = Image.open(f'{folder}/{block}.png')
    block_image = block_image.convert("RGBA")
    colors = block_image.getcolors()
    if colors == None:
        return [9999, 9999, 9999]
    if not 255 in [x[1][3] for x in colors]:
        return [9999, 9999, 9999]
    weights = [x[0] for x in colors]
    rgb = []
    for i in range(3):
        # First time will check for red, then blue, and green
        # this "current_values" hold every different reds corresponding to weight
        # (basically a part of the get_colors list)
        current_channel = [x[1][i] for x in colors]
        rgb.append(weighted_average(current_channel, weights))
    return rgb

def load_block_rgbs(save_filename="blocks.json"):
    with open(save_filename, 'r') as file:
        block_rgbs = json.loads(file.read())
    return block_rgbs

def find_closest_block(target_rgb: tuple, block_rgbs: dict):
    lowest_penalty = 99999
    closest_block = 'stone'
    for block, rgb in block_rgbs.items():
        penalty = 0
        for i in range(3):
            penalty += abs(rgb[i] - target_rgb[i])
        if penalty < lowest_penalty:
            lowest_penalty = penalty
            closest_block = block
    return closest_block

def dump_block_rgbs(folder="blocks/", save_filename="blocks.json"):
    blocks = [x.replace(f'{folder}/', '').replace('.png', '') for x in glob.glob(f'{folder}/*.png')]
    block_rgbs = {i: average_rgb(i) for i in blocks}
    with open(save_filename, 'w') as file:
        file.write(json.dumps(block_rgbs, indent=2))


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
3/ Extra: analyze blocks rgbs and save them for auto block assignment
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
    if choice == '3':
        dump_block_rgbs(folder='blocks')
        print("Done! You can generate a skin colors.json and now it will be filled with sample blocks :)")
