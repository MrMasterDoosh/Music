import numpy as np
import random
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QPoint, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QImage

from .theme import MATERIAL_COLORS, FONT_FAMILY

class SpectrumAnalyzer(QWidget):
    """A spectrum analyzer widget that visualizes audio frequencies"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Spectrum data
        self.spectrum_data = np.zeros(256) # Increased number of particles/bands
        self.peak_data = np.zeros(256)     # Increased number of particles/bands
        self.peak_decay_rate = 0.03
        self.current_sample_rate = 44100
        self.min_freq_display = 20.0
        self.max_freq_display = self.current_sample_rate / 2.0
        self.smoothing_window_size = 4
        
        # Morphing Particle Animation
        self.num_particles = len(self.spectrum_data)
        self.particle_spectrum_target_pos = np.zeros((self.num_particles, 2), dtype=float)
        self.particle_salik_target_pos = np.zeros((self.num_particles, 2), dtype=float)
        self.particle_current_pos = np.zeros((self.num_particles, 2), dtype=float)
        
        self.spectrum_particle_color = QColor(MATERIAL_COLORS['primary'])
        self.salik_particle_color = QColor(MATERIAL_COLORS['primary_light'])
        self.particle_render_size = 4 
        self.base_particle_render_size = 4 # Store base size for pulsing
        self.pulse_animation_step = 0.0
        self.pulse_amplitude = 1.5 # Max additional size for pulsing particles (radius change)
        self.pulse_speed = 0.05 # Slower pulse

        # Idle state & transition (morph progress)
        self.idle_timeout_frames = 60 # Define before use
        self.idle_state = "idle"  # Start in idle state
        self.frames_since_last_audio = self.idle_timeout_frames + 1 # Ensure it's considered idle initially
        self.transition_alpha = 1.0 # Start with SALIK fully visible
        self.transition_frames_total = 40 
        self.current_transition_frame_count = self.transition_frames_total # Start as if transition to SALIK just finished
        
        self._salik_points_calculated = False
        self._base_particle_salik_target_pos = np.zeros((self.num_particles, 2), dtype=float)
        self._salik_formation_width = 0 # Width of the SALIK text formation
        self.salik_scroll_offset_x = 0.0
        self.salik_scroll_speed = -0.75 # Pixels per frame for scrolling SALIK

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30) 
        
        self.animation_step = 0
        self.dynamic_range_db = 80.0

        self._initialize_particle_x_and_salik_targets()


    def _initialize_particle_x_and_salik_targets(self):
        # Initial call, width/height might be default, will be updated by resizeEvent
        width = self.width() if self.width() > 0 else 600 # Default guess
        height = self.height() if self.height() > 0 else 150 
        self._update_particle_spectrum_target_x(width) # Calculate spectrum X targets
        self._calculate_salik_target_points(width, height) # Calculate base SALIK targets

        # Initialize current positions based on initial state (SALIK visible)
        if self._salik_points_calculated:
            # Start with SALIK centered, scroll will apply in _tick
            self.particle_current_pos = np.copy(self._base_particle_salik_target_pos)
            # If starting scrolled, apply initial offset:
            # self.particle_current_pos[:, 0] += self.salik_scroll_offset_x 
        else: # Fallback if SALIK points not ready
            self.particle_current_pos = np.copy(self.particle_spectrum_target_pos)
        
        # If starting idle, ensure particle_spectrum_target_pos Y is at baseline
        self.particle_spectrum_target_pos[:, 1] = height


    def _update_particle_spectrum_target_x(self, current_width):
        """Calculates X positions for particles in spectrum mode."""
        if self.num_particles > 0:
            # Distribute particles across the width, centered in their 'band'
            particle_spacing = current_width / self.num_particles
            self.particle_spectrum_target_pos[:, 0] = np.linspace(
                particle_spacing / 2,
                current_width - (particle_spacing / 2),
                self.num_particles
            )

    def _calculate_salik_target_points(self, current_width, current_height):
        """Generates target points for particles to form 'SALIK' text."""
        if current_width <= 0 or current_height <= 0:
            self._salik_points_calculated = False
            return

        text = "SALIK"
        font_size = max(10, int(current_height * 0.6)) # Adjust font size based on height
        font = QFont(FONT_FAMILY, font_size, QFont.Bold)

        # Create an image to render text onto
        image = QImage(current_width, current_height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height() # ascent + descent

        # Calculate position to center the text
        x_text = (current_width - text_width) / 2
        y_text = (current_height - text_height) / 2 + metrics.ascent() # Baseline for drawText

        painter.setPen(Qt.white) # Draw text in white to find pixels
        painter.drawText(int(x_text), int(y_text), text)
        painter.end()

        salik_pixels = []
        for y_img in range(current_height):
            for x_img in range(current_width):
                if image.pixelColor(x_img, y_img).alpha() > 0: # Check if pixel is part of the text
                    salik_pixels.append((x_img, y_img))
        
        if not salik_pixels: # No text pixels found (e.g., if font is too small or color issue)
            # Fallback: distribute particles in a horizontal line in the middle
            ys = np.full(self.num_particles, current_height / 2)
            xs = np.linspace(current_width * 0.1, current_width * 0.9, self.num_particles)
            self.particle_salik_target_pos = np.column_stack((xs, ys))
            self._salik_points_calculated = False # Indicate fallback
            return

        # Assign target points to particles
        if len(salik_pixels) >= self.num_particles:
            chosen_pixels = random.sample(salik_pixels, self.num_particles)
        else:
            chosen_pixels = [salik_pixels[i % len(salik_pixels)] for i in range(self.num_particles)]
            random.shuffle(chosen_pixels) 

        self._base_particle_salik_target_pos = np.array(chosen_pixels, dtype=float)
        self._salik_points_calculated = True
        
        if self._base_particle_salik_target_pos.shape[0] > 0 and len(salik_pixels) > 0:
             min_x_text = np.min(self._base_particle_salik_target_pos[:, 0])
             max_x_text = np.max(self._base_particle_salik_target_pos[:, 0])
             self._salik_formation_width = max_x_text - min_x_text
        else: # Fallback if no text pixels were found or not enough particles
            self._salik_formation_width = current_width * 0.5 # Estimate

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        width = self.width()
        height = self.height()
        self._update_particle_spectrum_target_x(width)
        self._calculate_salik_target_points(width, height)
        # Re-interpolate current positions based on new targets and current alpha
        alpha = self.transition_alpha
        
        current_salik_targets_for_resize = np.copy(self._base_particle_salik_target_pos)
        if self._salik_points_calculated:
            current_salik_targets_for_resize[:, 0] += self.salik_scroll_offset_x
            # Apply wrapping for particles that might have scrolled off during resize calculation
            # This is complex as the text itself might resize. Simpler to let _tick handle final pos.
            # For now, just use the current scroll offset.

        self.particle_current_pos = (1 - alpha) * self.particle_spectrum_target_pos + \
                                    alpha * current_salik_targets_for_resize
        self.update()

    def set_dynamic_range(self, db_value):
        """Sets the dynamic range for the spectrum display."""
        self.dynamic_range_db = float(db_value)
        self.update()

    def set_display_frequency_range(self, min_hz, max_hz):
        """Sets the minimum and maximum frequency to display on the X-axis."""
        min_hz = float(min_hz)
        max_hz = float(max_hz)

        nyquist = self.current_sample_rate / 2.0 if self.current_sample_rate > 0 else 22050.0

        # Basic validation
        if min_hz < 0: min_hz = 0
        if max_hz <= min_hz: max_hz = min_hz + 100 # Ensure max is greater than min
        
        self.min_freq_display = max(0, min_hz) # Cannot be less than 0
        self.max_freq_display = min(max_hz, nyquist) # Cannot exceed Nyquist

        if self.min_freq_display >= self.max_freq_display: # If still invalid after clamping
            self.min_freq_display = max(0, self.max_freq_display - 100) # Ensure some range

        self.update() # Trigger repaint

    @pyqtSlot(np.ndarray, int)
    def update_spectrum(self, samples, sample_rate):
        """Update the spectrum data from audio samples. samples should be float32, normalized -1 to 1."""
        self.current_sample_rate = sample_rate
        self.frames_since_last_audio = 0

        if self.idle_state == "playing":
            pass
        elif self.idle_state == "idle": 
            self.idle_state = "fading_to_playing"
            self.current_transition_frame_count = 0 
        elif self.idle_state == "fading_to_idle": 
            current_progress_to_idle = self.transition_alpha 
            self.idle_state = "fading_to_playing"
            self.current_transition_frame_count = int((1.0 - current_progress_to_idle) * self.transition_frames_total)
        elif self.idle_state == "fading_to_playing":
            pass
        
        if samples is None or len(samples) == 0:
            # Update spectrum Y targets to zero if no samples (or keep last known?)
            # For now, let's make them go to baseline (height)
            self.particle_spectrum_target_pos[:, 1] = self.height()
            # self.spectrum_data = np.zeros(self.num_particles) # Keep spectrum_data zero
            # self.peak_data = np.zeros(self.num_particles)
            # No actual audio, so don't update spectrum_data from it.
            # The idle state machine will take over.
            return

        # Calculate FFT (existing logic largely okay)
        n = len(samples)
        if n > 0:
            # Ensure samples are float type for FFT
            samples_float = samples.astype(np.float32)

            # Apply a Hann window to the samples to reduce spectral leakage
            if n > 1: # Hann window requires at least 2 samples
                window = np.hanning(n)
                samples_windowed = samples_float * window
            else:
                samples_windowed = samples_float # Not enough samples to window
            
            fft_raw_magnitudes = np.abs(np.fft.rfft(samples_windowed))
            
            # Normalize FFT magnitudes so that a full-scale sine wave at a bin frequency corresponds to magnitude 1.0
            # For rfft, the sum of squares of rfft output (excluding DC and Nyquist if present) is N/2 * sum of squares of input.
            # A full scale sine (amplitude 1) has power 0.5. Its rfft bin would have magnitude N/2.
            # So, divide by N/2 to get magnitudes in [0,1] range for components.
            if n > 0:
                normalized_fft_magnitudes = fft_raw_magnitudes / (n / 2.0)
            else:
                normalized_fft_magnitudes = fft_raw_magnitudes # Should not happen if n > 0 check passed

            # Convert to dBFS (decibels relative to full scale)
            # 0 dBFS will correspond to a magnitude of 1.0 (full-scale sine)
            db_values = 20 * np.log10(normalized_fft_magnitudes + 1e-10) # Add epsilon to avoid log(0)
            
            # Scale to 0-1 range based on a chosen dynamic range
            # For example, if self.dynamic_range_db is 80, we map -80 dBFS to 0 dBFS into the 0-1 range.
            
            # Values below -self.dynamic_range_db will be 0, 0 dBFS will be 1.
            # Ensure self.dynamic_range_db is not zero to avoid division by zero
            current_dynamic_range = self.dynamic_range_db if self.dynamic_range_db > 0 else 80.0
            scaled_db_values = (db_values + current_dynamic_range) / current_dynamic_range
            scaled_db_values = np.clip(scaled_db_values, 0, 1)
            
            # Resample/map FFT bins to display bands
            num_display_bands = self.num_particles
            processed_bands = np.zeros(num_display_bands)

            if n > 0 and self.current_sample_rate > 0:
                all_fft_frequencies = np.fft.rfftfreq(n, 1.0 / self.current_sample_rate)
                all_fft_frequencies = all_fft_frequencies[:len(scaled_db_values)]

                start_fft_idx = np.searchsorted(all_fft_frequencies, self.min_freq_display, side='left')
                end_fft_idx = np.searchsorted(all_fft_frequencies, self.max_freq_display, side='right')
                
                source_values_for_display = scaled_db_values[start_fft_idx:end_fft_idx]

                if len(source_values_for_display) > 0:
                    if len(source_values_for_display) >= num_display_bands:
                        for i in range(num_display_bands):
                            s_idx = int(i * len(source_values_for_display) / num_display_bands)
                            e_idx = int((i + 1) * len(source_values_for_display) / num_display_bands)
                            if s_idx < e_idx:
                                processed_bands[i] = np.mean(source_values_for_display[s_idx:e_idx])
                            elif s_idx < len(source_values_for_display):
                                processed_bands[i] = source_values_for_display[s_idx]
                    else:
                        xp = np.linspace(0, num_display_bands - 1, num=len(source_values_for_display), endpoint=True)
                        fp = source_values_for_display
                        x_interp = np.arange(num_display_bands)
                        processed_bands = np.interp(x_interp, xp, fp)
            
            self.spectrum_data = processed_bands
            self.peak_data = np.maximum(self.peak_data, self.spectrum_data)

            # Update particle Y targets for spectrum mode
            if self.height() > 0: # Ensure height is valid
                # Apply smoothing before setting particle targets
                if self.smoothing_window_size > 1 and len(self.spectrum_data) >= self.smoothing_window_size:
                    pad_width = self.smoothing_window_size // 2
                    padded_data = np.pad(self.spectrum_data, pad_width, mode='edge')
                    smoothed_data_for_particles = np.convolve(padded_data, np.ones(self.smoothing_window_size)/self.smoothing_window_size, mode='valid')
                else:
                    smoothed_data_for_particles = self.spectrum_data
                
                # Ensure smoothed_data_for_particles has the correct length
                if len(smoothed_data_for_particles) != self.num_particles:
                     # Fallback or error handling if lengths don't match (e.g., use unsmoothed or zeros)
                     # This might happen if spectrum_data length changes unexpectedly, though it's fixed by num_particles
                     if len(self.spectrum_data) == self.num_particles:
                         smoothed_data_for_particles = self.spectrum_data
                     else: # Should not happen if self.spectrum_data is always self.num_particles
                         smoothed_data_for_particles = np.zeros(self.num_particles)


                scaled_values = smoothed_data_for_particles**0.6 # Visual scaling
                self.particle_spectrum_target_pos[:, 1] = self.height() - (scaled_values * self.height() * 0.9)
    
    def _tick(self):
        """Called by the timer to handle time-based updates like peak decay and animation."""
        if self.idle_state == "playing":
            self.frames_since_last_audio += 1
            if self.frames_since_last_audio > self.idle_timeout_frames:
                self.idle_state = "fading_to_idle"
                self.current_transition_frame_count = 0 
        elif self.idle_state == "fading_to_idle": # Morphing to SALIK
            self.current_transition_frame_count += 1
            self.transition_alpha = min(1.0, self.current_transition_frame_count / self.transition_frames_total)
            if self.transition_alpha >= 1.0:
                self.idle_state = "idle"
        elif self.idle_state == "fading_to_playing": # Morphing to Spectrum
            self.current_transition_frame_count += 1
            self.transition_alpha = 1.0 - min(1.0, self.current_transition_frame_count / self.transition_frames_total)
            if self.transition_alpha <= 0.0:
                self.transition_alpha = 0.0
                self.idle_state = "playing"
        elif self.idle_state == "idle": # Fully SALIK
            self.transition_alpha = 1.0
            self.pulse_animation_step += self.pulse_speed
            self.salik_scroll_offset_x += self.salik_scroll_speed
            
            # Scrolling wrap-around logic
            # Consider the text formation width and widget width
            # When the leftmost part of the text (original position + scroll) is off-screen left,
            # and the rightmost part is also off-screen left, reset.
            # A simpler way: if scroll_offset makes the whole text move by its width + widget_width margin
            text_effective_width = self._salik_formation_width if self._salik_formation_width > 0 else self.width() * 0.5
            if self.salik_scroll_offset_x < -(text_effective_width + self.width() * 0.1): # Allow some margin
                 self.salik_scroll_offset_x = self.width() # Reset to come from the right

        # Interpolate particle positions
        alpha = self.transition_alpha
        current_salik_targets = np.copy(self._base_particle_salik_target_pos)

        if self._salik_points_calculated:
            current_salik_targets[:, 0] += self.salik_scroll_offset_x
            # Particle-level wrapping for scrolling SALIK text
            # This ensures individual particles wrap around correctly.
            if self.idle_state == "idle" or self.idle_state == "fading_to_idle":
                 # Width of the widget
                widget_width = self.width()
                # Effective width of the SALIK text formation (can be estimated or calculated)
                # For simplicity, let's use a large boundary for wrapping individual particles
                # This is tricky because the _base_particle_salik_target_pos is centered.
                # The scroll_offset_x moves the whole group.
                # A particle's effective X is its base X + scroll_offset_x.
                # If this effective X < 0, it should wrap to widget_width + (base X + scroll_offset_x)
                # This needs to be done carefully to avoid visual glitches.
                # A simpler approach for group scrolling is to draw the group multiple times if it spans edges.
                # For now, the group scroll_offset_x handles the main movement.
                pass


        if self._salik_points_calculated:
             self.particle_current_pos = (1 - alpha) * self.particle_spectrum_target_pos + \
                                        alpha * current_salik_targets
        else: 
            self.particle_current_pos = np.copy(self.particle_spectrum_target_pos)


        self.peak_data = self.peak_data * (1 - self.peak_decay_rate) 
        self.animation_step = (self.animation_step + 1) % 360 
        self.update()

    def paintEvent(self, event):
        """Paint the spectrum analyzer with morphing particles."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        try:
            width = self.width()
            height = self.height()
            
            painter.fillRect(0, 0, width, height, QColor(MATERIAL_COLORS['background']))

            fading_elements_opacity = 1.0 - self.transition_alpha

            if fading_elements_opacity > 0.01: 
                painter.setOpacity(fading_elements_opacity)
                # Draw grid lines (unchanged)
                grid_color = QColor(60, 60, 60)
                painter.setPen(QPen(grid_color, 1))
                for i in range(1, 10):
                    y_grid = int(height * i / 10) 
                    painter.drawLine(0, y_grid, width, y_grid)
                num_v_grid_lines = 6
                if num_v_grid_lines > 0:
                    for i in range(1, num_v_grid_lines):
                        x_grid = int(width * i / num_v_grid_lines)
                        painter.drawLine(x_grid, 0, x_grid, height)
                
                # Draw frequency labels
                label_color = QColor(MATERIAL_COLORS['text_secondary'])
                painter.setPen(QPen(label_color, 1))
                painter.setFont(QFont(FONT_FAMILY, 8))
                if num_v_grid_lines > 0 and self.max_freq_display > self.min_freq_display:
                    for i in range(num_v_grid_lines + 1): 
                        freq_val = self.min_freq_display + (i / num_v_grid_lines) * (self.max_freq_display - self.min_freq_display)
                        x_pos = (i / num_v_grid_lines) * width
                        if freq_val < 1: label_text = f"{freq_val:.2f}Hz"
                        elif freq_val < 1000: label_text = f"{freq_val:.0f}Hz"
                        else: label_text = f"{freq_val/1000:.1f}k".replace(".0k","k")
                        
                        text_metrics = painter.fontMetrics()
                        text_w = text_metrics.horizontalAdvance(label_text)
                        draw_x = x_pos
                        if i == 0: draw_x = x_pos
                        elif i == num_v_grid_lines: draw_x = x_pos - text_w
                        else: draw_x = x_pos - text_w / 2
                        draw_x = max(0, min(width - text_w - 2, draw_x))
                        painter.drawText(int(draw_x), height - 5, label_text)
                    
                # Draw title
                title_color = QColor(MATERIAL_COLORS['text_primary'])
                painter.setPen(QPen(title_color, 1))
                painter.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))
                painter.drawText(10, 20, "Spectrum Analyzer")
                
                # Draw animated wave at the bottom
                wave_color = QColor(MATERIAL_COLORS['accent'])
                painter.setPen(QPen(wave_color, 1.5))
                wave_points = [] 
                for x_wave_coord in range(0, width, 4): 
                    y_wave_coord = height - 10 + 5 * np.sin((x_wave_coord / 50) + (self.animation_step / 10)) 
                    wave_points.append(QPointF(x_wave_coord, y_wave_coord)) # Use QPointF
                if len(wave_points) > 1:
                    painter.drawPolyline(wave_points) # QPainter can take list of QPointF
                
                painter.setOpacity(1.0) # Reset opacity

            # Draw Particles
            r_spec, g_spec, b_spec, _ = self.spectrum_particle_color.getRgb()
            r_salik, g_salik, b_salik, _ = self.salik_particle_color.getRgb()

            alpha_interp = self.transition_alpha
            curr_r = int((1 - alpha_interp) * r_spec + alpha_interp * r_salik)
            curr_g = int((1 - alpha_interp) * g_spec + alpha_interp * g_salik)
            curr_b = int((1 - alpha_interp) * b_spec + alpha_interp * b_salik)
            particle_color = QColor(curr_r, curr_g, curr_b)

            painter.setPen(Qt.NoPen) 
            painter.setBrush(particle_color)
            
            current_particle_size = self.base_particle_render_size
            if self.idle_state == "idle" and self.transition_alpha == 1.0: # Pulsing only when fully SALIK
                pulse_offset = self.pulse_amplitude * np.sin(self.pulse_animation_step)
                current_particle_size = max(1.0, self.base_particle_render_size + pulse_offset)

            radius = current_particle_size / 2.0
            
            # Draw particles at their current_pos
            # For scrolling, we might need to draw particles twice if they wrap around.
            # The self.particle_current_pos already includes the scroll offset via current_salik_targets.
            for i in range(self.num_particles):
                px, py = self.particle_current_pos[i]
                
                # Primary drawing
                painter.drawRect(QRectF(px - radius, py - radius, current_particle_size, current_particle_size))

                # Handle wrap-around drawing for scrolling SALIK
                # This is a simplified wrap-around; more robust would be to check individual particle visibility.
                if (self.idle_state == "idle" or (self.idle_state == "fading_to_idle" and self.transition_alpha > 0.5)) and self._salik_points_calculated:
                    # If particle's target X (with scroll) is near left edge, draw also on right
                    if px < radius + 20 : # 20 is a small margin
                         painter.drawRect(QRectF(px + width - radius, py - radius, current_particle_size, current_particle_size))
                    # If particle's target X is near right edge, draw also on left
                    elif px > width - radius - 20:
                         painter.drawRect(QRectF(px - width - radius, py - radius, current_particle_size, current_particle_size))


        finally:
            painter.end()
