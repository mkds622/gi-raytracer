import yaml
from PIL import Image

def load_config(path="config/scene.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def rgb8_to_rgb255(rgb):
    return tuple(int(c) for c in rgb)

def main():
    cfg = load_config()

    preset = cfg["render"]["active_preset"]
    res = cfg["render"]["resolution_presets"][preset]
    width, height = res["width"], res["height"]

    bg = cfg["background"]["color_rgb8"]
    bg_color = rgb8_to_rgb255(bg)

    img = Image.new("RGB", (width, height), bg_color)
    img.save("outputs/checkpoint2_background.png")

    print(f"Rendered background image: {width}x{height}")

if __name__ == "__main__":
    main()
