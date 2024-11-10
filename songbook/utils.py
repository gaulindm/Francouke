
from PIL import Image, ImageDraw
import svgwrite
import os

def load_instruments(file_path='/instruments.yaml'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r') as file:
        instruments = yaml.safe_load(file)
    return instruments

def draw_chord_grid(instrument_name, chord_name, positions):
    instruments = load_instruments('path/to/instruments.yaml')
    instrument = next((inst for inst in instruments if inst['name'] == instrument_name), None)
    if not instrument:
        raise ValueError(f"Instrument {instrument_name} not found")

    strings = len(instrument['tuning'])
    tuning = instrument['tuning']
    
    # Create a blank image with white background
    img = Image.new('RGB', (100, 150), 'white')
    draw = ImageDraw.Draw(img)

    # Draw the grid
    for i in range(strings + 1):
        draw.line((20, 20 + i*30, 80, 20 + i*30), fill='black')  # Horizontal lines
    for i in range(strings):
        draw.line((20 + i*20, 20, 20 + i*20, 140), fill='black')  # Vertical lines

    # Draw the chord positions
    for string, fret in enumerate(positions):
        if fret != 0:
            draw.ellipse((15 + string*20, 15 + fret*30, 25 + string*20, 25 + fret*30), fill='black')

    # Add chord name
    draw.text((10, 5), chord_name, fill='black')

    # Save the image
    img.save(f'{chord_name}_{instrument_name}.png')

    # Convert to SVG
    dwg = svgwrite.Drawing(f'{chord_name}_{instrument_name}.svg', profile='tiny')
    dwg.add(dwg.image(href=f'{chord_name}_{instrument_name}.png', insert=(0, 0), size=(100, 150)))
    dwg.save()
