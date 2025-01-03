import csv
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont, ImageColor
from textwrap import wrap
from typing import List, Dict

class ImageFeature:
    def __init__(self, font: str, font_size: int, text_color: str, 
                 justification: str, vertical_pos: float, element_name: str, rotation: float):
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.justification = justification
        self.vertical_pos = vertical_pos
        self.element_name = element_name
        self.rotation = rotation

    def __repr__(self):
        return (f"ImageFeature(font={self.font}, font_size={self.font_size}, text_color={self.text_color}, "
                f"justification={self.justification}, vertical_pos={self.vertical_pos}, element_name={self.element_name}, rotation={self.rotation})")

def read_csv_to_features(file_path: str) -> List[ImageFeature]:
    features = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            feature = ImageFeature(
                font=row['font'],
                font_size=int(row['font_size']),
                text_color=row['text_color'],
                justification=row['justification'],
                vertical_pos=float(row['vertical_pos']),
                element_name=row['element_name'],
                rotation=row['rotation']
            )
            features.append(feature)
    return features

def read_csv_to_cards(file_path: str) -> List[Dict[str, str]]:
    cards = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cards.append(row)
    return cards

def create_transparent_mask(image: Image) -> Image:
    """
    Converts an image to a mask where white is transparent and black is opaque.

    Args:
    - image (Image): The input image (can be any image, e.g., PNG).

    Returns:
    - Image: A new image in grayscale where white areas are transparent 
             and black areas are opaque, suitable to be used as a mask.
    """
    # Convert to grayscale (mode 'L')
    grayscale = image.convert("L")

    # Invert the grayscale image (white becomes black, and black becomes white)
    inverted_grayscale = Image.eval(grayscale, lambda x: 255 - x)

    # Return the mask (inverted grayscale)
    return inverted_grayscale

def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    """
    Convert a hex color string (e.g., '#555555') to an RGBA tuple with optional transparency.
    
    :param hex_color: Hex color string (e.g., '#555555').
    :param alpha: Alpha value for transparency (default is 255 for fully opaque).
    :return: A tuple (R, G, B, A).
    """
    # Convert the hex color to an RGB tuple
    rgb = ImageColor.getrgb(hex_color)
    
    # Add the alpha value for transparency
    return (rgb[0], rgb[1], rgb[2], alpha)

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> List[str]:
    """
    Wraps the text to fit within a specified width.

    Args:
        text (str): The text to be wrapped.
        font (ImageFont.FreeTypeFont): The font used to measure text size.
        max_width (int): The maximum width allowed for the text.
        draw (ImageDraw.Draw): The drawing context (not used directly here but kept for consistency).

    Returns:
        List[str]: A list of text lines wrapped to fit within max_width.
    """
    words = text.split()
    wrapped_lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        text_bbox = draw.textbbox((0, 0), test_line, font=font)  # Measure text bbox
        text_width = text_bbox[2] - text_bbox[0]  # Calculate the width
        if text_width <= max_width:
            current_line.append(word)
        else:
            wrapped_lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        wrapped_lines.append(' '.join(current_line))

    return wrapped_lines

def create_card_image(card: Dict[str, str], features: List['ImageFeature'], output_path: str):
    # Constants for card size and resolution
    CARD_WIDTH, CARD_HEIGHT = 750, 1050  # Poker card size at 300 DPI (2.5x3.5 inches)
    DPI = 300
    MARGIN = int(0.1 * DPI)  # Left and right margins

    # Create a blank white image
    image = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    for feature in features:
        text = card.get(feature.element_name, "")
        if not text:
            continue

        # Load font
        font_path = f"C:\\Windows\\Fonts\\{feature.font}.ttf"
        try:
            font = ImageFont.truetype(font_path, feature.font_size)
        except IOError:
            font = ImageFont.load_default()

        # Determine the maximum width for the text area
        max_width = CARD_WIDTH - 2 * MARGIN

        # Wrap the text to fit the width
        wrapped_lines = wrap_text(text, font, max_width, draw)

        # Calculate the maximum text height (consistent line spacing)
        max_text_height = max(
            draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
            for line in wrapped_lines
        )

        # Calculate initial position
        total_text_height = len(wrapped_lines) * max_text_height * 1.1  # Include spacing factor (1.1)
        y_start = int(feature.vertical_pos * CARD_HEIGHT - total_text_height / 2)
        y = y_start

        for line in wrapped_lines:
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            justification = feature.justification.lower()
            if justification == "center":
                x = (CARD_WIDTH - text_width) // 2
            elif justification == "right":
                x = CARD_WIDTH - text_width - MARGIN
            else:
                x = MARGIN  # Assume left justified

            # Draw the text line
            draw.text((x, y), line, fill=feature.text_color, font=font)

            # Increment y by the maximum line height plus spacing
            y += max_text_height * 1.1

    # Save the image
    image.save(output_path, "PNG")



def main():
    features_file_path = "layout.csv"
    cards_file_path = "cards.csv"

    features = read_csv_to_features(features_file_path)
    print("Features:")
    print(features)

    cards = read_csv_to_cards(cards_file_path)
    print("\nCards:")
    print(cards)

    # Generate images for each card
    for i, card in enumerate(cards):
        output_path = f"card_{i + 1}.png"
        create_card_image(card, features, output_path)
        print(f"Card image saved to {output_path}")

if __name__ == "__main__":
    main()
