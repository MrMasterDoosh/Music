from PyQt5.QtWidgets import (QFrame, QSlider, QDial, QCheckBox, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRectF # Added pyqtSignal and QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetricsF # Added QFontMetricsF
import numpy as np

from ui.theme import MATERIAL_COLORS, FONT_FAMILY # Import FONT_FAMILY

class MaterialCard(QFrame):
    """A Material Design inspired card widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("materialCard")
        self.setStyleSheet("""
            #materialCard {
                background-color: """ + MATERIAL_COLORS['surface'] + """;
                border-radius: 8px;
                border: none;
            }
        """)
        
        # Add drop shadow effect
        self.setGraphicsEffect(None)  # Remove any existing effect
        
    def paintEvent(self, event):
        """Custom paint event to draw the card with shadow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        try:
            # Draw shadow
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 30))
            painter.drawRoundedRect(self.rect().adjusted(3, 3, 3, 3), 8, 8)
            
            # Draw card
            painter.setBrush(QColor(MATERIAL_COLORS['surface']))
            painter.drawRoundedRect(self.rect(), 8, 8)
        finally:
            painter.end()
        
        super().paintEvent(event)

class ModernSlider(QSlider):
    """A modernized slider with a sleek appearance"""
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: """ + MATERIAL_COLORS['background'] + """;
                margin: 2px 0;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: """ + MATERIAL_COLORS['primary'] + """;
                border: none;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider::handle:horizontal:hover {
                background: """ + MATERIAL_COLORS['primary_light'] + """;
            }
            
            QSlider::handle:horizontal:pressed {
                background: """ + MATERIAL_COLORS['primary_dark'] + """;
            }
            
            QSlider::add-page:horizontal {
                background: """ + MATERIAL_COLORS['background'] + """;
                border-radius: 3px;
            }
            
            QSlider::sub-page:horizontal {
                background: """ + MATERIAL_COLORS['primary_light'] + """;
                border-radius: 3px;
            }
        """)

class ModernDial(QDial):
    """A modernized dial with a sleek appearance"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QDial {
                background-color: """ + MATERIAL_COLORS['surface'] + """;
                color: """ + MATERIAL_COLORS['primary'] + """;
            }
        """)

class ModernCheckBox(QCheckBox):
    """A modernized checkbox with a sleek appearance"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: """ + MATERIAL_COLORS['text_primary'] + """;
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid """ + MATERIAL_COLORS['primary'] + """;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: """ + MATERIAL_COLORS['background'] + """;
            }
            
            QCheckBox::indicator:checked {
                background-color: """ + MATERIAL_COLORS['primary'] + """;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48cGF0aCBmaWxsPSIjRkZGRkZGIiBkPSJNOSAxNi4yTDQuOCAxMmwtMS40IDEuNEw5IDE5IDIxIDdsLTEuNC0xLjRMOSAxNi4yeiIvPjwvc3ZnPg==);
            }
            
            QCheckBox::indicator:hover {
                border-color: """ + MATERIAL_COLORS['primary_light'] + """;
            }
        """)

