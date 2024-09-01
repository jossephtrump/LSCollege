"""
Este script se encarga de registrar a un alumno en la base de datos.
""" 

import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from databaseManager import mydb
from datetime import datetime

def registro_alumno_click(main_app, main_frame, event=None):
    """
    Crea la pestaña de registro para los alumnos.
    """
    notebook = ttk.Notebook(main_frame, style='TNotebook')
    notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

    tab_registro = ttk.Frame(notebook)
    notebook.add(tab_registro, text="Registro Alumno")

    a = 26
    font = ('noto sans', 10, 'bold')
    register_frame = tk.Frame(tab_registro, bd=2, relief='groove')
    register_frame.config(bg='#F0F3F4')
    register_frame.place(relx=0.5, rely=0.48, width=450, height=560, anchor='center')

    def close_tab():
        notebook.forget(tab_registro)  # Cierra la pestaña de registro
        notebook.place_forget()  # Oculta el notebook
        main_frame.lift()  # Trae el main_frame al frente
        main_frame.focus_force()  # Fuerza el enfoque en el main_frame
        main_app.root.update_idletasks()  # Actualiza cualquier tarea pendiente
        main_app.root.deiconify()  # Asegura que la ventana principal esté visible
        main_app.root.focus_force()  # Vuelve a forzar el enfoque en la ventana principal

        print("Formulario de registro cerrado")

    close_button = tk.Button(register_frame, text="X", font=font, bg='#F0F3F4', bd=0, command=close_tab)
    close_button.place(relx=0.97, rely=0.01, anchor='ne')

    style = ttk.Style()
    style.configure('TEntry', fieldbackground='#F7DC6F')
    r = 0.05

    # Campos del formulario
    cedula_label = tk.Label(register_frame, text="ID Alumno", font=font, bd=0, bg='#F0F3F4')
    cedula_label.place(relx=r, rely=0.20, anchor='w')
    cedula_entry = ttk.Entry(register_frame, font=('Noto Sans', 8), width=63, style='TEntry')
    cedula_entry.place(relx=0.5, rely=0.24, anchor='center', width=403, height=a)

    cedula_rep_label = tk.Label(register_frame, text="Cedula Representante", font=font, bd=0, bg='#F0F3F4')
    cedula_rep_label.place(relx=r, rely=0.10, anchor='w')
    cedula_rep_entry = ttk.Entry(register_frame, font=('Noto Sans', 8), width=63, style='TEntry')
    cedula_rep_entry.place(relx=0.5, rely=0.14, anchor='center', width=403, height=a)

    nombre_label = tk.Label(register_frame, text="Nombre", font=font, bd=0, bg='#F0F3F4')
    nombre_label.place(relx=r, rely=0.30, anchor='w')
    nombre_entry = ttk.Entry(register_frame)
    nombre_entry.place(relx=0.5, rely=0.34, anchor='center', width=403, height=a)

    direccion_label = tk.Label(register_frame, text="Dirección", font=font, bd=0, bg='#F0F3F4')
    direccion_label.place(relx=r, rely=0.40, anchor='w')
    direccion_entry = ttk.Entry(register_frame)
    direccion_entry.place(relx=0.5, rely=0.44, anchor='center', width=403, height=a)

    telefono_label = tk.Label(register_frame, text="Teléfono", font=font, bd=0, bg='#F0F3F4')
    telefono_label.place(relx=r, rely=0.50, anchor='w')
    telefono_entry = ttk.Entry(register_frame)
    telefono_entry.place(relx=0.5, rely=0.54, anchor='center', width=403, height=a)

    curso_label = tk.Label(register_frame, text="Curso", font=font, bd=0, bg='#F0F3F4')
    curso_label.place(relx=r, rely=0.60, anchor='w')
    grados = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Sexto", "Séptimo", "Octavo", "Noveno", "4to año", "5to año"]
    curso_combobox = ttk.Combobox(register_frame, values=grados)
    curso_combobox.place(relx=0.5, rely=0.64, anchor='center', width=403, height=a)
    curso_combobox.set("seleccione un curso")

    matricula_label = tk.Label(register_frame, text="Matrícula", font=font, bd=0, bg='#F0F3F4')
    matricula_label.place(relx=r, rely=0.70, anchor='w')
    matricula_entry = ttk.Entry(register_frame) 
    matricula_entry.place(relx=0.5, rely=0.74, anchor='center', width=403, height=a)

    def clear_entries():
        cedula_entry.delete(0, 'end')
        cedula_rep_entry.delete(0, 'end')
        nombre_entry.delete(0, 'end')
        direccion_entry.delete(0, 'end')
        telefono_entry.delete(0, 'end')
        curso_combobox.set("seleccione un curso")
        matricula_entry.delete(0, 'end')

    def validar_campos_obligatorios():
        cedula = cedula_entry.get()
        nombre = nombre_entry.get()
        telefono = telefono_entry.get()
        if not cedula or not nombre or not telefono:
            messagebox.showwarning("Campos obligatorios", "Los campos Cédula, Nombre y Teléfono son obligatorios.")
            return False
        return True
    
    def consulta_cedula_representante(cedula_rep):
        query = "SELECT * FROM representante WHERE cedula = %s"
        cursor = mydb.cursor()
        cursor.execute(query, (cedula_rep,))
        result = cursor.fetchone()
        cursor.close()
        return result


    def process_entries():
        if not validar_campos_obligatorios():
            return

        cedula = cedula_entry.get()
        cedula_rep = cedula_rep_entry.get()
        cedula_rep = cedula_rep_entry.get()
        if not consulta_cedula_representante(cedula_rep):
            messagebox.showwarning("Representante no encontrado", "La cédula del representante no existe en la base de datos.")
            return
        nombre = nombre_entry.get()
        direccion = direccion_entry.get() or None
        telefono = telefono_entry.get()
        curso = curso_combobox.get()
        matricula = matricula_entry.get()

        query = "INSERT INTO alumno (cedula, cedula_representante, nombre, direccion, telefono, curso, matricula) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = mydb.cursor()
        try:
            cursor.execute(query, (cedula, cedula_rep, nombre, direccion, telefono, curso, matricula))
            mydb.commit()
            print("Registro guardado con éxito")
            clear_entries()  # Limpia los campos después de guardar
            messagebox.showinfo("Información", "Registro de alumno guardado con éxito")
        except Exception as e:
            print(f"Error al guardar el registro: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el registro: {e}")
        finally:
            cursor.close()

    guardar_button = tk.Button(register_frame, text="Guardar", bg='DeepSkyBlue2', width=12, height=1, bd=0, font=font,
                               command=process_entries)
    guardar_button.place(relx=0.38, rely=0.95, anchor='sw')

    notebook.select(tab_registro)
    notebook.lift()
    print("Pestaña de registro de alumno abierta")
