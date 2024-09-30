"""
Este script se encarga de gestionar el registro y búsqueda de alumnos en la base de datos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from databaseManager import mydb

def registro_alumno_click(main_app, main_frame, event=None):
    """
    Crea la pestaña de registro para los alumnos.
    """
    notebook = ttk.Notebook(main_frame, style='TNotebook')
    notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

    tab_registro = ttk.Frame(notebook)
    notebook.add(tab_registro, text="Gestión de Alumnos")

    font = ('noto sans', 9, 'bold')
    register_frame = tk.Frame(tab_registro, bd=2, relief='groove', bg='#F0F3F4')
    register_frame.place(relx=0.5, rely=0.5, width=490, height=570, anchor='center')

    def close_tab():
        notebook.forget(tab_registro)
        notebook.place_forget()
        main_frame.lift()
        main_frame.focus_force()
        main_app.root.update_idletasks()
        main_app.root.deiconify()
        main_app.root.focus_force()
        print("Formulario de gestión cerrado")

    close_button = tk.Button(register_frame, text="X", font=font, bg='#F0F3F4', bd=0, command=close_tab)
    close_button.place(relx=0.97, rely=0.01, anchor='ne')

    style = ttk.Style()
    style.configure('TEntry', fieldbackground='#F7DC6F')

    # Variables para los campos
    campos = [
        {'label': 'ID Alumno', 'var': tk.StringVar(), 'name': 'cedula'},
        {'label': 'Cédula Representante', 'var': tk.StringVar(), 'name': 'cedula_rep'},
        {'label': 'Nombre', 'var': tk.StringVar(), 'name': 'nombre'},
        {'label': 'Fecha de Nacimiento', 'var': tk.StringVar(), 'name': 'fecha_nacimiento'},
        {'label': 'Curso', 'var': tk.StringVar(), 'name': 'curso'},
        {'label': 'Dirección', 'var': tk.StringVar(), 'name': 'direccion'},
        {'label': 'Teléfono', 'var': tk.StringVar(), 'name': 'telefono'},
        {'label': 'Género', 'var': tk.StringVar(), 'name': 'genero'},
        {'label': 'Email', 'var': tk.StringVar(), 'name': 'email'},
    ]

    # Creación de campos dinámicamente
    for idx, campo in enumerate(campos):
        y_position = 0.11 + idx * 0.085
        tk.Label(register_frame, text=campo['label'], font=font, bd=0, bg='#F0F3F4').place(relx=0.05, rely=y_position, anchor='w')

        if campo['name'] == 'fecha_nacimiento':
            # Permitir escribir o seleccionar fecha
            campo['widget'] = DateEntry(register_frame, textvariable=campo['var'], date_pattern='yyyy-mm-dd')
            campo['widget'].configure(width=62)
        elif campo['name'] == 'curso':
            grados = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Sexto",
                      "Séptimo", "Octavo", "Noveno", "4to año", "5to año"]
            campo['widget'] = ttk.Combobox(register_frame, values=grados, textvariable=campo['var'])
            campo['widget'].set("Seleccione un curso")
        elif campo['name'] == 'genero':
            opciones_genero = ["Masculino", "Femenino", "Otro"]
            campo['widget'] = ttk.Combobox(register_frame, values=opciones_genero, textvariable=campo['var'])
            campo['widget'].set("Seleccione género")
        else:
            campo['widget'] = ttk.Entry(register_frame, textvariable=campo['var'])

        campo['widget'].place(relx=0.5, rely=y_position + 0.04, anchor='center', width=450, height=25)

    # Botón "Buscar" en la misma línea que "ID Alumno"
    buscar_button = tk.Button(register_frame, text="Buscar", bg='DeepSkyBlue2', width=6, height=1, bd=1, font=font,
                              command=lambda: buscar_alumno(campos[0]['var'].get()))
    buscar_button.place(relx=0.895, rely=0.152, anchor='center')

    # Funciones auxiliares
    def clear_entries():
        for campo in campos:
            campo['var'].set('')
        # Restablecer el texto del botón a "Guardar"
        accion_button.config(text="Guardar")
        accion_button.update()

    def validar_campos_obligatorios():
        obligatorios = ['cedula', 'cedula_rep', 'nombre', 'fecha_nacimiento', 'curso']
        for campo in campos:
            if campo['name'] in obligatorios and not campo['var'].get():
                messagebox.showwarning("Campos obligatorios", f"El campo {campo['label']} es obligatorio.")
                return False
        return True
    
    def verificar_cedula_representante(event=None):
        """
        Verifica si la cédula del representante está registrada.
        Si no está registrada, muestra una advertencia y mantiene el enfoque en el campo.
        """
        cedula_rep = campos[1]['var'].get()  # Obtener el valor de la cédula del representante
        if not cedula_rep.strip():  # Verifica que el campo no esté vacío
            messagebox.showwarning("Campo vacío", "Por favor, ingrese la cédula del representante.")
            campos[1]['widget'].focus_set()  # Mantiene el enfoque en el campo
            return

        result = consulta_cedula_representante(cedula_rep)
        if not result:
            messagebox.showwarning(
                "Representante no encontrado",
                "La cédula del representante no está registrada en la base de datos. Por favor, verifique e intente de nuevo."
            )
            campos[1]['widget'].focus_set()  # Mantiene el enfoque en el campo si no se encuentra la cédula


    def consulta_cedula_representante(cedula_rep):
        query = "SELECT * FROM representante WHERE cedula = %s"
        cursor = mydb.cursor()
        cursor.execute(query, (cedula_rep,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    # Enlaza la verificación al campo de cédula del representante
    campos[1]['widget'].bind('<FocusOut>', verificar_cedula_representante)

    def buscar_alumno(cedula):
        if not cedula:
            messagebox.showwarning("Buscar Alumno", "Por favor, ingrese el ID del alumno para buscar.")
            return
        query = "SELECT * FROM alumno WHERE cedula = %s"
        cursor = mydb.cursor()
        cursor.execute(query, (cedula,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            # Rellenar los campos con la información obtenida
            for idx, campo in enumerate(campos):
                if idx < len(result):
                    campo['var'].set(result[idx])
            messagebox.showinfo("Búsqueda Exitosa", "Alumno encontrado y cargado en el formulario.")
            # Cambiar el texto del botón a "Actualizar"
            accion_button.config(text="Actualizar")
            accion_button.update()
        else:
            messagebox.showwarning("No encontrado", "Alumno no registrado.")
            

    def process_entries():
        if not validar_campos_obligatorios():
            return

        data = [campo['var'].get() or None for campo in campos]

        # Validar representante
        cedula_rep = campos[1]['var'].get()
        if not consulta_cedula_representante(cedula_rep):
            messagebox.showwarning("Representante no encontrado", "La cédula del representante no existe en la base de datos.")
            return

        cursor = mydb.cursor()
        try:
            cedula = campos[0]['var'].get()
            # Verificar si el alumno ya existe
            query_exist = "SELECT * FROM alumno WHERE cedula = %s"
            cursor.execute(query_exist, (cedula,))
            exists = cursor.fetchone()

            if exists:
                # Actualizar registro existente
                query_update = """
                UPDATE alumno SET cedula_representante=%s, nombre=%s, fecha_nacimiento=%s, curso=%s,
                direccion=%s, telefono=%s, genero=%s, email=%s WHERE cedula=%s
                """
                cursor.execute(query_update, data[1:] + [data[0]])
                mydb.commit()
                messagebox.showinfo("Información", "Registro de alumno actualizado con éxito.")
            else:
                # Insertar nuevo registro
                query_insert = """
                INSERT INTO alumno (cedula, cedula_representante, nombre, fecha_nacimiento, curso, direccion, telefono, genero, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_insert, data)
                mydb.commit()
                messagebox.showinfo("Información", "Registro de alumno guardado con éxito.")
            clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar la acción: {e}")
        finally:
            cursor.close()

    # Botón de acción (Guardar/Actualizar)
    accion_button = tk.Button(register_frame, text="Guardar", bg='DeepSkyBlue2', width=12, height=1, bd=1, font=font,
                              command=process_entries)
    accion_button.place(relx=0.25, rely=0.97, anchor='sw')

    # Botón "Limpiar"
    limpiar_button = tk.Button(register_frame, text="Limpiar", bg='orange', width=12, height=1, bd=1, font=font,
                               command=clear_entries)
    limpiar_button.place(relx=0.6, rely=0.97, anchor='sw')

    notebook.select(tab_registro)
    notebook.lift()
    print("Pestaña de gestión de alumno abierta")
