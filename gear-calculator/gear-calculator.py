import customtkinter as ctk
from tkinter import messagebox
import math
import os
import sys

# Theme settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Involute Gear Equation Generator for SolidWorks")
        
        # Window centering logic
        window_width = 580
        window_height = 720
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        # Set application icon
        try:
            icon_path = resource_path("gear.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                self.after(200, lambda: self.iconbitmap(icon_path))
        except Exception:
            pass

        # UI Components
        self.label_title = ctk.CTkLabel(self, text="Gear & Involute Calculator", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=25)

        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.pack(pady=10, padx=20, fill="x")

        # Inputs with labels and focus bindings
        self._create_input("Module (m):", "entry_m", "e.g., 2.5", 0)
        self._create_input("Number of Teeth (z):", "entry_z", "e.g., 30", 1)
        self._create_input("Gear Thickness (mm):", "entry_thickness", "e.g., 20", 2)

        # t2 input with info button
        self.label_t2 = ctk.CTkLabel(self.frame_inputs, text="t2 (Curve Length):", font=ctk.CTkFont(weight="bold"))
        self.label_t2.grid(row=3, column=0, padx=15, pady=10, sticky="w")
        
        self.frame_t2_inner = ctk.CTkFrame(self.frame_inputs, fg_color="transparent")
        self.frame_t2_inner.grid(row=3, column=1, padx=15, pady=10, sticky="w")
        
        self.entry_t2 = ctk.CTkEntry(self.frame_t2_inner, width=80)
        self.entry_t2.pack(side="left", padx=(0, 10))
        self.entry_t2.insert(0, "0.7")
        
        # Binding Enter keys for navigation
        self.entry_m.bind("<Return>", lambda e: self.entry_z.focus())
        self.entry_z.bind("<Return>", lambda e: self.entry_thickness.focus())
        self.entry_thickness.bind("<Return>", lambda e: self.entry_t2.focus())
        self.entry_t2.bind("<Return>", lambda e: self.calculate())

        self.btn_info = ctk.CTkButton(self.frame_t2_inner, text="?", width=30, fg_color="#F39C12", hover_color="#D68910", command=self.show_info)
        self.btn_info.pack(side="left")

        # Action Buttons
        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(pady=20)

        self.btn_calc = ctk.CTkButton(self.frame_btns, text="Calculate & Generate", font=ctk.CTkFont(weight="bold"), command=self.calculate)
        self.btn_calc.pack(side="left", padx=10)

        self.btn_clear = ctk.CTkButton(self.frame_btns, text="Clear", width=80, fg_color="#C0392B", hover_color="#922B21", command=self.clear_fields)
        self.btn_clear.pack(side="left", padx=10)

        self.textbox_result = ctk.CTkTextbox(self, width=520, height=280, font=ctk.CTkFont(family="Consolas", size=13))
        self.textbox_result.pack(pady=10, padx=20)

    def _create_input(self, label_text, attr_name, placeholder, row_idx):
        label = ctk.CTkLabel(self.frame_inputs, text=label_text, font=ctk.CTkFont(weight="bold"))
        label.grid(row=row_idx, column=0, padx=15, pady=10, sticky="w")
        entry = ctk.CTkEntry(self.frame_inputs, placeholder_text=placeholder)
        entry.grid(row=row_idx, column=1, padx=15, pady=10)
        setattr(self, attr_name, entry)

    def show_info(self):
        msg = "The 't2' value controls the length of the involute curve.\n\n" \
              "Increase this value if the curve doesn't reach the Addendum Circle (outer diameter)."
        messagebox.showinfo("Involute Parameter Info", msg)

    def clear_fields(self):
        for entry in [self.entry_m, self.entry_z, self.entry_thickness, self.entry_t2]:
            entry.delete(0, 'end')
        self.entry_t2.insert(0, "0.7")
        self.textbox_result.delete("1.0", "end")
        self.entry_m.focus()

    def calculate(self):
        try:
            m_str = self.entry_m.get()
            z_str = self.entry_z.get()
            
            if not m_str or not z_str:
                messagebox.showwarning("Input Error", "Please enter Module and Number of Teeth.")
                return

            m = float(m_str)
            z = float(z_str)
            t2_val = self.entry_t2.get()
            t2 = float(t2_val) if t2_val else 0.7
            
            if m <= 0 or z <= 0:
                messagebox.showwarning("Input Error", "Module and Number of Teeth must be positive values.")
                return

            thickness = float(self.entry_thickness.get()) if self.entry_thickness.get() else 0.0
            
            # Geometric Calculations
            d0 = m * z               
            base_radius = d0 / 2               
            da = d0 + (2 * m)          
            df = d0 - (2.332 * m) 
            h = (da - df) / 2
            p_pitch = math.pi * m    
            center_angle = 90 / z  

            res = "--- GEAR GEOMETRY DATA ---\n"
            res += f"Circular Pitch (p)   : {p_pitch:.4f} mm\n"
            res += f"Pitch Diameter (d)   : {d0:.4f} mm\n"
            res += f"Addendum Diameter(da): {da:.4f} mm\n"
            res += f"Dedendum Diameter(df): {df:.4f} mm\n"
            res += f"Total Tooth Depth (h): {h:.4f} mm\n"
            res += f"Face Width (b)       : {thickness:.4f} mm\n"
            res += f"Tooth Center Angle   : {center_angle:.4f}°\n\n"

            res += "--- SOLIDWORKS EQUATION-DRIVEN CURVE ---\n"
            res += "Paste these into the 'Equation Driven Curve' tool:\n"
            res += f"Xt = ({base_radius:.4f})*(cos(t)+t*sin(t))\n"
            res += f"Yt = ({base_radius:.4f})*(sin(t)-t*cos(t))\n"
            res += "t1 = 0\n"
            res += f"t2 = {t2}\n"

            self.textbox_result.delete("1.0", "end")
            self.textbox_result.insert("1.0", res)

        except ValueError:
            messagebox.showerror("Error", "Please provide valid numerical inputs.")

if __name__ == "__main__":
    app = App()
    app.mainloop()