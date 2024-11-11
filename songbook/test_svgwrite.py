import svgwrite

def create_test_svg():
    # Create a simple SVG drawing
    dwg = svgwrite.Drawing(filename="test_output.svg", size=("100px", "100px"))
    dwg.add(dwg.line((10, 10), (90, 90), stroke=svgwrite.rgb(10, 10, 16, '%')))
    dwg.add(dwg.text("Test SVG", insert=(10, 20), fill="black"))
    dwg.save()
    print("SVG file 'test_output.svg' created successfully.")

if __name__ == "__main__":
    create_test_svg()
