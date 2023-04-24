import os, sys
from svgpathtools import svg2paths
from svgpathtools import Line, CubicBezier


def parse_svg(file_path):
    paths, attributes = svg2paths(file_path)
    return [path for path, attr in zip(paths, attributes)]

def path_to_gcode(path, power=255, bezier_steps=100):
    def move_to(x, y, gcode_prefix):
        return f"{gcode_prefix} X{x:.2f} Y{y:.2f}\n"

    gcode = ""

    for i, segment in enumerate(path):
        if isinstance(segment, (Line, CubicBezier)):
            if isinstance(segment, Line):
                points = [segment.start, segment.end]
            else:
                points = [segment.point(t / bezier_steps) for t in range(bezier_steps + 1)]

            for j, point in enumerate(points):
                x, y = point.real, point.imag
                gcode_prefix = "G0" if i == 0 and j == 0 else "G1"

                if i == 0 and j == 0:
                    gcode += move_to(x, y, gcode_prefix)
                    gcode += f"M106 S{power}\n"  # Laser ON
                else:
                    gcode += move_to(x, y, gcode_prefix)

    gcode += "M107\n"  # Laser OFF
    return gcode

def svg_to_gcode(file_path, power=255, pass_nbr=1, speed=90):
    red_paths = parse_svg(file_path)
    gcode = f"G90\nG21\nG1 F{speed}\n"  # Set to absolute positioning, millimeters, and feed rate

    gcode += "G28 X0 Y0\n"
    for _ in range(pass_nbr):
        for path in red_paths:
            print(path)
            gcode += path_to_gcode(path, power=power)
    
    gcode += "G0 X0 Y0\n"  # Return to origin
    return gcode

def main():
    input_svg = 'base.svg'
    output_gcode = 'base.gcode'
    power = 255
    pass_nbr = 120
    speed = 900

    gcode = svg_to_gcode(input_svg, power=power, pass_nbr=pass_nbr, speed=speed)

    with open(output_gcode, 'w') as f:
        f.write(gcode)
    # move test.gcode file to I:\
    os.system(f"move {output_gcode} I:\\")

if __name__ == '__main__':
    main()
