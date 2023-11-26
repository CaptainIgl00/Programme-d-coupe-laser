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


def path_to_gcode(path, scale=1.0, power=255, steps=100, first_path=True):
    def move_to(x, y, gcode_prefix):
        return f"{gcode_prefix} X{x:.2f} Y{y:.2f}\n"

    gcode = ""

    for i, segment in enumerate(path):
        points = segment_to_points(segment, type(segment), steps)

        for j, point in enumerate(points):
            x, y = point.real * scale, point.imag * scale
            gcode_prefix = "G0" if i == 0 and j == 0 and first_path else "G1"

            if i == 0 and j == 0:
                if not first_path:
                    gcode += "M107\n"  # Laser OFF
                gcode += move_to(x, y, gcode_prefix)
                gcode += f"M106 S{power}\n"  # Laser ON
            else:
                gcode += move_to(x, y, gcode_prefix)

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
    output_gcode = 'output.gcode'
    power = 255
    pass_nbr = 12 # 120 passes for 3mm plywood
    speed = 9000

    gcode = svg_to_gcode(input_svg, power=power, pass_nbr=pass_nbr, speed=speed)

    with open(output_gcode, 'w') as f:
        f.write(gcode)
    # move test.gcode file to I:\
    os.system(f"move {output_gcode} J:\\")

if __name__ == '__main__':
    main()
