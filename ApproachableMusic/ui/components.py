from PyQt5.QtWidgets import (QFrame, QSlider, QDial, QCheckBox, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRectF, QPointF # Added pyqtSignal and QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetricsF, QPainterPath # Added QPainterPath
import math

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


class CircleOfFifthsWidget(QFrame):
    """Interactive widget that presents root notes and modes on concentric rings."""

    rootChanged = pyqtSignal(int)
    modeChanged = pyqtSignal(int)

    def __init__(self, notes, modes, parent=None):
        super().__init__(parent)
        self.notes = list(notes or [])
        self.modes = list(modes or [])

        self.root_order = self._build_root_order(self.notes)
        self.mode_order = list(self.modes)

        self._recalculate_steps()

        self.root_index = 0 if self.root_order else -1
        self.mode_index = 0 if self.mode_order else -1
        self.root_rotation = 0.0
        self.mode_rotation = 0.0
        self._base_angle = -math.pi / 2

        self._drag_active = None
        self._drag_start_angle = 0.0
        self._drag_start_rotation = 0.0
        self._dragged = False

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(260, 260)

        if self.root_order and self.notes:
            initial_circle_index = self.root_order.index(self.notes[0])
            self._set_circle_index('root', initial_circle_index, emit=False)
        if self.mode_order:
            self._set_circle_index('mode', 0, emit=False)

    def _recalculate_steps(self):
        self._root_step = (2 * math.pi / len(self.root_order)) if self.root_order else 0.0
        self._mode_step = (2 * math.pi / len(self.mode_order)) if self.mode_order else 0.0

    def _build_root_order(self, notes):
        if not notes:
            return []
        circle_order = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
        ordered = [note for note in circle_order if note in notes]
        for note in notes:
            if note not in ordered:
                ordered.append(note)
        return ordered

    def sizeHint(self):
        return self.minimumSize()

    def _ring_metrics(self):
        radius = min(self.width(), self.height()) / 2.0
        margin = 14.0
        outer_mode_radius = max(0.0, radius - margin)
        mode_ring_width = max(32.0, outer_mode_radius * 0.22)
        mode_inner_radius = max(0.0, outer_mode_radius - mode_ring_width)
        separation = 12.0
        root_outer_radius = max(0.0, mode_inner_radius - separation)
        root_ring_width = max(32.0, root_outer_radius * 0.28)
        root_inner_radius = max(0.0, root_outer_radius - root_ring_width)
        center_radius = max(0.0, root_inner_radius - separation / 2.0)
        return {
            'mode_outer': outer_mode_radius,
            'mode_inner': mode_inner_radius,
            'root_outer': root_outer_radius,
            'root_inner': root_inner_radius,
            'center': center_radius
        }

    def _create_ring_segment_path(self, center, outer_radius, inner_radius, start_angle_deg, span_angle_deg):
        outer_rect = QRectF(center.x() - outer_radius, center.y() - outer_radius,
                             outer_radius * 2.0, outer_radius * 2.0)
        inner_rect = QRectF(center.x() - inner_radius, center.y() - inner_radius,
                             inner_radius * 2.0, inner_radius * 2.0)
        path = QPainterPath()
        start_rad = math.radians(start_angle_deg)
        span_rad = math.radians(span_angle_deg)
        start_point = self._point_on_circle(center, outer_radius, start_rad)
        path.moveTo(start_point)
        path.arcTo(outer_rect, start_angle_deg, span_angle_deg)
        end_point = self._point_on_circle(center, inner_radius, start_rad + span_rad)
        path.lineTo(end_point)
        path.arcTo(inner_rect, start_angle_deg + span_angle_deg, -span_angle_deg)
        path.closeSubpath()
        return path

    def _point_on_circle(self, center, radius, angle):
        return QPointF(
            center.x() + math.cos(angle) * radius,
            center.y() + math.sin(angle) * radius
        )

    def _normalize_angle(self, angle):
        while angle <= -math.pi:
            angle += 2 * math.pi
        while angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def _set_circle_index(self, ring, circle_index, emit=True):
        if ring == 'root' and self.root_order:
            total = len(self.root_order)
            circle_index %= total
            changed = circle_index != self.root_index
            self.root_index = circle_index
            self.root_rotation = -self.root_index * self._root_step if self._root_step else 0.0
            self.update()
            if emit and changed and self.notes:
                self.rootChanged.emit(self.get_root_index())
        elif ring == 'mode' and self.mode_order:
            total = len(self.mode_order)
            circle_index %= total
            changed = circle_index != self.mode_index
            self.mode_index = circle_index
            self.mode_rotation = -self.mode_index * self._mode_step if self._mode_step else 0.0
            self.update()
            if emit and changed and self.modes:
                self.modeChanged.emit(self.get_mode_index())

    def _set_rotation_for_ring(self, ring, rotation, snap=False, emit=True):
        rotation = self._normalize_angle(rotation)
        if ring == 'root' and self.root_order:
            self.root_rotation = rotation
            index = 0
            if self._root_step:
                index = int(round((-self.root_rotation) / self._root_step)) % len(self.root_order)
            changed = index != self.root_index
            self.root_index = index
            if snap:
                self.root_rotation = -self.root_index * self._root_step if self._root_step else 0.0
            self.update()
            if emit and changed and self.notes:
                self.rootChanged.emit(self.get_root_index())
        elif ring == 'mode' and self.mode_order:
            self.mode_rotation = rotation
            index = 0
            if self._mode_step:
                index = int(round((-self.mode_rotation) / self._mode_step)) % len(self.mode_order)
            changed = index != self.mode_index
            self.mode_index = index
            if snap:
                self.mode_rotation = -self.mode_index * self._mode_step if self._mode_step else 0.0
            self.update()
            if emit and changed and self.modes:
                self.modeChanged.emit(self.get_mode_index())

    def get_root_index(self):
        if not self.notes or self.root_index < 0 or not self.root_order:
            return 0
        note = self.root_order[self.root_index % len(self.root_order)]
        return self.notes.index(note) if note in self.notes else 0

    def get_mode_index(self):
        if not self.modes or self.mode_index < 0 or not self.mode_order:
            return 0
        mode_name = self.mode_order[self.mode_index % len(self.mode_order)]
        return self.modes.index(mode_name) if mode_name in self.modes else 0

    def get_root_name(self):
        if not self.root_order or self.root_index < 0:
            return ''
        return self.root_order[self.root_index % len(self.root_order)]

    def get_mode_name(self):
        if not self.mode_order or self.mode_index < 0:
            return ''
        return self.mode_order[self.mode_index % len(self.mode_order)]

    def set_root_index(self, note_index, emit=True):
        if not self.notes or not self.root_order:
            return
        note_index %= len(self.notes)
        target_note = self.notes[note_index]
        if target_note in self.root_order:
            circle_index = self.root_order.index(target_note)
            self._set_circle_index('root', circle_index, emit=emit)

    def set_root_name(self, note_name, emit=True):
        if note_name in self.notes:
            self.set_root_index(self.notes.index(note_name), emit=emit)

    def set_mode_index(self, mode_index, emit=True):
        if not self.modes or not self.mode_order:
            return
        mode_index %= len(self.modes)
        target_mode = self.modes[mode_index]
        if target_mode in self.mode_order:
            circle_index = self.mode_order.index(target_mode)
            self._set_circle_index('mode', circle_index, emit=emit)

    def set_mode_name(self, mode_name, emit=True):
        if mode_name in self.modes:
            self.set_mode_index(self.modes.index(mode_name), emit=emit)

    def rotate_root(self, steps=1):
        if self.root_order:
            new_index = (self.root_index + steps) % len(self.root_order)
            self._set_circle_index('root', new_index)

    def rotate_mode(self, steps=1):
        if self.mode_order:
            new_index = (self.mode_index + steps) % len(self.mode_order)
            self._set_circle_index('mode', new_index)

    def _ring_at_position(self, pos):
        metrics = self._ring_metrics()
        center = self.rect().center()
        distance = math.hypot(pos.x() - center.x(), pos.y() - center.y())
        if metrics['root_inner'] <= distance <= metrics['root_outer']:
            return 'root'
        if metrics['mode_inner'] <= distance <= metrics['mode_outer']:
            return 'mode'
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            ring = self._ring_at_position(event.pos())
            if ring:
                self.setFocus()
                self._drag_active = ring
                self._drag_start_angle = math.atan2(
                    event.pos().y() - self.rect().center().y(),
                    event.pos().x() - self.rect().center().x()
                )
                self._drag_start_rotation = self.root_rotation if ring == 'root' else self.mode_rotation
                self._dragged = False
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active:
            center = self.rect().center()
            current_angle = math.atan2(event.pos().y() - center.y(), event.pos().x() - center.x())
            delta = self._normalize_angle(current_angle - self._drag_start_angle)
            if abs(delta) > 0.005:
                self._dragged = True
            new_rotation = self._drag_start_rotation + delta
            self._set_rotation_for_ring(self._drag_active, new_rotation, snap=False)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_active and event.button() == Qt.LeftButton:
            center = self.rect().center()
            angle = math.atan2(event.pos().y() - center.y(), event.pos().x() - center.x())
            ring = self._drag_active
            if not self._dragged:
                index = self._index_from_angle(ring, angle)
                self._set_circle_index(ring, index)
            else:
                current_rotation = self.root_rotation if ring == 'root' else self.mode_rotation
                self._set_rotation_for_ring(ring, current_rotation, snap=True)
            self._drag_active = None
            self._dragged = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _index_from_angle(self, ring, angle):
        if ring == 'root' and self.root_order and self._root_step:
            relative = self._normalize_angle(angle - self._base_angle - self.root_rotation)
            return int(round(relative / self._root_step)) % len(self.root_order)
        if ring == 'mode' and self.mode_order and self._mode_step:
            relative = self._normalize_angle(angle - self._base_angle - self.mode_rotation)
            return int(round(relative / self._mode_step)) % len(self.mode_order)
        return 0

    def keyPressEvent(self, event):
        handled = False
        if event.key() in (Qt.Key_Left, Qt.Key_A):
            self.rotate_root(-1)
            handled = True
        elif event.key() in (Qt.Key_Right, Qt.Key_D):
            self.rotate_root(1)
            handled = True
        elif event.key() in (Qt.Key_Up, Qt.Key_W):
            self.rotate_mode(-1)
            handled = True
        elif event.key() in (Qt.Key_Down, Qt.Key_S):
            self.rotate_mode(1)
            handled = True

        if handled:
            event.accept()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()
        metrics = self._ring_metrics()

        surface_color = QColor(MATERIAL_COLORS.get('surface', '#424242'))
        background_color = QColor(MATERIAL_COLORS.get('background', '#303030'))
        divider_color = QColor(MATERIAL_COLORS.get('divider', '#1F1F1F'))
        primary_color = QColor(MATERIAL_COLORS.get('primary', '#1976D2'))
        accent_color = QColor(MATERIAL_COLORS.get('accent', '#FF4081'))
        text_primary = QColor(MATERIAL_COLORS.get('text_primary', '#FFFFFF'))
        text_secondary = QColor(MATERIAL_COLORS.get('text_secondary', '#B0BEC5'))

        painter.setPen(Qt.NoPen)
        painter.setBrush(background_color)
        painter.drawEllipse(center, metrics['mode_outer'], metrics['mode_outer'])

        mode_base = surface_color
        root_base = surface_color.darker(115)

        self._draw_ring(
            painter,
            labels=self.mode_order,
            rotation=self.mode_rotation,
            inner_radius=metrics['mode_inner'],
            outer_radius=metrics['mode_outer'],
            selected_index=self.mode_index,
            highlight_color=accent_color,
            base_color=mode_base,
            text_color=text_secondary,
            highlight_text_color=text_primary,
            divider_color=divider_color,
            font_ratio=0.32,
            bold=False
        )

        self._draw_ring(
            painter,
            labels=self.root_order,
            rotation=self.root_rotation,
            inner_radius=metrics['root_inner'],
            outer_radius=metrics['root_outer'],
            selected_index=self.root_index,
            highlight_color=primary_color,
            base_color=root_base,
            text_color=text_secondary,
            highlight_text_color=text_primary,
            divider_color=divider_color,
            font_ratio=0.42,
            bold=True
        )

        painter.setBrush(background_color)
        painter.drawEllipse(center, metrics['center'], metrics['center'])

        painter.end()

    def _draw_ring(self, painter, labels, rotation, inner_radius, outer_radius,
                   selected_index, highlight_color, base_color, text_color,
                   highlight_text_color, divider_color, font_ratio, bold):
        if not labels or outer_radius <= inner_radius:
            return

        step = (2 * math.pi) / len(labels)
        center = self.rect().center()
        ring_pen = QPen(divider_color)
        ring_pen.setWidthF(max(1.0, (outer_radius - inner_radius) * 0.05))

        for i, label in enumerate(labels):
            mid_angle = self._base_angle + rotation + i * step
            start_angle = mid_angle - step / 2.0
            start_deg = math.degrees(start_angle)
            span_deg = math.degrees(step)

            path = self._create_ring_segment_path(center, outer_radius, inner_radius, start_deg, span_deg)

            painter.save()
            painter.setPen(ring_pen)
            painter.setBrush(QBrush(highlight_color if i == selected_index else base_color))
            painter.drawPath(path)
            painter.restore()

            text_radius = (outer_radius + inner_radius) / 2.0
            text_x = center.x() + math.cos(mid_angle) * text_radius
            text_y = center.y() + math.sin(mid_angle) * text_radius

            font = QFont(FONT_FAMILY, 10)
            font.setBold(bold)
            font.setPointSizeF(max(8.0, (outer_radius - inner_radius) * font_ratio))

            painter.save()
            painter.setFont(font)
            painter.setPen(highlight_text_color if i == selected_index else text_color)
            metrics = QFontMetricsF(font)
            text_rect = metrics.boundingRect(label)
            label_rect = QRectF(
                text_x - text_rect.width() / 2.0,
                text_y - text_rect.height() / 2.0,
                text_rect.width(),
                text_rect.height()
            )
            painter.drawText(label_rect, Qt.AlignCenter, label)
            painter.restore()