class ModernRotaryDial(QFrame):
    """A modern rotary dial with a sleek appearance"""
    currentIndexChanged = pyqtSignal(int) # Signal to emit when index changes

    def __init__(self, items, parent=None, item_type="Chord"): # item_type can be "Chord" or "Mode"
        super().__init__(parent)
        # Assuming items are now list of dicts: e.g., [{'roman': 'I', 'quality': 'Major'}, {'roman': 'ii', 'quality': 'Minor'}]
        # Or for modes: [{'name': 'Ionian', 'quality': 'Major Equivalent'}]
        self.items = items
        self.item_type = item_type # To know how to format/display
        self.current_index = 0
        self.setMinimumSize(280, 90) # Wider for carousel view
        self.setMaximumSize(400, 90)

        # Define colors (ideally from theme.py, using placeholders if not present)
        self.color_major = QColor(MATERIAL_COLORS.get('green_primary', QColor(102, 187, 106))) # Light Green
        self.color_minor = QColor(MATERIAL_COLORS.get('blue_primary', QColor(66, 165, 245)))   # Light Blue
        self.color_diminished = QColor(MATERIAL_COLORS.get('purple_primary', QColor(171, 71, 188))) # Light Purple
        self.color_default_bg = QColor(MATERIAL_COLORS['surface'])
        self.text_color_on_colored_bg = Qt.white
        self.text_color_default = QColor(MATERIAL_COLORS['text_primary'])
        self.text_color_neighbor = QColor(MATERIAL_COLORS.get('text_secondary', QColor(150,150,150)))


        # Internal QDial for logic, not necessarily for display
        self._internal_dial = QDial() # Not parented, just for state
        self._internal_dial.setRange(0, len(items) - 1 if items else 0)
        self._internal_dial.setSingleStep(1)
        self._internal_dial.setWrapping(True)
        self._internal_dial.valueChanged.connect(self._update_current_index_from_dial)

        # Create left/right buttons
        button_height = 40
        button_width = 30
        self.left_button = QPushButton("<", self)
        self.left_button.setGeometry(5, (self.height() - button_height) // 2, button_width, button_height)
        self.left_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_primary']};
                border-radius: {button_height//2}px; border: 1px solid {MATERIAL_COLORS['primary_light']};
                font-size: 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {MATERIAL_COLORS['primary_light']}; }}
            QPushButton:pressed {{ background-color: {MATERIAL_COLORS['primary']}; }}
        """)
        self.left_button.clicked.connect(self.rotate_left)
        
        self.right_button = QPushButton(">", self)
        # Position right button at the other end
        self.right_button.setGeometry(self.width() - button_width - 5, (self.height() - button_height) // 2, button_width, button_height)
        self.right_button.setStyleSheet(self.left_button.styleSheet()) # Same style
        self.right_button.clicked.connect(self.rotate_right)
        
        # No explicit QLabel for current item, will be drawn in paintEvent
        # self.label is removed

    def resizeEvent(self, event):
        super().resizeEvent(event)
        button_height = 40
        button_width = 30
        self.left_button.setGeometry(5, (self.height() - button_height) // 2, button_width, button_height)
        self.right_button.setGeometry(self.width() - button_width - 5, (self.height() - button_height) // 2, button_width, button_height)
        self.update()


    def _get_item_display_info(self, index):
        if not self.items or not (0 <= index < len(self.items)):
            return {"roman_display": "N/A", "quality_text": "", "bg_color": self.color_default_bg, "text_color": self.text_color_default}

        item = self.items[index]
        roman_display = ""
        quality_text = ""
        bg_color = self.color_default_bg
        text_color = self.text_color_default

        if self.item_type == "Chord":
            quality_input = item.get('quality', '').lower() # Expect "maj", "min", "dim", "aug" etc.
            roman = item.get('roman', '')
            
            # Default to avoid unset variables if no match
            roman_display = roman 
            quality_text = item.get('quality', '').capitalize()
            bg_color = self.color_default_bg
            text_color = self.text_color_default

            if quality_input == 'maj':
                roman_display = roman.upper()
                bg_color = self.color_major
                text_color = self.text_color_on_colored_bg
                quality_text = "Major"
            elif quality_input == 'min':
                roman_display = roman.lower()
                bg_color = self.color_minor
                text_color = self.text_color_on_colored_bg
                quality_text = "Minor"
            elif quality_input == 'dim':
                roman_display = roman.lower() + "°"
                bg_color = self.color_diminished
                text_color = self.text_color_on_colored_bg
                quality_text = "Dim."
            elif quality_input == 'aug': # Example for augmented
                roman_display = roman.upper() + "+" # Or however you want to display augmented
                # bg_color = self.color_augmented # Define if needed
                # text_color = self.text_color_on_colored_bg
                quality_text = "Aug."
            # else: roman_display, quality_text, bg_color, text_color remain as initialized (default/fallback)
        
        elif self.item_type == "Mode":
            roman_display = item.get('name', 'N/A') # For modes, 'name' is the primary display
            quality_text = item.get('quality', '') # e.g. "Major Equivalent"
            # Modes usually don't have the same color coding, use default or a specific mode color logic if needed
            # For now, default background for modes.
        
        return {"roman_display": roman_display, "quality_text": quality_text, "bg_color": bg_color, "text_color": text_color}

    def _update_current_index_from_dial(self, index):
        if self.current_index != index:
            self.current_index = index
            self.update() # Trigger repaint
            self.currentIndexChanged.emit(self.current_index)

    def update_index(self, index): # Kept for external setting if needed, though dial is internal
        if self.items and 0 <= index < len(self.items):
            self._internal_dial.setValue(index) # This will trigger _update_current_index_from_dial

    def rotate_left(self):
        if not self.items: return
        self._internal_dial.setValue((self._internal_dial.value() - 1 + len(self.items)) % len(self.items))
        
    def rotate_right(self):
        if not self.items: return
        self._internal_dial.setValue((self._internal_dial.value() + 1) % len(self.items))
        
    def get_value(self):
        if not self.items: return None
        return self.items[self.current_index]
        
    def get_index(self):
        return self.current_index
        
    def paintEvent(self, event):
        super().paintEvent(event) # Handles basic QFrame painting like background if not overridden by stylesheet
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Clear background (optional, if not handled by stylesheet or super.paintEvent)
        # painter.fillRect(self.rect(), QColor(MATERIAL_COLORS['background_dark']))


        if not self.items:
            painter.end()
            return

        # Define areas for current, prev, next items
        # Leave space for buttons on sides
        content_x_start = 40 
        content_x_end = width - 40
        content_width = content_x_end - content_x_start
        
        center_item_width = content_width * 0.46 # Slightly less than 50% to give more space to neighbors if needed
        neighbor_item_width = content_width * 0.27 # Slightly more

        center_item_x = content_x_start + (content_width - center_item_width) / 2
        center_item_rect = QRectF(center_item_x, 0, center_item_width, height)
        
        # Adjust neighbor rects to be directly beside the center item, filling remaining space
        prev_item_rect = QRectF(content_x_start, 0, center_item_x - content_x_start, height)
        next_item_rect = QRectF(center_item_x + center_item_width, 0, content_x_end - (center_item_x + center_item_width), height)


        # Current item
        current_info = self._get_item_display_info(self.current_index)
        self._draw_item(painter, center_item_rect, current_info, is_center=True)

        # Previous item
        prev_index = (self.current_index - 1 + len(self.items)) % len(self.items)
        prev_info = self._get_item_display_info(prev_index)
        self._draw_item(painter, prev_item_rect, prev_info, is_center=False)
        
        # Next item
        next_index = (self.current_index + 1) % len(self.items)
        next_info = self._get_item_display_info(next_index)
        self._draw_item(painter, next_item_rect, next_info, is_center=False)

        painter.end()

    def _draw_item(self, painter, rect, info, is_center):
        painter.save()

        # Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(info['bg_color'] if is_center else self.color_default_bg) # Only center has special bg
        painter.drawRoundedRect(rect.adjusted(2,2,-2,-2), 5, 5) # Small margin and rounding

        # Text
        # Dynamically adjust font size to fit, especially for neighbors
        base_font_size_roman = rect.height() * (0.33 if is_center else 0.28)
        base_font_size_quality = rect.height() * (0.17 if is_center else 0.14)

        roman_font = QFont(FONT_FAMILY, int(base_font_size_roman), QFont.Bold if is_center else QFont.Normal)
        quality_font = QFont(FONT_FAMILY, int(base_font_size_quality))
        
        painter.setPen(info['text_color'] if is_center else self.text_color_neighbor)
        
        text_flags = Qt.AlignCenter | Qt.TextWordWrap

        # Adjust font size for Roman numeral to fit width if too long
        painter.setFont(roman_font)
        fm_roman = QFontMetricsF(roman_font)
        text_width_roman = fm_roman.horizontalAdvance(info['roman_display'])
        if text_width_roman > rect.width() * 0.95: # If text wider than 95% of rect
            scale_factor_roman = (rect.width() * 0.95) / text_width_roman
            roman_font.setPointSizeF(roman_font.pointSizeF() * scale_factor_roman)
            painter.setFont(roman_font)

        if is_center:
            # For center item, quality text is below.
            roman_display_height_ratio = 0.63
            quality_display_height_ratio = 0.32

            roman_rect = QRectF(rect.x(), rect.y() + rect.height() * 0.05, rect.width(), rect.height() * roman_display_height_ratio)
            painter.drawText(roman_rect, text_flags, info['roman_display'])
            
            if info['quality_text']:
                painter.setFont(quality_font)
                fm_quality = QFontMetricsF(quality_font)
                text_width_quality = fm_quality.horizontalAdvance(info['quality_text'])
                if text_width_quality > rect.width() * 0.95:
                    scale_factor_quality = (rect.width() * 0.95) / text_width_quality
                    quality_font.setPointSizeF(quality_font.pointSizeF() * scale_factor_quality)
                    painter.setFont(quality_font)

                quality_rect = QRectF(rect.x(), rect.y() + rect.height() * (roman_display_height_ratio), 
                                      rect.width(), rect.height() * quality_display_height_ratio)
                painter.drawText(quality_rect, text_flags, info['quality_text'])
        else: # Neighbors - only Roman numeral
            painter.drawText(rect, text_flags, info['roman_display'])
            
        painter.restore()
