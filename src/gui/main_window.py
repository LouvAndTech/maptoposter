"""Main window for the Qt GUI application."""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QComboBox,
    QCheckBox, QFileDialog, QMessageBox, QProgressBar, QTextEdit,
    QTabWidget, QFormLayout, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from src.data import get_coordinates
from src.theme import load_theme, get_available_themes
from src.core import create_poster
from src.callbacks import register_status_callback, register_progress_callback, clear_callbacks
from src.fonts import load_fonts


class PosterGeneratorWorker(QThread):
    """Worker thread for poster generation to prevent GUI freezing."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, params: dict):
        super().__init__()
        self.params = params
    
    def run(self):
        """Run the poster generation."""
        try:
            self.progress.emit("Generating poster...")
            create_poster(**self.params)
            self.finished.emit(True, f"✓ Poster saved to {self.params['output_file']}")
        except Exception as e:
            self.finished.emit(False, f"✗ Error: {str(e)}")


class MainWindow(QMainWindow):
    """Main window for the map poster generator GUI."""
    
    def __init__(self):
        super().__init__()
        self.generator_thread: Optional[PosterGeneratorWorker] = None
        
        # Register callbacks for status updates
        register_status_callback(self.on_status_update)
        register_progress_callback(self.on_progress_update)
        
        self.init_ui()
        self.setWindowTitle("City Map Poster Generator")
        self.setGeometry(100, 100, 900, 750)
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Basic tab
        basic_tab = self._create_basic_tab()
        tabs.addTab(basic_tab, "Basic")
        
        # Advanced tab
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        main_layout.addWidget(tabs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Output text
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(300)
        main_layout.addWidget(QLabel("Output:"))
        self.output_text.setFont(QFont("Courier New", 12))
        main_layout.addWidget(self.output_text)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Poster")
        self.generate_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.generate_btn.clicked.connect(self.generate_poster)
        main_layout.addWidget(self.generate_btn)
        
        central_widget.setLayout(main_layout)
    
    def _create_basic_tab(self) -> QWidget:
        """Create the basic settings tab."""
        tab = QWidget()
        layout = QFormLayout()
        
        # City
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Paris")
        layout.addRow("City:", self.city_input)
        
        # Country
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("e.g., France")
        layout.addRow("Country:", self.country_input)
        
        # Theme
        self.theme_combo = QComboBox()
        themes = get_available_themes()
        self.theme_combo.addItems(themes)
        self.theme_combo.setCurrentText("terracotta")
        layout.addRow("Theme:", self.theme_combo)
        
        # Distance
        self.distance_spin = QSpinBox()
        self.distance_spin.setMinimum(100)
        self.distance_spin.setMaximum(100000)
        self.distance_spin.setValue(18000)
        self.distance_spin.setSingleStep(1000)
        self.distance_spin.setSuffix(" m")
        layout.addRow("Distance (map radius):", self.distance_spin)
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "svg", "pdf"])
        layout.addRow("Output Format:", self.format_combo)
        
        # Output file
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Auto-generated if empty")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_btn)
        layout.addRow("Output File:", output_layout)
        
        tab.setLayout(layout)
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """Create the advanced settings tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        layout = QFormLayout()
        
        # Dimensions
        dim_group = QGroupBox("Dimensions")
        dim_layout = QFormLayout()
        
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setMinimum(3.6)
        self.width_spin.setMaximum(20)
        self.width_spin.setValue(12)
        self.width_spin.setSingleStep(0.5)
        self.width_spin.setSuffix(" in")
        dim_layout.addRow("Width:", self.width_spin)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setMinimum(3.6)
        self.height_spin.setMaximum(20)
        self.height_spin.setValue(16)
        self.height_spin.setSingleStep(0.5)
        self.height_spin.setSuffix(" in")
        dim_layout.addRow("Height:", self.height_spin)
        
        self.metric_check = QCheckBox("Use metric units (cm)")
        self.metric_check.toggled.connect(self.update_dimension_units)
        dim_layout.addRow("", self.metric_check)
        
        dim_group.setLayout(dim_layout)
        layout.addRow(dim_group)
        
        # Display overrides
        override_group = QGroupBox("Display Overrides")
        override_layout = QFormLayout()
        
        self.display_city_input = QLineEdit()
        self.display_city_input.setPlaceholderText("Leave empty to use city name")
        override_layout.addRow("Display City:", self.display_city_input)
        
        self.display_country_input = QLineEdit()
        self.display_country_input.setPlaceholderText("Leave empty to use country name")
        override_layout.addRow("Display Country:", self.display_country_input)
        
        self.country_label_input = QLineEdit()
        self.country_label_input.setPlaceholderText("Label to display on poster")
        override_layout.addRow("Country Label:", self.country_label_input)
        
        override_group.setLayout(override_layout)
        layout.addRow(override_group)
        
        # Coordinates override
        coord_group = QGroupBox("Coordinates Override")
        coord_layout = QFormLayout()
        
        self.latitude_input = QLineEdit()
        self.latitude_input.setPlaceholderText("Leave empty to geocode")
        coord_layout.addRow("Latitude:", self.latitude_input)
        
        self.longitude_input = QLineEdit()
        self.longitude_input.setPlaceholderText("Leave empty to geocode")
        coord_layout.addRow("Longitude:", self.longitude_input)
        
        coord_group.setLayout(coord_layout)
        layout.addRow(coord_group)
        
        # Fonts and options
        self.font_input = QLineEdit()
        self.font_input.setPlaceholderText("Google Fonts name (e.g., 'Noto Sans JP')")
        layout.addRow("Font Family:", self.font_input)
        
        self.no_railways_check = QCheckBox("Exclude railways")
        layout.addRow("", self.no_railways_check)

        self.include_oceans_check = QCheckBox("Attempt to render oceans based on coastlines")
        layout.addRow("", self.include_oceans_check)
        
        widget.setLayout(layout)
        scroll.setWidget(widget)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll)
        tab.setLayout(tab_layout)
        return tab
    
    def browse_output(self):
        """Open file dialog for output file selection."""
        format_ext = self.format_combo.currentText()
        file_filter = f"{format_ext.upper()} Files (*.{format_ext})"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Poster As", "", file_filter
        )
        if file_path:
            self.output_path.setText(file_path)
    
    def validate_inputs(self) -> tuple[bool, str]:
        """Validate user inputs."""
        if not self.city_input.text().strip():
            return False, "Please enter a city name"
        if not self.country_input.text().strip():
            return False, "Please enter a country name"
        
        # Validate coordinates if provided
        if self.latitude_input.text().strip() or self.longitude_input.text().strip():
            if not (self.latitude_input.text().strip() and self.longitude_input.text().strip()):
                return False, "Both latitude and longitude must be provided together"
        
        return True, ""
    
    def update_dimension_units(self, is_metric: bool):
        """Update dimension spin boxes suffixes based on metric selection."""
        if is_metric:
            self.width_spin.setSuffix(" cm")
            self.height_spin.setSuffix(" cm")
        else:
            self.width_spin.setSuffix(" in")
            self.height_spin.setSuffix(" in")
    
    def on_status_update(self, message: str):
        """Handle status update from core app."""
        self.log_output(message)
    
    def on_progress_update(self, description: str, current: int, total: int):
        """Handle progress update from core app."""
        if total > 0:
            progress_percent = int((current / total) * 100)
            self.progress_bar.setValue(progress_percent)
            self.progress_bar.setFormat(f"{description}... {progress_percent}%")
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"{description}...")
    
    def closeEvent(self, event):
        """Clean up callbacks when closing the window."""
        clear_callbacks()
        super().closeEvent(event)
    
    def generate_poster(self):
        """Generate the poster."""
        # Validate inputs
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        # Disable generate button
        self.generate_btn.setEnabled(False)
        self.output_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            city = self.city_input.text().strip()
            country = self.country_input.text().strip()
            theme = self.theme_combo.currentText()
            
            # Get coordinates
            if self.latitude_input.text().strip() and self.longitude_input.text().strip():
                from lat_lon_parser import parse
                try:
                    lat = parse(self.latitude_input.text())
                    lon = parse(self.longitude_input.text())
                    point = (lat, lon)
                    self.log_output(f"Using provided coordinates: {lat}, {lon}")
                except ValueError as e:
                    QMessageBox.critical(self, "Error", f"Invalid coordinates: {e}")
                    self.generate_btn.setEnabled(True)
                    return
            else:
                self.log_output("Looking up coordinates...")
                point = get_coordinates(city, country)
            
            # Prepare parameters
            output_file = self.output_path.text().strip()
            if not output_file:
                from src.core.poster import generate_output_filename
                output_file = generate_output_filename(city, theme, self.format_combo.currentText())
            
            # Load theme
            theme_dict = load_theme(theme)
            
            # Load fonts
            fonts = load_fonts()
            if self.font_input.text().strip():
                custom_fonts = load_fonts(self.font_input.text())
                if custom_fonts:
                    fonts = custom_fonts
            
            params = {
                "city": city,
                "country": country,
                "point": point,
                "dist": self.distance_spin.value(),
                "output_file": output_file,
                "output_format": self.format_combo.currentText(),
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
                "metric": self.metric_check.isChecked(),
                "country_label": self.country_label_input.text() or None,
                "display_city": self.display_city_input.text() or None,
                "display_country": self.display_country_input.text() or None,
                "fonts": fonts,
                "exclude_railways": self.no_railways_check.isChecked(),
                "theme_dict": theme_dict,
                "include_oceans": self.include_oceans_check.isChecked()
            }
            
            # Create and start worker thread
            self.generator_thread = PosterGeneratorWorker(params)
            self.generator_thread.progress.connect(self.log_output)
            self.generator_thread.finished.connect(self.on_generation_finished)
            self.generator_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start generation: {str(e)}")
            self.generate_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def log_output(self, message: str):
        """Log output message."""
        self.output_text.append(message)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
    
    def on_generation_finished(self, success: bool, message: str):
        """Handle generation completion."""
        self.log_output(message)
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)


def main():
    """Main entry point for the GUI."""
    app = __import__('PyQt6.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
