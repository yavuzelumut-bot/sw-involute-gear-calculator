import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QLocale
from PyQt6.QtGui import QDoubleValidator, QPainter, QPen, QColor, QFont, QPainterPath
import math

class GearPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m = 0
        self.z = 0
        self.d = 0
        self.da = 0
        self.df = 0
        self.bore = 0
        self.kw = 0
        self.kd = 0

    def update_gear(self, m, z, d, da, df, bore, kw, kd):
        self.m = m
        self.z = z
        self.d = d
        self.da = da
        self.df = df
        self.bore = bore
        self.kw = kw
        self.kd = kd
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center = QPointF(width / 2, height / 2)

        if self.d <= 0:
            painter.setPen(QColor("#444444"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "LIVE GEAR PREVIEW")
            return

        # Scaling
        scale = (min(width, height) * 0.75) / self.da
        
        r_pitch = (self.d / 2) * scale
        r_tip = (self.da / 2) * scale
        r_root = (self.df / 2) * scale

        # --- 1. GEAR SILHOUETTE DRAWING ---
        if self.z >= 3:
            gear_path = QPainterPath()
            z = int(self.z)
            angle_pitch = 2 * math.pi / z
            for i in range(z):
                a_start = i * angle_pitch
                a_1 = a_start + angle_pitch * 0.05
                a_2 = a_start + angle_pitch * 0.40
                a_3 = a_start + angle_pitch * 0.60
                a_4 = a_start + angle_pitch * 0.95
                
                p1 = QPointF(center.x() + r_root * math.cos(a_1), center.y() + r_root * math.sin(a_1))
                p2 = QPointF(center.x() + r_tip * math.cos(a_2), center.y() + r_tip * math.sin(a_2))
                p3 = QPointF(center.x() + r_tip * math.cos(a_3), center.y() + r_tip * math.sin(a_3))
                p4 = QPointF(center.x() + r_root * math.cos(a_4), center.y() + r_root * math.sin(a_4))
                
                if i == 0: gear_path.moveTo(p1)
                else: gear_path.lineTo(p1)
                
                gear_path.lineTo(p2)
                gear_path.lineTo(p3)
                gear_path.lineTo(p4)
                
            gear_path.closeSubpath()
            painter.setPen(QPen(QColor("#444444"), 1))
            painter.setBrush(QColor(50, 50, 50, 100))
            painter.drawPath(gear_path)

        # --- 2. TECHNICAL LINES ---
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Root Circle - Dashed Red
        painter.setPen(QPen(QColor("#E74C3C"), 1, Qt.PenStyle.DashLine))
        painter.drawEllipse(center, r_root, r_root)

        # Pitch Circle - Dashed Blue
        painter.setPen(QPen(QColor("#3498DB"), 2, Qt.PenStyle.DashDotLine))
        painter.drawEllipse(center, r_pitch, r_pitch)

        # Tip Circle - Solid White
        painter.setPen(QPen(QColor("#FFFFFF"), 1, Qt.PenStyle.SolidLine))
        painter.drawEllipse(center, r_tip, r_tip)

        # --- 3. BORE AND KEYWAY ---
        if self.bore > 0:
            bore_path = QPainterPath()
            r_bore = (self.bore / 2) * scale
            bore_path.addEllipse(center, r_bore, r_bore)
            
            if self.kw > 0 and self.kd > 0:
                kw_s = self.kw * scale
                kd_s = self.kd * scale
                key_rect = QRectF(center.x() - kw_s/2, center.y() - r_bore - kd_s, kw_s, r_bore + kd_s)
                bore_path.addRect(key_rect)
            
            final_bore_path = bore_path.simplified()
            painter.setPen(QPen(QColor("#F1C40F"), 2))
            painter.setBrush(QColor("#121212"))
            painter.drawPath(final_bore_path)

        # --- 4. DIMENSION LABELS ---
        painter.setFont(QFont("Consolas", 10))
        
        # Tip Dia (da)
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawLine(int(center.x() + r_tip + 10), int(center.y() - r_tip), 
                         int(center.x() + r_tip + 40), int(center.y() - r_tip))
        painter.drawText(int(center.x() + r_tip + 45), int(center.y() - r_tip + 5), f"da: {self.da:.2f}")

        # Pitch Dia (d)
        painter.setPen(QPen(QColor("#3498DB"), 1))
        painter.drawLine(int(center.x() + r_pitch + 10), int(center.y()), 
                         int(center.x() + r_pitch + 30), int(center.y()))
        painter.drawText(int(center.x() + r_pitch + 35), int(center.y() + 5), f"d: {self.d:.2f}")

        # Info
        painter.setPen(QColor("#F1C40F"))
        painter.drawText(20, 30, f"Module: {self.m}")
        painter.drawText(20, 50, f"Teeth: {int(self.z)}")

class GearCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1150, 780) 

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("QWidget { background-color: #121212; border-radius: 20px; }")
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # --- LEFT PANEL ---
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(350)
        self.left_panel.setStyleSheet("""
            QFrame { background-color: #252525; border-radius: 20px; }
            QLabel { color: #B3B3B3; font-family: 'Segoe UI'; font-size: 14px; background: transparent; }
            QLineEdit { background-color: #121212; color: white; border: 2px solid #000000; border-radius: 8px; padding: 6px; font-size: 14px; }
        """)
        
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(10)

        title = QLabel("GEAR GENERATOR")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 22px;")
        left_layout.addWidget(title)
        left_layout.addSpacing(10)

        numeric_validator = QDoubleValidator(0.1, 999.0, 2)
        locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        numeric_validator.setLocale(locale)
        numeric_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        # Input Groups
        self.module_input = self.create_input_group("Module", left_layout, numeric_validator)
        self.teeth_input = self.create_input_group("Number of Teeth", left_layout, numeric_validator)
        self.width_input = self.create_input_group("Face Width (Thickness)", left_layout, numeric_validator)
        self.bore_input = self.create_input_group("Bore Dia (Optional)", left_layout, numeric_validator)
        self.kw_input = self.create_input_group("Keyway Width", left_layout, numeric_validator)
        self.kd_input = self.create_input_group("Keyway Depth", left_layout, numeric_validator)

        # Navigation
        self.module_input.returnPressed.connect(self.teeth_input.setFocus)
        self.teeth_input.returnPressed.connect(self.width_input.setFocus)
        self.width_input.returnPressed.connect(self.bore_input.setFocus)
        self.bore_input.returnPressed.connect(self.kw_input.setFocus)
        self.kw_input.returnPressed.connect(self.kd_input.setFocus)
        self.kd_input.returnPressed.connect(self.calculate_gear_data)

        left_layout.addStretch()

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setFixedSize(110, 40)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-weight: bold; border-radius: 10px; }")
        self.clear_btn.clicked.connect(self.clear_inputs)
        
        self.generate_btn = QPushButton("GENERATE")
        self.generate_btn.setFixedHeight(50)
        self.generate_btn.setStyleSheet("QPushButton { background-color: #3498DB; color: white; font-weight: bold; border-radius: 10px; font-size: 16px; }")
        self.generate_btn.clicked.connect(self.calculate_gear_data)
        
        left_layout.addWidget(self.clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        left_layout.addWidget(self.generate_btn)

        self.main_layout.addWidget(self.left_panel)

        # --- RIGHT PANEL ---
        right_layout = QVBoxLayout()
        
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("□") 
        self.close_btn = QPushButton("✕")
        
        for btn, color in [(self.min_btn, "#F1C40F"), (self.max_btn, "#2ECC71"), (self.close_btn, "#E74C3C")]:
            btn.setFixedSize(30, 30)
            f_size = "20px" if btn == self.max_btn else "16px"
            extra_style = "padding-bottom: 3px;" if btn == self.min_btn else ""
            btn.setStyleSheet(f"color: {color}; font-size: {f_size}; background: transparent; font-weight: bold; border: none; {extra_style}")
            top_bar.addWidget(btn)
            
        self.close_btn.clicked.connect(self.close)
        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        right_layout.addLayout(top_bar)

        self.preview_area = GearPreviewWidget()
        self.preview_area.setStyleSheet("background-color: #1E1E1E; border-radius: 20px; border: 1px solid #3498DB;")
        right_layout.addWidget(self.preview_area, 3)

        self.results_area = QFrame()
        self.results_area.setStyleSheet("background-color: #1E1E1E; border-radius: 20px;")
        self.results_layout = QHBoxLayout(self.results_area)
        
        self.tech_data_display = QTextEdit()
        self.sw_formula_display = QTextEdit()
        
        for display in [self.tech_data_display, self.sw_formula_display]:
            display.setReadOnly(True)
            display.setStyleSheet("QTextEdit { background: transparent; color: white; font-family: 'Consolas', monospace; font-size: 13px; border: none; }")
            self.results_layout.addWidget(display)
            
        right_layout.addWidget(self.results_area, 1)
        self.main_layout.addLayout(right_layout)

    def create_input_group(self, label_text, layout, validator):
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setValidator(validator)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return line_edit

    def safe_float(self, text):
        try:
            return float(text.replace(',', '.'))
        except ValueError:
            return 0.0

    def calculate_gear_data(self):
        m_raw = self.module_input.text()
        z_raw = self.teeth_input.text()
        b_raw = self.width_input.text()
        
        if not m_raw or not z_raw or not b_raw:
            self.tech_data_display.setText("ERROR: Please fill in Module, Number of Teeth, and Width.")
            self.sw_formula_display.clear()
            return

        m = self.safe_float(m_raw)
        z = self.safe_float(z_raw)
        b = self.safe_float(b_raw)
        
        bore = self.safe_float(self.bore_input.text())
        kw = self.safe_float(self.kw_input.text())
        kd = self.safe_float(self.kd_input.text())
        
        d = m * z
        da = d + (2 * m)
        df = d - (2.5 * m)
        db = d * math.cos(math.radians(20))
        rb = db / 2
        
        tech_text = (
            f"--- TECHNICAL DATA ---\n"
            f"Pitch (d):     {d:.2f} mm\n"
            f"Outer (da):    {da:.2f} mm\n"
            f"Root  (df):    {df:.2f} mm\n"
            f"Base  (db):    {db:.2f} mm\n"
            f"Face Width:    {b:.2f} mm\n"
            f"Bore Dia:      {bore:.2f} mm\n"
            f"Keyway:        {kw:.2f} x {kd:.2f} mm"
        )
        
        sw_text = (
            f"--- SOLIDWORKS EQUATION ---\n"
            f"X: {rb:.4f} * (cos(t) + t*sin(t))\n"
            f"Y: {rb:.4f} * (sin(t) - t*cos(t))\n"
            f"Range: t from 0 to 1"
        )
        
        self.tech_data_display.setText(tech_text)
        self.sw_formula_display.setText(sw_text)
        self.preview_area.update_gear(m, z, d, da, df, bore, kw, kd)

    def clear_inputs(self):
        for input_field in [self.module_input, self.teeth_input, self.width_input, 
                            self.bore_input, self.kw_input, self.kd_input]:
            input_field.clear()
        self.tech_data_display.clear()
        self.sw_formula_display.clear()
        self.preview_area.update_gear(0, 0, 0, 0, 0, 0, 0, 0)

    def toggle_maximize(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GearCalculator()
    window.show()
    sys.exit(app.exec())