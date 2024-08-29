import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from module_funciones import close_button, search_button, error_cedula, name_data, mail_data, phone_data, birth_data, dir_data, genero_data, ig_data, consulta_cedula, verificarCedula, insertClientes
from client import Client
import module_access
import module_person
from databaseManager import mydb
from datetime import datetime

def registro_click(main_app, main_frame, event=None):
    """
    Crea la pestaña de registro.
    """
    notebook = ttk.Notebook(main_frame, style='TNotebook')
    notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

    tab_registro = ttk.Frame(notebook)
    notebook.add(tab_registro, text="Registro")

    a = 26
    font = ('noto sans', 10, 'bold')
    register_frame = tk.Frame(tab_registro, bd=2, relief='groove')
    register_frame.config(bg='#F0F3F4')
    register_frame.place(relx=0.5, rely=0.45, width=458, height=640, anchor='center')
    close_button(register_frame, notebook, tab_registro)

    def remove_ci(event):
        event.widget.delete(0, 'end')

    def open_huella_tab():
        huella_tab = ttk.Frame(notebook)
        notebook.add(huella_tab, text="Huella")
        notebook.select(huella_tab)
        close_button(register_frame, notebook, huella_tab)
        print("fingerprints tab opened")
        huella_frame = tk.Frame(huella_tab, bd=2, relief='groove')
        huella_frame.config(bg='#F0F3F4')
        huella_frame.place(relx=0.5, rely=0.5, width=448, height=540, anchor='center')
        photo = main_app.load_and_customize_image("fingerprint.jpg")
        image_label = tk.Label(huella_frame, image=photo)
        image_label.image = photo
        image_label.place(relx=0.5, rely=0.3, anchor='center')

        def go_back():
            notebook.select(notebook.index(huella_tab) - 1)
            notebook.forget(huella_tab)

        back_button = tk.Button(huella_frame, text="Volver", bg='#F9E79F', width=17, height=2, bd=0, font=font, command=go_back)
        back_button.place(relx=0.2, rely=0.9, anchor='center')

        def open_foto_tab():
            foto_tab = ttk.Frame(notebook)
            notebook.add(foto_tab, text="Foto")
            notebook.select(foto_tab)
            print(" Photo tab opened")
            foto_frame = tk.Frame(foto_tab, bd=2, relief='groove')
            foto_frame.config(bg='#F0F3F4')
            foto_frame.place(relx=0.5, rely=0.5, width=448, height=540, anchor='center')
            photo = main_app.load_and_customize_image("informes2.jpg")
            image_label = tk.Label(foto_frame, image=photo)
            image_label.image = photo
            image_label.place(relx=0.5, rely=0.3, anchor='center')
            cargar_button = tk.Button(foto_frame, text="Cargar", bg='#F9E79F', width=12, height=2, bd=0, font=font, command=None)
            cargar_button.place(relx=0.3, rely=0.6, anchor='center')
            capturar_button = tk.Button(foto_frame, text="Capturar", bg='#F9E79F', width=12, height=2, bd=0, font=font, command=None)
            capturar_button.place(relx=0.7, rely=0.6, anchor='center')

            if open_huella_tab is not None:
                regresar_button = tk.Button(foto_frame, text="Regresar", bg='#F9E79F', width=17, height=2, bd=0, font=font, command=lambda: [notebook.select(huella_tab), notebook.forget(foto_tab)])
                regresar_button.place(relx=0.2, rely=0.9, anchor='center')
            guardar_button = tk.Button(foto_frame, text="Guardar", bg='#F9E79F', width=17, height=2, bd=0, font=font, command=lambda: [notebook.select(tab_registro), notebook.forget(huella_tab), notebook.forget(foto_tab), clear_entries()])
            guardar_button.place(relx=0.8, rely=0.9, anchor='center')
            print("el boton de guardar fue presionado")
            close_button(huella_frame, notebook, foto_tab)

        next_button = tk.Button(huella_frame, text="Siguiente", bg='#F9E79F', width=17, height=2, bd=0, font=font, command=open_foto_tab)
        next_button.place(relx=0.8, rely=0.9, anchor='center')

        capturar_button = tk.Button(huella_frame, text="Capturar", bg='#F9E79F', width=17, height=2, bd=0, font=font, command=None)
        capturar_button.place(relx=0.5, rely=0.55, anchor='center')

    style = ttk.Style()
    style.configure('TEntry', fieldbackground='#F7DC6F')
    r = 0.05
    ci_label = tk.Label(register_frame, text="CEDULA", font=font, bd=0, bg='#F0F3F4')
    ci_label.place(relx=r, rely=0.07, anchor='w')
    ci_entry = ttk.Entry(register_frame, font=('Noto Sans', 8), width=63, style='TEntry')
    ci_entry.insert(0, 'Type here')
    ci_entry.bind('<FocusIn>', remove_ci)
    ci_entry.bind("<KP_Enter>", lambda event: fill_entries_reg())
    ci_entry.bind("<Return>", lambda event: fill_entries_reg())
    ci_entry.place(relx=0.5, rely=0.11, anchor='center', width=403, height=a)
    cedulaFact = None

    def fill_entries_reg():
        global cedulaFact
        cedulaFact = ci_entry.get()
        if error_cedula(cedulaFact):
            name_entry.delete(0, 'end')
            name_entry.insert(0, name_data(cedulaFact))
            name_entry.config(state='normal')
            apellido_entry.delete(0, 'end')
            apellido_entry.insert(0, name_data(cedulaFact))
            correo_entry.delete(0, 'end')
            correo_entry.insert(0, mail_data(cedulaFact))
            correo_entry.config(state='normal')
            tlf_entry.delete(0, 'end')
            tlf_entry.insert(0, phone_data(cedulaFact))
            tlf_entry.config(state='normal')
            birth_entry.delete(0, 'end')
            fecha_nacimiento = birth_data(cedulaFact)
            birth_entry.set_date(fecha_nacimiento)
            dir_entry.delete(0, 'end')
            dir_entry.insert(0, dir_data(cedulaFact))
            gender_combobox.delete(0, 'end')
            gender_combobox.set(genero_data(cedulaFact))
            ig_entry.delete(0, 'end')
            ig_entry.insert(0, ig_data(cedulaFact))
            return cedulaFact

    def update_registro():
        print("Actualiza registro")
        cedula = ci_entry.get()
        nombre = name_entry.get()
        apellido = apellido_entry.get()
        correo = correo_entry.get()
        telefono = tlf_entry.get()
        fecha_nacimiento = birth_entry.get()
        direccion = dir_entry.get()
        instagram = ig_entry.get()
        genero = gender_combobox.get()
        nivel_acceso = access_level_comb.get()

        query = (
            "UPDATE clientes "
            "SET nombre = %s, apellido = %s, genero = %s, email = %s, telefono = %s, "
            "fechaNac = %s, direccion = %s, socialMedia = %s, acceso = %s "
            "WHERE cedula = %s"
        )
        cursor = mydb.cursor()
        try:
            cursor.execute(query, (nombre, apellido, genero, correo, telefono, fecha_nacimiento, direccion, instagram, nivel_acceso, cedula))
            mydb.commit()
            print("Registro actualizado con éxito")
        except Exception as e:
            print(f"Error al actualizar el registro: {e}")
        finally:
            cursor.close()

    search_button(register_frame, command=fill_entries_reg, relx=0.892, rely=0.093)

    name_label = tk.Label(register_frame, text="Nombre", font=font, bd=0, bg='#F0F3F4')
    name_label.place(relx=r, rely=0.16, anchor='w')
    name_entry = ttk.Entry(register_frame)
    name_entry.place(relx=0.5, rely=0.20, anchor='center', width=403, height=a)
    
    apellido_label = tk.Label(register_frame, text="Apellido", font=font, bd=0, bg='#F0F3F4')
    apellido_label.place(relx=r, rely=0.25, anchor='w')
    apellido_entry = ttk.Entry(register_frame)
    apellido_entry.place(relx=0.5, rely=0.29, anchor='center', width=403, height=a)

    correo_label = tk.Label(register_frame, text="CORREO", font=font, bd=0, bg='#F0F3F4')
    correo_label.place(relx=r, rely=0.34, anchor='w')
    correo_entry = ttk.Entry(register_frame)
    correo_entry.place(relx=0.5, rely=0.38, anchor='center', width=403, height=a)

    tlf_label = tk.Label(register_frame, text="TELEFONO", font=font, bd=0, bg='#F0F3F4')
    tlf_label.place(relx=r, rely=0.43, anchor='w')
    tlf_entry = ttk.Entry(register_frame)
    tlf_entry.place(relx=0.5, rely=0.47, anchor='center', width=403, height=a)

    birth_label = tk.Label(register_frame, text=" FECHA DE NACIMIENTO", font=font, bd=0, bg='#F0F3F4')
    birth_label.place(relx=r, rely=0.52, anchor='w')
    birth_entry = DateEntry(register_frame, date_pattern='dd/mm/yyyy')
    birth_entry.place(relx=0.5, rely=0.56, anchor='center', width=403, height=a)

    dir_label = tk.Label(register_frame, text="DIRECCION", font=font, bd=0, bg='#F0F3F4')
    dir_label.place(relx=r, rely=0.61, anchor='w')
    dir_entry = ttk.Entry(register_frame)
    dir_entry.place(relx=0.5, rely=0.65, anchor='center', width=403, height=a)

    ig_label = tk.Label(register_frame, text="USUARIO INSTAGRAM", font=font, bd=0, bg='#F0F3F4')
    ig_label.place(relx=r, rely=0.70, anchor='w')
    ig_entry = ttk.Entry(register_frame)
    ig_entry.place(relx=0.5, rely=0.74, anchor='center', width=403, height=a)

    def remove_placeholder(event):
        current_value = gender_combobox.get()
        if current_value == 'Select':
            gender_combobox.set('')

    gen_label = tk.Label(register_frame, text="GENERO", font=font, bd=0, bg='#F0F3F4')
    gen_label.place(relx=r, rely=0.79, anchor='w')
    gender_combobox = ttk.Combobox(register_frame, values=["Masculino", "Femenino"], width=63, font=('Noto Sans', 8))
    gender_combobox.insert(0, 'Select')
    gender_combobox.bind('<FocusIn>', remove_placeholder)
    gender_combobox.place(relx=0.5, rely=0.83, anchor='center')

    def get_privilege_group_names():
        privilege_groups = module_access.get_privilege_groups(module_access.external_signature_privilege_list)
        # Excluir el nivel de acceso "moroso"
        return {group['privilegeGroupName']: group['privilegeGroupId'] for group in privilege_groups if group['privilegeGroupName'].lower() != 'morosos'} if privilege_groups else {}

    privilege_group_mapping = get_privilege_group_names()

    access_level_label = tk.Label(register_frame, text="NIVEL DE ACCESO", font=font, bd=0, bg='#F0F3F4')
    access_level_label.place(relx=r, rely=0.88, anchor='w')
    access_level_comb = ttk.Combobox(register_frame, values=list(privilege_group_mapping.keys()), width=63, font=('Noto Sans', 8))
    access_level_comb.insert(0, 'Seleccione el nivel de acceso')
    access_level_comb.place(relx=0.5, rely=0.92, anchor='center')
    access_level_comb.config(state="disabled")
    access_level_comb.bind("<Button-1>", lambda event: solicitar_clave())

    def solicitar_clave():
        def verificar_clave():
            clave_ingresada = clave_entry.get()
            clave_correcta = "1234"  # Reemplaza esto con tu clave segura

            if clave_ingresada == clave_correcta:
                clave_window.destroy()
                access_level_comb.config(state="readonly")
                access_level_comb.unbind("<Button-1>")  # Quitar el bind para permitir la selección
                access_level_comb.event_generate('<Button-1>')  # Reenviar el evento para abrir el combobox
                registrar_clave_usada()
            else:
                messagebox.showerror("Error", "Clave incorrecta")

        clave_window = tk.Toplevel(register_frame)
        clave_window.title("Verificación de Clave")
        clave_window.geometry("300x150")
        clave_window.resizable(False, False)
        clave_window.iconbitmap("gym.ico")
        
        # Centrar la ventana en la pantalla
        ancho_ventana = 300
        alto_ventana = 150
        x_ventana = (clave_window.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y_ventana = (clave_window.winfo_screenheight() // 2) - (alto_ventana // 2)
        clave_window.geometry(f"{ancho_ventana}x{alto_ventana}+{x_ventana}+{y_ventana}")

        tk.Label(clave_window, text="Ingrese la clave:").pack(pady=10)
        clave_entry = tk.Entry(clave_window, show="*")
        clave_entry.pack(pady=5)
        tk.Button(clave_window, text="Verificar", command=verificar_clave).pack(pady=10)


    def registrar_clave_usada():
        with open("registro_claves.txt", "a") as file:
            file.write(f"Clave usada el {datetime.now()}\n")

    def clear_entries():
        ci_entry.delete(0, 'end')
        dir_entry.delete(0, 'end')
        name_entry.delete(0, 'end')
        apellido_entry.delete(0, 'end')
        correo_entry.delete(0, 'end')
        tlf_entry.delete(0, 'end')
        ig_entry.delete(0, 'end')

    def process_entries(name_entry, apellido_entry, ci_entry, birth_entry, dir_entry, gender_combobox, tlf_entry, correo_entry, ig_entry, access_level_comb):
        name = name_entry.get()
        apellido = apellido_entry.get()
        ci = ci_entry.get()
        birth_date = birth_entry.get_date()
        formatted_date = birth_date.strftime('%Y-%m-%d')
        dir = dir_entry.get()
        gender = gender_combobox.get()
        tlf = tlf_entry.get()
        correo = correo_entry.get()
        ig = ig_entry.get()
        access_level = access_level_comb.get()

        user = Client(name, apellido, ci, gender, formatted_date, dir, tlf, correo, ig, access_level)
        print(name, apellido, ci, gender, formatted_date, dir, tlf, correo, ig)
        if verificarCedula(user.cedula) == True:
            insertClientes(user)
        else:
            print("la cedula, email o telefono ya estan registrados")

# Función para procesar los datos ingresados y registrarlos en la base de datos
    def actualizar_registrar_save(cedula):
        global cedulaFact
        cedulaFact = ci_entry.get()
        cedula = cedulaFact
        nombre = name_entry.get()
        apellido = apellido_entry.get()
        external_signature_add = "IfKuEOfGzQUDZ1oX6uRLkLVYRkxWS4v+8D5sLwiGNMU="
        external_signature_list = "a5qgFmGbW4U/PM54UjbV1Zm6xpQXxw/spdAwI3R9XRo="
        external_signature_person = "I+scEUWORP/phvzwhFlerMauoVECMIGTuLLiZxc1NOc="

        if consulta_cedula(cedula):
            print("se modifico el registro")
            update_registro()
            messagebox.showinfo("Información", "Se modificó el registro con éxito")
        else:
            print("Cédula no encontrada en la base de datos local, registrando entradas...")
            process_entries(name_entry, apellido_entry, ci_entry, birth_entry, dir_entry, gender_combobox, tlf_entry, correo_entry, ig_entry, access_level_comb)

        # Verificar si la persona ya existe en Hikvision
        person_id = module_person.get_person_id_by_code(cedula, external_signature_person)
        if not person_id:
            # Si la persona no existe en Hikvision, agregarla
            print("Persona no encontrada en Hikvision, agregando...")
            person_result = module_person.add_person(cedula, nombre, apellido, external_signature_add)
            if person_result:
                if isinstance(person_result, str):
                    person_id = person_result
                    print(f"Persona agregada con ID {person_id}")
                else:
                    print("Persona agregada, pero no se pudo obtener el ID")
            else:
                messagebox.showerror("Error", "No se pudo agregar la persona en Hikvision")
                return
        else:
            print("Persona ya existe en Hikvision con ID:", person_id)

        # Asignar nivel de acceso
        if person_id:
            selected_access_level = access_level_comb.get()
            if selected_access_level in privilege_group_mapping:
                privilege_group_id = privilege_group_mapping[selected_access_level]
                module_access.assign_access_level(person_id, privilege_group_id)
                messagebox.showinfo("Éxito", "Usuario registrado y nivel de acceso asignado correctamente")
            else:
                messagebox.showerror("Error", "Nivel de acceso seleccionado no válido")

        clear_entries()

    guardar_button = tk.Button(notebook, text="Guardar", bg='#F9E79F', width=13, height=1, bd=0, font=font,
                               command=lambda: actualizar_registrar_save(cedulaFact))
    guardar_button.place(relx=0.38, rely=0.88, anchor='sw')

    fp_button = tk.Button(notebook, text="Huella--->", font=font, bg='#F9E79F', width=13, height=1, bd=0, 
                          command=open_huella_tab)
    fp_button.place(relx=0.62, rely=0.88, anchor='se')
    notebook.select(tab_registro)
    notebook.lift()
    print("Pestaña de registro abierta")
