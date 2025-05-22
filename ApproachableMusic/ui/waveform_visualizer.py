import numpy as np
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen

from .theme import MATERIAL_COLORS # Assuming theme.py is in the same directory

class WaveformVisualizer(QWidget):
    """A widget to display a waveform shape."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # Fixed height, expanding width
        self.samples = np.array([])
        self.line_color = QColor(MATERIAL_COLORS.get('accent', '#FF0000')) # Default to red if accent not found
        self.background_color = QColor(MATERIAL_COLORS.get('background', '#333333'))

    def update_waveform(self, samples):
        """Update the waveform data to display."""
        if samples is not None and len(samples) > 0:
            # Ensure samples are normalized between -1 and 1 for consistent display
            max_abs = np.max(np.abs(samples))
            if max_abs > 0:
                self.samples = samples / max_abs
            else:
                self.samples = np.zeros_like(samples)
        else:
            self.samples = np.array([])
        self.update() # Schedule a repaint

    def paintEvent(self, event):
        """Paint the waveform."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Clear background
        painter.fillRect(0, 0, width, height, self.background_color)

        if len(self.samples) < 2:
            return # Not enough data to draw

        painter.setPen(QPen(self.line_color, 1.5))

        # Calculate points for the line graph
        points = []
        num_samples_to_draw = len(self.samples)
        
        # X-axis scaling: fit all samples to the widget width
        x_step = width / (num_samples_to_draw - 1) if num_samples_to_draw > 1 else width

        for i in range(num_samples_to_draw):
            x = i * x_step
            # Y-axis scaling: samples are -1 to 1. Map to 0 to height.
            # (sample + 1) / 2 maps -1..1 to 0..1
            # Then multiply by height. We want 0 at center, so map to height/2 +/- sample_val * height/2
            y_normalized = self.samples[i] # Should be in -1 to 1 range
            y = (height / 2) - (y_normalized * height / 2 * 0.9) # 0.9 to leave some margin

            points.append((x, y))

        # Draw lines between points
        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]),
                             int(points[i+1][0]), int(points[i+1][1]))

        # Draw center line (zero amplitude)
        painter.setPen(QPen(QColor(80, 80, 80), 1, Qt.DashLine)) # Darker gray dashed line
        center_y = height / 2
        painter.drawLine(0, int(center_y), width, int(center_y))
