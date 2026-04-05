import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFileDialog, QScrollArea, QFrame, QListWidget, 
                               QListWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QPen, QCursor
from PySide6.QtCore import Qt, QPoint, QSize, Signal, QObject
from color_model import ColorModel

class ColorItemWidget(QWidget):
    """Custom widget for displaying a color in the list with exclude and delete buttons."""
    delete_requested = Signal(int)
    exclude_toggled = Signal(int)

    def __init__(self, index, color_data, parent=None):
        super().__init__(parent)
        self.index = index
        self.color_data = color_data
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Color circle
        self.color_circle = QLabel()
        self.color_circle.setFixedSize(24, 24)
        r, g, b = color_data['rgb']
        self.color_circle.setStyleSheet(f"background-color: rgb({r},{g},{b}); border-radius: 12px; border: 1px solid #ccc;")
        layout.addWidget(self.color_circle)
        
        # RGB and Hex text
        info_text = f"RGB: ({r}, {g}, {b})  Hex: {color_data['hex']}"
        self.info_label = QLabel(info_text)
        
        # Visual feedback for excluded state
        if color_data.get('excluded', False):
            self.info_label.setStyleSheet("color: #888; text-decoration: line-through;")
            self.color_circle.setStyleSheet(f"background-color: rgba({r},{g},{b}, 100); border-radius: 12px; border: 1px dashed #888;")
        
        layout.addWidget(self.info_label)
        layout.addStretch()
        
        # Exclude toggle button
        exclude_text = "Include" if color_data.get('excluded', False) else "Exclude"
        self.exclude_btn = QPushButton(exclude_text)
        self.exclude_btn.setFixedSize(60, 24)
        self.exclude_btn.setStyleSheet("font-size: 10px;")
        self.exclude_btn.clicked.connect(lambda: self.exclude_toggled.emit(self.index))
        layout.addWidget(self.exclude_btn)
        
        # Delete button
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet("QPushButton { color: red; font-weight: bold; border: none; } QPushButton:hover { background-color: #eee; }")
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        layout.addWidget(self.delete_btn)

class ImageLabel(QLabel):
    """Custom QLabel to handle mouse events and magnification."""
    color_picked = Signal(int, int, int)
    mouse_moved = Signal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.original_pixmap = None

    def set_image(self, pixmap):
        self.original_pixmap = pixmap
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())

    def mouseMoveEvent(self, event):
        if self.pixmap():
            self.mouse_moved.emit(event.position().toPoint())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.pixmap() and event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            image = self.pixmap().toImage()
            if 0 <= pos.x() < image.width() and 0 <= pos.y() < image.height():
                color = QColor(image.pixel(pos))
                self.color_picked.emit(color.red(), color.green(), color.blue())
        super().mousePressEvent(event)

class MagnifierWidget(QLabel):
    """A small widget that shows a magnified view of the area under the cursor."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self.setStyleSheet("border: 2px solid #333; background-color: white;")
        self.zoom_factor = 5
        self.source_pixmap = None

    def update_view(self, pos, pixmap):
        if not pixmap:
            return
        
        self.source_pixmap = pixmap
        size = 150 // self.zoom_factor
        rect_x = pos.x() - size // 2
        rect_y = pos.y() - size // 2
        
        # Extract the small portion of the image
        cropped = pixmap.copy(rect_x, rect_y, size, size)
        scaled = cropped.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        
        # Draw a crosshair in the center
        painter = QPainter(scaled)
        painter.setPen(QPen(Qt.GlobalColor.red, 1))
        painter.drawLine(75, 65, 75, 85)
        painter.drawLine(65, 75, 85, 75)
        painter.end()
        
        self.setPixmap(scaled)

class ColorPickerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Image Color Picker (with Exclusion)")
        self.resize(1100, 750)
        
        self.model = ColorModel()
        self.init_ui()
        self.refresh_color_list()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        outer_layout = QVBoxLayout(central_widget)
        
        main_layout = QHBoxLayout()

        # Left side: Image Area
        left_layout = QVBoxLayout()
        
        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.clicked.connect(self.upload_image)
        left_layout.addWidget(self.upload_btn)

        self.scroll_area = QScrollArea()
        self.image_label = ImageLabel()
        self.image_label.color_picked.connect(self.add_color)
        self.image_label.mouse_moved.connect(self.update_magnifier)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        left_layout.addWidget(self.scroll_area)
        
        main_layout.addLayout(left_layout, 3)

        # Right side: Controls and List
        right_layout = QVBoxLayout()
        
        # Magnifier
        right_layout.addWidget(QLabel("Magnifier:"))
        self.magnifier = MagnifierWidget()
        right_layout.addWidget(self.magnifier, alignment=Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addSpacing(20)
        
        # Color List
        right_layout.addWidget(QLabel("Selected Colors:"))
        self.color_list_widget = QListWidget()
        right_layout.addWidget(self.color_list_widget)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_colors)
        right_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(right_layout, 1)
        
        outer_layout.addLayout(main_layout)
        
        # Bottom: Export Button
        self.export_svg_btn = QPushButton("Export as SVG")
        self.export_svg_btn.setFixedHeight(40)
        self.export_svg_btn.setStyleSheet("font-weight: bold; background-color: #f0f0f0;")
        self.export_svg_btn.clicked.connect(self.export_as_svg)
        outer_layout.addWidget(self.export_svg_btn)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.image_label.set_image(pixmap)

    def update_magnifier(self, pos):
        if self.image_label.pixmap():
            self.magnifier.update_view(pos, self.image_label.pixmap())

    def add_color(self, r, g, b):
        self.model.add_color(r, g, b)
        self.refresh_color_list()

    def toggle_exclude(self, index):
        self.model.toggle_exclude(index)
        self.refresh_color_list()

    def remove_color(self, index):
        self.model.remove_color(index)
        self.refresh_color_list()

    def clear_colors(self):
        self.model.clear()
        self.refresh_color_list()

    def refresh_color_list(self):
        self.color_list_widget.clear()
        for i, color_data in enumerate(self.model.get_colors()):
            item = QListWidgetItem(self.color_list_widget)
            widget = ColorItemWidget(i, color_data)
            widget.delete_requested.connect(self.remove_color)
            widget.exclude_toggled.connect(self.toggle_exclude)
            item.setSizeHint(widget.sizeHint())
            self.color_list_widget.addItem(item)
            self.color_list_widget.setItemWidget(item, widget)

    def export_as_svg(self):


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorPickerApp()
    window.show()
    sys.exit(app.exec())
