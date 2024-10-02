"""
Software de gestión de campus virtual para  centros educativos .
"""

import os
import sys
import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk, ImageOps, ImageDraw
from tkcalendar import DateEntry
from databaseManager import *
import module_fact  # Importa el módulo sin traer todos los nombres al espacio global
from module_fact import FacturacionApp
import module_registro
import registro_alumno
from reportes_facturacion import ReportesFacturacionApp
from informes_app import InformesApp
from module_cobranza import CobranzaApp




def resource_path(relative_path):
    """ Obtener el camino absoluto al recurso, trabaja para Dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena el camino en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CampusUI:
    """
    Clase principal de la interfaz de usuario de la aplicación LSCollege.
    """
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.state('zoomed')
        self.root.geometry("1366x768")
        self.root.title("Campus Virtual")
        
        # Use resource_path to create the path to the icon
        icon_path = resource_path('college.ico')
        self.root.iconbitmap(icon_path)

        self.background = tk.Frame(self.root, bg='white')
        self.background.place(relwidth=1, relheight=1)

        self.main_frame = ttk.Frame(self.background)
        self.main_frame.place(relwidth=1, relheight=1)

        # Use resource_path to create the path to the logo image
        logo_image_path = resource_path('logo.png')
        logo = Image.open(logo_image_path)
        logo = logo.resize((104, 104), Image.Resampling.NEAREST)
        logo_photo = ImageTk.PhotoImage(logo)

        logo_label = ttk.Label(self.main_frame, image=logo_photo, borderwidth=0)
        logo_label.image = logo_photo
        logo_label.place(relx=0.3, rely=0.064, anchor='w')

        # label title
        title_label = ttk.Label(self.main_frame, text="Campus Virtual LSCollege", font=("noto sans", 24, "bold"))
        title_label.place(relx=0.4, rely=0.07, anchor='w')

        # Creación de las secciones
        self.create_sections()
        self.section_functions = {
            "Registro": (self.registro_representante, self.registro_alumno),
            "Facturación": (self.facturacion_click, self.cierre_diario),
            "Informes": (self.informe_1, self.informe_2),
        }

    def create_sections(self):
        """
        Crea las secciones de la interfaz de usuario.
        """
        sections = ["Registro", "Facturación", "Informes"]
        images = ["register_representante.png", "facturar.png", "informes1.png"]
        images2 = ["register_alumno.png", "cierre_diario.png", "informes2.png"]
        for i, section in enumerate(sections):  # itera sobre las secciones
            line = ttk.Frame(self.main_frame, height=2, relief='sunken')
            line.place(relx=0.15, rely=(i * 0.3) + 0.16, relwidth=0.8)

            label = ttk.Label(self.main_frame, text=section, font=("noto sans", 14, "bold"))
            label.place(relx=0.05, rely=(i * 0.3) + 0.16, anchor='w')
            label.configure(width=10)

            image_path = resource_path(images[i])
            image = self.load_and_customize_image(image_path)
            image_label = tk.Label(self.main_frame, image=image)
            image_label.image = image
            image_label.place(relx=0.05, rely=(i * 0.3) + 0.28, anchor='w')
            image_label.bind("<Button-1>", lambda event, s=section: self.section_functions[s][0](event))

            image2_path = resource_path(images2[i])
            image2 = self.load_and_customize_image(image2_path)
            image_label_2 = tk.Label(self.main_frame, image=image2)
            image_label_2.image = image2
            image_label_2.place(relx=0.25, rely=(i * 0.3) + 0.28, anchor='w')
            image_label_2.bind("<Button-1>", lambda event, s=section: self.section_functions[s][1](event))

    def load_and_customize_image(self, image_path):
        """
        Carga una imagen, la redimensiona y la ajusta al widget.
        """
        # Carga la imagen manteniendo su color original
        image = Image.open(image_path)
        
        # Redimensiona la imagen para que encaje bien en el widget
        image = image.resize((100, 100), Image.Resampling.NEAREST)
        
        # Convierte la imagen a un objeto PhotoImage para usar en Tkinter
        return ImageTk.PhotoImage(image)

    def registro_representante(self, event=None):
        """
        Llama la función registro_click desde module_registro.
        """
        module_registro.registro_click(self, self.main_frame, event)

    def registro_alumno(self, event=None):
        """
        Llama la función registro_click desde module_registro.
        """
        registro_alumno.registro_alumno_click(self, self.main_frame, event)

    def facturacion_click(self, event=None):
        main_frame = self.main_frame
        FacturacionApp(main_frame)
        print("ventana de facturacion abierta")

    def cierre_diario(self, event=None):
        ReportesFacturacionApp(self.main_frame)
        print("Módulo de Reportes de Facturación abierto")
    
    def informe_1(self, event):
        InformesApp(self.main_frame)
        print("Módulo de Informes abierto")

    def informe_2(self, event):
        CobranzaApp(self.main_frame)
        print("Informes de cobranza")

app = CampusUI()
app.root.mainloop()
# Fin del archivo main_window.py
