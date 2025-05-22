# Material Design Colors
MATERIAL_COLORS = {
    'primary': '#1976D2',  # Blue 700
    'primary_light': '#42A5F5',  # Blue 400
    'primary_dark': '#0D47A1',  # Blue 900
    'accent': '#FF4081',  # Pink A200
    'accent_light': '#FF80AB',  # Pink A100
    'accent_dark': '#F50057',  # Pink A400
    'background': '#303030',  # Dark Grey
    'surface': '#424242',  # Grey 800
    'error': '#B00020',  # Standard error color
    'text_primary': '#FFFFFF',  # White
    'text_secondary': '#B0BEC5',  # Blue Grey 200
    'divider': '#1F1F1F',  # Slightly lighter than background

    # Chord specific colors
    'chord_major': '#4CAF50',      # Green 500
    'chord_minor': '#AB47BC',      # Purple 400
    'chord_diminished': '#FFD54F', # Amber 300
    'chord_augmented': '#FF7043',  # Deep Orange 400
    
    'text_on_chord_major': '#FFFFFF',
    'text_on_chord_minor': '#FFFFFF',
    'text_on_chord_diminished': '#000000', # Black text for light yellow
    'text_on_chord_augmented': '#FFFFFF'
}

# Application-wide style sheets
APP_STYLE = """
    QMainWindow {
        background-color: """ + MATERIAL_COLORS['background'] + """;
        color: """ + MATERIAL_COLORS['text_primary'] + """;
    }
    QGroupBox {
        background-color: """ + MATERIAL_COLORS['surface'] + """;
        border: 1px solid #555555;
        border-radius: 5px;
        margin-top: 1ex;
        font-weight: bold;
        color: """ + MATERIAL_COLORS['text_primary'] + """;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 3px;
        color: """ + MATERIAL_COLORS['text_primary'] + """;
    }
    QLabel {
        color: """ + MATERIAL_COLORS['text_primary'] + """;
    }
    QCheckBox {
        color: """ + MATERIAL_COLORS['text_primary'] + """;
    }
    QPushButton {
        background-color: """ + MATERIAL_COLORS['primary'] + """;
        color: white;
        border-radius: 4px;
        padding: 6px;
        border: none;
    }
    QPushButton:hover {
        background-color: """ + MATERIAL_COLORS['primary_light'] + """;
    }
    QPushButton:pressed {
        background-color: """ + MATERIAL_COLORS['primary_dark'] + """;
    }
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: """ + MATERIAL_COLORS['surface'] + """;
    }
    QTabBar::tab {
        background-color: """ + MATERIAL_COLORS['background'] + """;
        color: """ + MATERIAL_COLORS['text_primary'] + """;
        padding: 8px 12px;
        border: 1px solid #555555;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: """ + MATERIAL_COLORS['surface'] + """;
        border-bottom: none;
    }
    QTabBar::tab:!selected {
        margin-top: 2px;
    }
    QScrollArea {
        background-color: transparent;
        border: none;
    }
    QScrollBar:vertical {
        background-color: """ + MATERIAL_COLORS['background'] + """;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: """ + MATERIAL_COLORS['primary'] + """;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background-color: """ + MATERIAL_COLORS['background'] + """;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: """ + MATERIAL_COLORS['primary'] + """;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""

# Font settings
FONT_FAMILY = "Roboto, Arial, sans-serif"
FONT_SIZES = {
    'small': 8,
    'normal': 10,
    'large': 12,
    'title': 14,
    'header': 16
}
