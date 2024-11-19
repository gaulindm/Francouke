import svgwrite
import logging

# Define constants for default dimensions
PADDING = 20
TITLE_HEIGHT = 20
STRING_AREA_PADDING = 10
DEFAULT_FRET_COUNT = 4
DEFAULT_WIDTH = 80
DEFAULT_HEIGHT = 110

# Configure logger (remove basicConfig; assume it's set globally)
logger = logging.getLogger(__name__)

def validate_chord_data(frets, fingers):
    """
    Validate chord data input based on the number of strings.
    
    Args:
        frets (list[Union[int, str]]): The fret positions for each string. "x" represents a muted string.
        fingers (list[Union[int, None]] or None): The finger positions for each string. Can be None.

    Raises:
        ValueError: If input data is invalid.
    """
    string_count = len(frets)

    if fingers is None:
        # If fingers are None, treat as zeros
        fingers = [0] * string_count
    elif len(frets) != len(fingers):
        raise ValueError("Frets and fingers lists must have the same length.")

    # Allow "x" in frets for muted strings
    for fret in frets:
        if not (isinstance(fret, int) and fret >= 0) and fret != "x":
            raise ValueError("Frets must be non-negative integers or 'x' for muted strings.")

    logger.debug(f"Input validation passed for {string_count} strings.")
    return string_count, fingers

def generate_chord_svg(
    chord_name, frets, fingers=None, 
    fret_count=DEFAULT_FRET_COUNT, 
    width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT
):
    """
    Generate an SVG for a chord diagram.

    Args:
        chord_name (str): The name of the chord.
        frets (list[Union[int, str]]): The fret positions for each string. "x" represents a muted string.
        fingers (list[Union[int, None]] or None): The finger positions for each string. Can be None.
        fret_count (int): Number of frets to display.
        width (int): Width of the SVG.
        height (int): Height of the SVG.

    Returns:
        str: The SVG representation as a string.
    """
    # Validate input data
    string_count, fingers = validate_chord_data(frets, fingers)

    # Compute spacings
    string_spacing = (width - 2 * PADDING) / (string_count - 1)
    fret_spacing = (height - TITLE_HEIGHT - 2 * STRING_AREA_PADDING) / fret_count
    logger.debug(f"String spacing: {string_spacing}, Fret spacing: {fret_spacing}")

    # Initialize drawing
    dwg = svgwrite.Drawing(size=(width, height))
    dwg.add(dwg.text(
        chord_name, insert=(width / 2, TITLE_HEIGHT), 
        text_anchor="middle", font_size=16, font_weight="bold"
    ))

    # Draw strings
    for i in range(string_count):
        x = PADDING + i * string_spacing
        dwg.add(dwg.line(
            start=(x, TITLE_HEIGHT + STRING_AREA_PADDING), 
            end=(x, TITLE_HEIGHT + STRING_AREA_PADDING + fret_spacing * fret_count), 
            stroke="black", stroke_width=2
        ))

    #Draw nut 
    dwg.add(dwg.line(start=(PADDING,TITLE_HEIGHT + STRING_AREA_PADDING),end=(width - PADDING,TITLE_HEIGHT + STRING_AREA_PADDING),stroke="black", stroke_width=4)
    )

    # Draw frets
    for i in range(fret_count + 1):
        y = TITLE_HEIGHT + STRING_AREA_PADDING + i * fret_spacing
        dwg.add(dwg.line(
            start=(PADDING, y), 
            end=(width - PADDING, y), 
            stroke="black", stroke_width=2 if i == 0 else 1
        ))

    # Draw muted strings and finger positions
    for string_index, fret in enumerate(frets):
        x = PADDING + string_index * string_spacing
        if fret == "x":
            # Draw "x" at the top of the string for muted strings
            dwg.add(dwg.text(
                "x", insert=(x, TITLE_HEIGHT + 6), 
                text_anchor="middle", font_size=20, font_weight="bold", fill="black"
            ))
        elif isinstance(fret, int) and fret > 0:
            # Draw a circle and finger number for fretted notes
            y = TITLE_HEIGHT + STRING_AREA_PADDING + fret * fret_spacing - fret_spacing / 2
            logger.debug(f"Drawing finger circle at: x={x}, y={y}")
            dwg.add(dwg.circle(center=(x, y), r=8, fill="black"))
            if fingers[string_index] > 0:
                dwg.add(dwg.text(
                    str(fingers[string_index]), insert=(x, y + 4), 
                    text_anchor="middle", font_family="Georgia", font_size=12, 
                    font_weight="bold", fill="white"
                ))

    return dwg.tostring()
