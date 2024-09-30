"""
Este script se encarga de registrar a un Representante en la base de datos.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from databaseManager import mydb
from datetime import datetime

def remove_ci(event):
    """
    Elimina el texto de marcador de posición en el campo de entrada de la cédula.
    """
    if event.widget.get() == 'Type here':
        event.widget.delete(0, tk.END)

def registro_click(main_app, main_frame, event=None):
    """
    Crea la pestaña de registro.
    """
    notebook = ttk.Notebook(main_frame, style='TNotebook')
    notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

    tab_registro = ttk.Frame(notebook)
    notebook.add(tab_registro, text="Registro Representante")

    a = 26
    font = ('noto sans', 10, 'bold')
    register_frame = tk.Frame(tab_registro, bd=2, relief='groove')
    register_frame.config(bg='#F0F3F4')
    register_frame.place(relx=0.5, rely=0.48, width=450, height=480, anchor='center')

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
    ci_label = tk.Label(register_frame, text="Cedula Representante", font=font, bd=0, bg='#F0F3F4')
    ci_label.place(relx=r, rely=0.10, anchor='w')

    ci_entry = ttk.Entry(register_frame, font=('Noto Sans', 8), width=63, style='TEntry')
    ci_entry.insert(0, 'Type here')
    ci_entry.bind('<FocusIn>', remove_ci)
    ci_entry.bind("<KP_Enter>", lambda event: fill_entries_reg())
    ci_entry.bind("<Return>", lambda event: fill_entries_reg())
    ci_entry.place(relx=0.5, rely=0.15, anchor='center', width=403, height=a)

    cedulaFact = None

    def consulta_cedula(cedula):
        query = "SELECT * FROM representante WHERE cedula = %s"
        cursor = mydb.cursor()
        cursor.execute(query, (cedula,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def fill_entries_reg():
        global cedulaFact
        cedulaFact = ci_entry.get()

        if not cedulaFact.strip():  # Verifica que la cédula no esté vacía
            messagebox.showwarning("Campo vacío", "Por favor, ingrese la cédula del representante.")
            return

        result = consulta_cedula(cedulaFact)
        if result:
            # Rellenar los campos con la información obtenida
            name_entry.delete(0, 'end')
            name_entry.insert(0, result[1])  # Nombre

            dir_entry.delete(0, 'end')
            dir_entry.insert(0, result[2])  # Dirección

            tlf_entry.delete(0, 'end')
            tlf_entry.insert(0, result[3])  # Teléfono

            birth_entry.set_date(result[4])  # Fecha de Nacimiento

            correo_entry.delete(0, 'end')
            correo_entry.insert(0, result[5])  # Correo

            print("Datos de la cédula encontrados y cargados en el formulario.")
        else:
            messagebox.showwarning("No encontrado", "El registro con la cédula especificada no fue encontrado.")
            print("Registro no encontrado en la base de datos")

    def update_registro():
        print("Actualiza registro")
        cedula = ci_entry.get()
        nombre = name_entry.get()
        correo = correo_entry.get()
        telefono = tlf_entry.get()
        fecha_nacimiento = birth_entry.get_date() if birth_entry.get_date() else None
        direccion = dir_entry.get()

        query = (
            "UPDATE representante "
            "SET nombre = %s, direccion = %s, telefono = %s, birth = %s, correo = %s "
            "WHERE cedula = %s"
        )
        cursor = mydb.cursor()
        try:
            cursor.execute(query, (nombre, direccion, telefono, fecha_nacimiento, correo, cedula))
            mydb.commit()
            print("Registro actualizado con éxito")
        except Exception as e:
            print(f"Error al actualizar el registro: {e}")
        finally:
            cursor.close()

    search_button = tk.Button(register_frame, text="Buscar", font=('noto sans', 9, 'bold'), bg='DeepSkyBlue2', width=6, height=1, bd=0, command=fill_entries_reg)
    search_button.place(relx=0.829, rely=0.1724, anchor='sw')
    
    name_label = tk.Label(register_frame, text="Nombre", font=font, bd=0, bg='#F0F3F4')
    name_label.place(relx=r, rely=0.23, anchor='w')
    name_entry = ttk.Entry(register_frame)
    name_entry.place(relx=0.5, rely=0.28, anchor='center', width=403, height=a)

    correo_label = tk.Label(register_frame, text="CORREO", font=font, bd=0, bg='#F0F3F4')
    correo_label.place(relx=r, rely=0.36, anchor='w')
    correo_entry = ttk.Entry(register_frame)
    correo_entry.place(relx=0.5, rely=0.41, anchor='center', width=403, height=a)

    tlf_label = tk.Label(register_frame, text="TELEFONO", font=font, bd=0, bg='#F0F3F4')
    tlf_label.place(relx=r, rely=0.49, anchor='w')
    tlf_entry = ttk.Entry(register_frame)
    tlf_entry.place(relx=0.5, rely=0.54, anchor='center', width=403, height=a)

    birth_label = tk.Label(register_frame, text="FECHA DE NACIMIENTO", font=font, bd=0, bg='#F0F3F4')
    birth_label.place(relx=r, rely=0.62, anchor='w')
    birth_entry = DateEntry(register_frame, date_pattern='dd/mm/yyyy')
    birth_entry.place(relx=0.5, rely=0.67, anchor='center', width=403, height=a)

    dir_label = tk.Label(register_frame, text="DIRECCION", font=font, bd=0, bg='#F0F3F4')
    dir_label.place(relx=r, rely=0.75, anchor='w')
    dir_entry = ttk.Entry(register_frame)
    dir_entry.place(relx=0.5, rely=0.80, anchor='center', width=403, height=a)

    def clear_entries():
        ci_entry.delete(0, 'end')
        dir_entry.delete(0, 'end')
        name_entry.delete(0, 'end')
        correo_entry.delete(0, 'end')
        tlf_entry.delete(0, 'end')
        birth_entry.set_date(datetime.now())  # Opcional, restablece la fecha al día de hoy

    def validar_campos_obligatorios():
        cedula = ci_entry.get()
        nombre = name_entry.get()
        telefono = tlf_entry.get()
        if not cedula or not nombre or not telefono:
            messagebox.showwarning("Campos obligatorios", "Los campos Cédula, Nombre y Teléfono son obligatorios.")
            return False
        return True

    def process_entries():
        if not validar_campos_obligatorios():
            return

        cedula = ci_entry.get()
        nombre = name_entry.get()
        direccion = dir_entry.get() or None
        telefono = tlf_entry.get()
        fecha_nacimiento = birth_entry.get_date().strftime('%Y-%m-%d') if birth_entry.get_date() else None
        correo = correo_entry.get() or None

        query = "INSERT INTO representante (cedula, nombre, direccion, telefono, birth, correo) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = mydb.cursor()
        try:
            cursor.execute(query, (cedula, nombre, direccion, telefono, fecha_nacimiento, correo))
            mydb.commit()
            print("Registro guardado con éxito")
            clear_entries()  # Limpia los campos después de guardar
            
        except Exception as e:
            print(f"Error al guardar el registro: {e}")
        finally:
            cursor.close()

    def actualizar_registrar_save(cedula):
        global cedulaFact
        cedulaFact = ci_entry.get()
        cedula = cedulaFact

        if consulta_cedula(cedula):
            print("Se modificó el registro")
            update_registro()
            messagebox.showinfo("Información", "Se modificó el registro con éxito")
            clear_entries()
        else:
            print("Cédula no encontrada en la base de datos local, registrando entradas...")
            process_entries()
            messagebox.showinfo("Información", "Registro guardado con éxito")
            clear_entries()
            

    guardar_button = tk.Button(register_frame, text="Guardar", bg='DeepSkyBlue2', width=12, height=1, bd=0, font=font,
                               command=lambda: actualizar_registrar_save(cedulaFact))
    guardar_button.place(relx=0.38, rely=0.95, anchor='sw')

    notebook.select(tab_registro)
    notebook.lift()
    print("Pestaña de registro abierta")
