import os, sys
from tqdm import tqdm
from svgpathtools import svg2paths
from svgpathtools import Line, CubicBezier, Arc

from PyQt6.QtWidgets import QApplication, QFileDialog


segment_type_map = {
    Line: 'Line',
    CubicBezier: 'CubicBezier',
    Arc: 'Arc'
}


def parse_svg(file_path):
    paths, attributes = svg2paths(file_path)
    return [path for path, attr in zip(paths, attributes)]


def segment_to_points(segment, segment_type, steps=100):
    return (
        [segment.start, segment.end]
        if segment_type == Line
        else [segment.point(t / steps) for t in range(steps + 1)]
    )


def path_to_gcode(path, scale=1, power=255, steps=100, first_path=True):
    def move_to(x, y, gcode_prefix):
        return f"{gcode_prefix} X{x:.2f} Y{y:.2f}\n"

    gcode = ""

    for i, segment in enumerate(path):
        points = segment_to_points(segment, type(segment), steps)

        # Active le laser au début de chaque segment
        if i == 0 or not first_path:
            gcode += "M106 S{power}\n"  # Allume le laser

        for j, point in enumerate(points):
            y, x = point.real * scale - 220 , point.imag * scale + 15
            gcode_prefix = "G1"  # Utilise G1 pour le mouvement linéaire

            gcode += move_to(x, y, gcode_prefix)

        # Désactive le laser à la fin de chaque segment
        gcode += "M107\n"  # Éteint le laser

        # S'assure que le prochain segment ne sera pas traité comme le premier
        first_path = False

    return gcode


def svg_to_gcode(file_path, scale=1.0, power=255, pass_nbr=1, speed=90):
    red_paths = parse_svg(file_path)
    print(f"Found {len(red_paths)} paths in {file_path}")
    
    gcode = f"G90\nG21\nG1 F{speed}\n"  # Set to absolute positioning, millimeters, and feed rate

    gcode += "G28 X0 Y0\n"
    
    for _ in tqdm(range(pass_nbr), desc='Overall Progress'):
        for i, path in tqdm(enumerate(red_paths), desc='Path Progress', total=len(red_paths)):
            first_path = i == 0
            gcode += path_to_gcode(path, scale=scale, power=power, first_path=first_path)
        gcode += "M107\n"  # Laser OFF
    
    gcode += "G0 X0 Y0\n"  # Return to origin
    return gcode

def main():
    app = QApplication(sys.argv)
    input_svg = QFileDialog.getOpenFileName(None, 'Open File', '', 'SVG (*.svg)')[0]
    if not input_svg:
        return
    output_gcode = os.path.basename(input_svg).split('.')[0] + '.gcode'
    power = 255
    pass_nbr = 1 # 120 passes for 3mm plywood
    speed = 9000

    gcode = svg_to_gcode(input_svg, scale=0.27, power=power, pass_nbr=pass_nbr, speed=speed)

    with open(output_gcode, 'w') as f:
        f.write(gcode)
    import gcode_visualizer
    gcode_visualizer.visualize_gcode(output_gcode)

    # move test.gcode file to J:\
    os.system(f"move {output_gcode} J:\\")


if __name__ == '__main__':
    main()
