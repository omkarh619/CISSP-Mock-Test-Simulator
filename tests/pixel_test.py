from PIL import Image

def hex_from_rgb(rgb):
    return '#%02x%02x%02x' % rgb[:3]

def test_visual_pixels(image_path="ui_audit_screenshot.png"):
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        width, height = img.size
        
        print(f"Image Resolution: {width}x{height}")
        
        # 1. Sample Header Color (Top area)
        header_pixel = img.getpixel((10, 10))
        header_hex = hex_from_rgb(header_pixel)
        print(f"Header Pixel at (10,10): {header_hex}")
        
        # 2. Sample Footer Color (Bottom area)
        footer_pixel = img.getpixel((10, height - 10))
        footer_hex = hex_from_rgb(footer_pixel)
        print(f"Footer Pixel at (10, {height-10}): {footer_hex}")
        
        # 3. Sample Center Background (White)
        center_pixel = img.getpixel((width // 2, height // 2))
        center_hex = hex_from_rgb(center_pixel)
        print(f"Center Background Pixel: {center_hex}")

        # Expected Values
        TARGET_BLUE = "#003057"
        TARGET_GRAY = "#e1e1e1"
        TARGET_WHITE = "#ffffff"

        print("\n--- Visual Validation Results ---")
        if header_hex == TARGET_BLUE:
            print("PASS: Header color matches ISC2 Dark Blue (#003057)")
        else:
            print(f"FAIL: Header color {header_hex} deviates from target {TARGET_BLUE}")

        if footer_hex == TARGET_GRAY:
            print("PASS: Footer color matches Pearson VUE Gray (#e1e1e1)")
        else:
            print(f"FAIL: Footer color {footer_hex} deviates from target {TARGET_GRAY}")

        if center_hex == TARGET_WHITE:
            print("PASS: Content background is clean white (#ffffff)")
        else:
            print(f"FAIL: Center color {center_hex} is not white")

    except Exception as e:
        print(f"Visual analysis failed: {e}")

if __name__ == "__main__":
    test_visual_pixels()
