# Approachable Music Generator

## Overview

The Approachable Music Generator is a Python-based desktop application designed for musicians, composers, and hobbyists to experiment with chord progressions, sound design, and music theory concepts in an interactive way. It features a modern graphical user interface built with PyQt5, allowing users to select root notes and modes, generate diatonic chords, and customize multiple synthesized voices to create rich soundscapes. The application includes real-time audio visualization tools like a spectrum analyzer and a waveform visualizer.

## Key Features

*   **Diatonic Chord Progression:**
    *   Select a root note (C, C#, D, etc.) and a musical mode (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian).
    *   Automatically generates and displays the 7 diatonic chords for the selected key and mode.
    *   Play chords individually, with options to shift their octave up or down.
*   **Advanced Voicing Control:**
    *   Toggle individual degrees (1st, 3rd, 5th, 7th, 9th, 11th, 13th) for each of the 7 diatonic chords to customize their voicing.
*   **Multi-Voice Synthesis Engine:**
    *   Four distinct waveform voices: Sine, Square, Sawtooth, and Triangle.
    *   Independent controls for each voice:
        *   **Enable/Disable:** Toggle voices on or off.
        *   **Volume:** Adjust the amplitude of the voice.
        *   **Duration:** Set the length of the note.
        *   **Delay:** Introduce a pre-delay before the note sounds.
        *   **Fade In/Out:** Control the attack and release times of the note's envelope.
*   **Preset Management:**
    *   Save and load custom voice configurations as presets.
    *   Create new presets, delete existing ones, or reset to default templates.
    *   Presets are stored in a `presets.json` file located within the `ApproachableMusic` directory, making them portable with the application folder. Includes "Default", "Bright", "Soft", and "Punchy" templates.
*   **Interactive UI & Visualization:**
    *   **Root Note & Mode Selection:** Intuitive rotary dials for selecting the musical root and mode.
    *   **Octave Control:** Spinbox to set the base octave for chord playback.
    *   **Spectrum Analyzer:** Real-time frequency spectrum display of the output audio.
        *   Adjustable dynamic range (dB).
        *   Adjustable minimum and maximum frequency display.
    *   **Waveform Visualizer:** Shows the shape of the combined output waveform.
    *   **Master Audio Settings:** Control for interruption fade-out duration when playback is stopped.
*   **Modern Interface:**
    *   Styled with a clean, material-inspired theme.
    *   Custom UI components for a polished user experience.

## File Structure

The `ApproachableMusic` project is organized as follows:

```
ApproachableMusic/
├── final_music_generator.py  # Main application script, launches the UI and handles logic.
├── presets.py                # Manages loading, saving, and handling of voice presets.
├── presets.json              # (Auto-generated) Stores user-defined and default voice presets.
├── README.md                 # This file.
├── ui/                         # Directory for UI-related modules.
│   ├── components.py           # Custom PyQt5 widgets (MaterialCard, ModernSlider, etc.).
│   ├── spectrum_analyzer.py    # Spectrum analyzer widget.
│   ├── theme.py                # Styling constants, color palettes, and global app style.
│   └── waveform_visualizer.py  # Waveform visualizer widget.
└── utils/                      # Directory for utility functions and data.
    └── audio_utils.py          # Core audio generation functions, note/mode definitions,
                                # musical constants (NOTES, MODES, WAVEFORMS, etc.).
```

## Prerequisites

To run the Approachable Music Generator, you need Python 3 and the following libraries:

*   **PyQt5:** For the graphical user interface.
    *   `pip install PyQt5`
*   **NumPy:** For numerical operations, especially array manipulation for audio data.
    *   `pip install numpy`
*   **PyAudio:** For audio playback.
    *   `pip install pyaudio`
    (Note: PyAudio installation might require system dependencies like `portaudio`. Refer to PyAudio documentation for platform-specific installation instructions if you encounter issues.)

## How to Run

1.  Ensure all prerequisites are installed.
2.  Navigate to the directory containing the `ApproachableMusic` folder in your terminal.
3.  Run the main application script:
    ```bash
    python ApproachableMusic/final_music_generator.py
    ```

## How to Use

1.  **Set the Musical Context:**
    *   Use the "Root Note" dial to select the tonic of your scale (e.g., C, G, F#).
    *   Use the "Octave" spinbox to set the base octave for the chords.
    *   Use the "Mode" dial to select the desired musical mode (e.g., Ionian for major, Aeolian for natural minor).
    *   The seven chord buttons below will update to reflect the diatonic chords of the selected key and mode, showing their root, quality (e.g., "Cmaj", "Dmin"), and Roman numeral.

2.  **Play Chords:**
    *   Click any of the seven main chord buttons (labeled "Chord 1" through "Chord 7") to play the corresponding chord.
    *   Use the small "-" and "+" buttons next to each main chord button to play the chord an octave lower or higher, respectively.

3.  **Customize Chord Voicings:**
    *   Below each main chord button are checkboxes for "1", "3", "5" (top row) and "7", "9", "11", "13" (bottom row).
    *   Check or uncheck these to include or exclude specific diatonic degrees when that chord is played. For example, unchecking "3" for a major chord will remove its third. Checking "7" will add the diatonic seventh.

4.  **Adjust Voice Parameters (Sound Design):**
    *   The "Voice Controls" section contains tabs for each waveform (Sine, Square, Sawtooth, Triangle).
    *   Select a tab to adjust its parameters:
        *   **Enable:** Check to include this waveform in the sound.
        *   **Volume:** Control the loudness of this specific waveform.
        *   **Duration:** Set how long notes from this voice will last.
        *   **Delay:** Add a delay before this voice sounds.
        *   **Fade In/Out:** Adjust the attack and release envelope.
        *   **Test:** Play a test note (A4) using only the current voice's settings.
    *   Changes to these parameters affect all subsequently played chords.
    *   The "Waveform Visualizer" (top right) will update to show a representation of the combined enabled voices' shapes.

5.  **Manage Presets:**
    *   The "Preset" dropdown in the "Voice Controls" section allows you to manage voice settings configurations.
    *   **Load:** Select a preset from the dropdown to apply its settings to all voices.
    *   **Save:**
        *   If you want to save the current voice settings under the currently selected preset name (and it's not "Default"), click "Save" and confirm overwrite.
        *   To save as a new preset, type a new name in the editable combo box (or select "Default" then type a new name) and click "Save", then enter the name in the dialog.
    *   **New:** Click "New" to create a new preset. You'll be prompted for a name, and it will be initialized with default voice settings.
    *   **Delete:** Select a preset (other than "Default") and click "Delete" to remove it.

6.  **Visualizers & Master Settings:**
    *   **Spectrum Analyzer (Top Left):** Shows the real-time frequency content of the audio.
        *   Adjust "Spectrum Range (dB)", "Spectrum Min Freq (Hz)", and "Spectrum Max Freq (Hz)" sliders in the "Master Audio Settings" card to customize the analyzer's display.
    *   **Waveform Visualizer (Top Right):** Displays the general shape of the combined active waveforms.
    *   **Interruption Fade (Master Audio Settings):** Sets how quickly the sound fades out if you play a new chord while another is still sounding.

## Preset System Explained

*   The application uses a `presets.json` file to store all voice presets.
*   This file is automatically created in the `ApproachableMusic` directory (the same directory as `presets.py`) if it doesn't exist when the application starts. It will be initialized with "Default", "Bright", "Soft", and "Punchy" presets.
*   Because `presets.json` is stored relative to the application's code, the entire `ApproachableMusic` folder (including your saved presets) can be moved to different locations or shared with others, and the presets will remain accessible.

---

Enjoy exploring music with the Approachable Music Generator!
