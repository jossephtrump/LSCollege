import os
import sys
import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk, ImageOps, ImageDraw
from module_funciones import *
from module_funciones import cedula_return
from client import Client
from tkcalendar import DateEntry
from module_informes import *
from databaseManager import *
from module_fact import *
import module_access
import module_activacion
import module_person
import module_registro

def resource_path(relative_path):
    """ Obtener el camino absoluto al recurso, trabaja para Dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena el camino en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class VidaGymUI:
    """
    Clase principal de la interfaz de usuario de la aplicación Vida Gym.
    """
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.state('zoomed')
        self.root.geometry("1366x768")
        self.root.title("VIDA GYM")
        
        # Use resource_path to create the path to the icon
        icon_path = resource_path('gym.ico')
        self.root.iconbitmap(icon_path)

        self.background = tk.Frame(self.root, bg='white')
        self.background.place(relwidth=1, relheight=1)

        self.main_frame = ttk.Frame(self.background)
        self.main_frame.place(relwidth=1, relheight=1)

        # Use resource_path to create the path to the logo image
        logo_image_path = resource_path('logovidagym.png')
        logo = Image.open(logo_image_path)
        logo = logo.resize((298, 45), Image.Resampling.NEAREST)
        logo_photo = ImageTk.PhotoImage(logo)

        logo_label = ttk.Label(self.main_frame, image=logo_photo, borderwidth=0)
        logo_label.image = logo_photo
        logo_label.place(relx=0.05, rely=0.05, anchor='w')

        # Creación de las secciones
        self.create_sections()
        self.section_functions = {
            "Registro": (self.registro_click, self.puerta),
            "Facturación": (self.facturacion_click, self.activacion_click),
            "Informes": (self.informe_click, self.informe_click_2),
        }

    def create_sections(self):
        """
        Crea las secciones de la interfaz de usuario.
        """
        sections = ["Registro", "Facturación", "Informes"]
        images = ["registro1.jpg", "fact1.jpg", "informes1.jpg"]
        images2 = ["puerta.jpg", "fact3.jpg", "informes2.jpg"]
        for i, section in enumerate(sections):  # itera sobre las secciones
            line = ttk.Frame(self.main_frame, height=2, relief='sunken')
            line.place(relx=0.15, rely=(i * 0.3) + 0.15, relwidth=0.8)

            label = ttk.Label(self.main_frame, text=section, font=("noto sans", 14, "bold"))
            label.place(relx=0.05, rely=(i * 0.3) + 0.15, anchor='w')
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
        Carga una imagen y la personaliza.
        """
        image = Image.open(image_path)
        image = image.resize((100, 100), Image.Resampling.NEAREST)
        image = ImageOps.colorize(image.convert("L"), '#000000',  '#F9E79F')
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + image.size, 20, fill=255)
        image.putalpha(mask)
        border = 30
        background = Image.new('RGB', (image.width + border * 4, image.height + border * 2), '#F9E79F')
        bg_mask = Image.new('L', background.size, 0)
        bg_draw = ImageDraw.Draw(bg_mask)
        bg_draw.rounded_rectangle((0, 0) + background.size, 30, fill=255)
        background.putalpha(bg_mask)
        position = ((background.width - image.width) // 2, (background.height - image.height) // 2)
        background.paste(image, position, image)
        return ImageTk.PhotoImage(background)

    def solicitar_clave(self, callback):
        """
        Solicita una clave de verificación antes de permitir el acceso a una funcionalidad.
        """
        def verificar_clave():
            clave_ingresada = clave_entry.get()
            clave_correcta = "1234"
            if clave_ingresada == clave_correcta:
                messagebox.showinfo("Clave correcta", "La clave ingresada es correcta.")
                clave_window.destroy()
                callback()
            else:
                messagebox.showerror("Clave incorrecta", "La clave ingresada es incorrecta.")

        clave_window = tk.Toplevel(self.root)
        clave_window.title("Verificar clave")
        clave_window.geometry("300x150")
        clave_window.resizable(False, False)
        clave_window.iconbitmap(resource_path("gym.ico"))

        label = ttk.Label(clave_window, text="Ingrese la clave de verificación:")
        label.pack(pady=10)

        clave_entry = ttk.Entry(clave_window, show="*")
        clave_entry.pack(pady=5)

        verificar_button = ttk.Button(clave_window, text="Verificar", command=verificar_clave)
        verificar_button.pack(pady=10)

        clave_window.transient(self.root)
        clave_window.grab_set()

        # Centrando la ventana en la pantalla
        self.root.update_idletasks()
        window_width = clave_window.winfo_width()
        window_height = clave_window.winfo_height()
        position_right = int(self.root.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.root.winfo_screenheight()/2 - window_height/2)
        clave_window.geometry("+{}+{}".format(position_right, position_down))
        
        self.root.wait_window(clave_window)

    def registro_click(self, event=None):
        """
        Llama la función registro_click desde module_registro.
        """
        module_registro.registro_click(self, self.main_frame, event)

    def activacion_click(self, event=None):
        self.solicitar_clave(lambda: module_activacion.mostrar_usuarios_con_facturas_pagadas())
        print("ventana de activacion abierta")

    def facturacion_click(self, event=None):
        main_frame = self.main_frame
        FacturacionApp(main_frame)
        print("ventana de facturacion abierta")

    def puerta(self, event):
        try:
            module_access.door_open()  # Llama a la función para abrir la puerta
            messagebox.showinfo("Door Open", "La puerta se ha abierto")
        except Exception as e:
            print(f"Error al intentar abrir la puerta: {e}")
            messagebox.showerror("Error", f"Error al abrir la puerta: {e}")

    def informe_click(self, event):
        main_frame = self.main_frame
        informe_click(main_frame)
        print("Informes por usuario")

    def informe_click_2(self, event):
        main_frame = self.main_frame
        informe_users(main_frame)
        print("Informes de asistencia")

app = VidaGymUI()
app.root.mainloop()
# Fin del archivo main_window.py
