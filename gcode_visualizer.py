import sys

import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QFileDialog

def parse_gcode_file(file_path):
    with open(file_path, 'r') as f:
        gcode = f.read()
    return parse_gcode(gcode)

def parse_gcode(gcode):
    lines = gcode.split('\n')
    segments = []
    segment = []
    for line in lines:
        if line.startswith('G0') or line.startswith('G1'):
            try:
                x = float(line.split('X')[1].split(' ')[0])
                y = float(line.split('Y')[1].split(' ')[0])
                segment.append((x, y))
            except:
                pass
        elif line.startswith('M107'):
            if segment:
                segments.append(segment)
                segment = []
    return segments

def plot_gcode(segments):
    colors = plt.cm.viridis(np.linspace(0, 1, len(segments)))

    for segment, color in zip(segments, colors):
        x, y = zip(*segment)
        plt.plot(x, y, color=color)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Gcode Visualization')
    plt.grid()
    plt.show()

def visualize_gcode(gcode_file):
    segments = parse_gcode_file(gcode_file)
    plot_gcode(segments)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gcode_file, _ = QFileDialog.getOpenFileName(None, 'Open File', '', 'Gcode (*.gcode)')
    if gcode_file:
        visualize_gcode(gcode_file)
