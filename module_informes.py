import os
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from databaseManager import *
from functools import partial

global cedulaFact

# Funciones de informes botón 1
def informe_click(main_frame):
    notebook = ttk.Notebook(main_frame, style='TNotebook')
    notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Informes")
    close_button(main_frame, notebook, tab)  # Crea un botón para cerrar la pestaña
    a = 27
    font = ('noto sans', 9, 'bold')
    iframe = tk.Frame(tab, bd=2, relief='groove')
    iframe.config(bg='#F0F3F4')
    iframe.place(relx=0.5, rely=0.5, width=713, height=754, anchor='center')
    r = 0.07
    w = 475
    relx = 0.4
    # CAMPO 1
    ci = tk.Label(iframe, text="CEDULA", font=font, bd=0, bg='#F0F3F4')
    ci.place(relx=r, rely=0.1, anchor='w')
    ci_entry = ttk.Entry(iframe, font=('Noto Sans', 9, "bold"), width=w, style='TEntry')
    ci_entry.bind("<KP_Enter>", lambda event: fill_entries2())  # Llama a la función fill_entries cuando se presiona Enter en el teclado numérico
    ci_entry.bind("<Return>", lambda event: fill_entries2())  # Llama a la función fill_entries cuando se presiona Enter
    ci_entry.place(relx=relx, rely=0.15, anchor='center', width=w, height=a)

    # Define una función para llenar las entradas con datos de la base de datos
    def fill_entries2():
        cedulaFact = ci_entry.get()
        error_cedula(cedulaFact)
        name_entry.delete(0, 'end')
        name_entry.insert(0, name_data(cedulaFact))
        name_entry.config(state='normal')  # Hacer que el widget de entrada no sea editable
        tlf_entry.delete(0, 'end')
        tlf_entry.insert(0, phone_data(cedulaFact))
        tlf_entry.config(state='normal')

        # Nueva consulta SQL para verificar la existencia del usuario
        cedula = ci_entry.get()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM clientes WHERE cedula = %s)", (cedula,))
        usuario_existe = cursor.fetchone()[0]

        if usuario_existe:
            cursor.execute("SELECT f.id, f.fechaPago, f.suscripcion, f.zelle, f.usdt, f.efectivo, f.bolivares, c.acceso "
                           "FROM facturacion f JOIN clientes c ON f.cedula = c.cedula WHERE f.cedula = %s", (cedula,))
            rows = cursor.fetchall()

            # Limpiar el treeview antes de insertar nuevas filas
            for i in treeview.get_children():
                treeview.delete(i)

            # Verificar si se encontraron filas y luego insertarlas en el treeview
            if rows:
                for row in rows:
                    treeview.insert('', 'end', values=row)
            else:
                messagebox.showinfo("Información", "No se encontraron datos para la cédula proporcionada.")
        else:
            messagebox.showinfo("Información", "El usuario no existe en la base de datos.")

    # BOTON SEARCH IMAGE -- # Botón de llamada
    search_button(iframe, fill_entries2, relx=0.703, rely=0.135)  # Llamar a la función search_button, pasando el frame y la función command

    # CAMPO 2
    name_fact = tk.Label(iframe, text="NOMBRE DEL CLIENTE", font=font, bd=0, bg='#F0F3F4')
    name_fact.place(relx=r, rely=0.20, anchor='w')
    name_entry = ttk.Entry(iframe, font=font, width=w, style='TEntry')
    name_entry.insert(0, 'Type here')
    name_entry.place(relx=relx, rely=0.25, anchor='center', width=w, height=a)

    # CAMPO 3
    tlf_fact = tk.Label(iframe, text="TELEFONO", font=font, bd=0, bg='#F0F3F4')
    tlf_fact.place(relx=r, rely=0.3, anchor='w')
    tlf_entry = ttk.Entry(iframe, font=font, width=w, style='TEntry')
    tlf_entry.insert(0, 'Type here')
    tlf_entry.place(relx=relx, rely=0.35, anchor='center', width=w, height=a)

    # Crea un botón de registro y colócalo en el marco del formulario
    fp_button = tk.Button(iframe, text="Imprimir --->", font=font, bg='#F9E79F', width=15, height=1, bd=0,
                          command=lambda: print("ventana de Imprimir"))
    fp_button.place(relx=0.96, rely=0.96, anchor='se')
    notebook.select(tab)  # Selecciona la pestaña recién creada
    notebook.lift()  # Trae el notebook al frente
    print("Informe historico de pagos")

    # Crea el Treeview
    treeview = ttk.Treeview(iframe)
    treeview.place(relx=0.50, rely=0.65, width=624, height=377, anchor='center')
    # Configura las columnas del Treeview
    treeview['columns'] = ('id', 'fechaPago', 'motivoPago', 'zelle', 'usdt', 'efectivo', 'bolivares', 'acceso')
    treeview.column('#0', width=0, stretch='no')
    treeview.column('id', anchor='center', width=30)
    treeview.column('fechaPago', anchor='center', width=30)
    treeview.column('motivoPago', anchor='center', width=30)
    treeview.column('zelle', anchor='center', width=30)
    treeview.column('usdt', anchor='center', width=30)
    treeview.column('efectivo', anchor='center', width=30)
    treeview.column('bolivares', anchor='center', width=30)
    treeview.column('acceso', anchor='center', width=50)  # Nueva columna para nivel de acceso
    # Crea los encabezados de las columnas
    treeview.heading('#0', text='', anchor='center')
    treeview.heading('id', text='N° Factura', anchor='center')
    treeview.heading('fechaPago', text='Fecha', anchor='center')
    treeview.heading('motivoPago', text='Suscripcion', anchor='center')
    treeview.heading('zelle', text='Zelle', anchor='center')
    treeview.heading('usdt', text='USDT', anchor='center')
    treeview.heading('efectivo', text='Efectivo', anchor='center')
    treeview.heading('bolivares', text='Bolivares', anchor='center')
    treeview.heading('acceso', text='Acceso', anchor='center')  # Encabezado para la nueva columna


# Funciones de informes botón 2
def informe_users(main_frame):
    """
    Crea una ventana de informes con un Treeview y un botón para borrar la fila seleccionada.
    :param main_frame: The parent window for the new reports window.
    """
    informe_window = tk.Toplevel(main_frame)
    informe_window.title("Informes")
    informe_window.state('zoomed')  # Maximiza la ventana
    informe_window.configure(bg='#D9D9D9')
    informe_window.attributes('-topmost', True)  # Mantiene la ventana al frente
    informe_window.resizable(False, False)  # Evita que la ventana se pueda redimensionar

    # Cambia el ícono de la ventana
    script_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(script_dir, 'gym.ico')  # Use os.path.join to create the path to the icon
    informe_window.iconbitmap(icon_path)
    font = ('noto sans', 10, 'bold')

    # Configuración del Treeview
    treeview = ttk.Treeview(informe_window)
    treeview.place(relx=0.1, rely=0.05, relwidth=0.76, height=910, anchor='nw')
    # Crea una Scrollbar y la coloca a la derecha del treeview
    scrollbar = ttk.Scrollbar(informe_window, orient="vertical", command=treeview.yview)
    scrollbar.place(relx=0.86, rely=0.05, relheight=0.86, anchor='nw')
    treeview.configure(yscrollcommand=scrollbar.set)  # Configura el treeview para que utilice la Scrollbar
    # Configura las columnas del Treeview
    treeview['columns'] = ('id', 'name', 'ci', 'phone', 'access')
    treeview.column('#0', width=0, stretch='no')
    treeview.column('id', anchor='center', width=10)
    treeview.column('name', anchor='center', width=40)
    treeview.column('ci', anchor='center', width=40)
    treeview.column('phone', anchor='center', width=40)
    treeview.column('access', anchor='center', width=40)  # Nueva columna para nivel de acceso

    # Crea los encabezados de las columnas
    treeview.heading('#0', text='', anchor='center')
    treeview.heading('id', text='N°', anchor='center')
    treeview.heading('name', text='Nombre', anchor='center')
    treeview.heading('ci', text='Cedula', anchor='center')
    treeview.heading('phone', text='Telefono', anchor='center')
    treeview.heading('access', text='Acceso', anchor='center')  # Encabezado para la nueva columna

    buscador = module_classes.BuscadorClientes(treeview)
    buscador.cargar_datos_treeview(treeview)

    # Crea un widget de etiqueta para mostrar el total
    total_label = tk.Label(informe_window, text="Total", font=('noto sans', 9, 'bold'), bg='#F9E79F', width=10, height=1)
    total_label.place(relx=0.5, rely=0.95, anchor='se')

    # Crea un botón que llame a esta función cuando se haga clic en él
    total_entry = tk.Entry(informe_window, width=8, font=('noto sans', 9))
    total_entry.place(relx=0.57, rely=0.95, anchor='se')

    # Botón para borrar la fila seleccionada
    delete_button = tk.Button(informe_window, text="Borrar",
                              command=lambda: buscador.borrar_fila_seleccionada(treeview, total_entry),
                              bg='#F9E79F', width=10, height=1, bd=0, font=font)
    delete_button.place(relx=0.9, rely=0.95, anchor='se')
    buscador.actualizar_total(total_entry)

    # Crea widgets de etiqueta y entrada para buscar por cédula y nombre
    y = 0.04
    name_label = tk.Label(informe_window, text="Nombre", font=('noto sans', 9, 'bold'), bg='#F9E79F', width=8, height=1)
    name_label.place(relx=0.10, rely=y, anchor='sw')
    name_entry = tk.Entry(informe_window, width=10, font=('noto sans', 10))
    name_entry.bind("<KP_Enter>", lambda event: buscador.buscar_por_nombre(treeview, name_entry)) # Llama a la función de búsqueda cuando se presiona Enter en el teclado numérico
    name_entry.bind("<Return>", lambda event: buscador.buscar_por_nombre(treeview, name_entry)) # Llama a la función de búsqueda cuando se presiona Enter
    name_entry.place(relx=0.17, rely=y, anchor='sw')
    # Crea un botón de búsqueda que filtra los resultados por nombre
    search_button(informe_window, command=lambda: buscador.buscar_por_nombre(treeview, name_entry), relx=0.21, rely=0.02)
    # Crea widgets de etiqueta y entrada para buscar por cédula
    ci_label = tk.Label(informe_window, text="Cédula", font=('noto sans', 9, 'bold'), bg='#F9E79F', width=8, height=1)
    ci_label.place(relx=0.70, rely=y, anchor='sw')
    ci_entry = tk.Entry(informe_window, width=10, font=('noto sans', 10))
    ci_entry.bind("<Return>", lambda event: buscador.buscar_por_cedula(treeview, ci_entry)) # Llama a la función de búsqueda cuando se presiona Enter
    ci_entry.bind("<KP_Enter>", lambda event: buscador.buscar_por_cedula(treeview, ci_entry)) # Llama a la función de búsqueda cuando se presiona Enter en el teclado numérico
    ci_entry.bind("<Button-3>", lambda event: ci_entry.delete(0, 'end')) # Elimina el texto si se hace clic con el botón derecho
    ci_entry.bind("<Button-2>", lambda event: ci_entry.delete(0, 'end')) # Elimina el texto si se hace clic con el botón central
    ci_entry.bind("<Button-1>", lambda event: ci_entry.delete(0, 'end')) # Elimina el texto si se hace clic con el botón izquierdo
    ci_entry.place(relx=0.77, rely=y, anchor='sw')

    search_button(informe_window, command=lambda: buscador.buscar_por_cedula(treeview, ci_entry), relx=0.81, rely=0.02)

    def handle_user_update(ci, nombre, item):
        external_signature_add = "IfKuEOfGzQUDZ1oX6uRLkLVYRkxWS4v+8D5sLwiGNMU="
        external_signature_person = "I+scEUWORP/phvzwhFlerMauoVECMIGTuLLiZxc1NOc="

        person_id = module_person.get_person_id_by_code(ci, external_signature_person)
        if not person_id:
            print("Persona no encontrada en Hikvision, agregando...")
            person_result = module_person.add_person(ci, nombre, nombre, external_signature_add)
            if person_result:
                if isinstance(person_result, str):
                    person_id = person_result
                    print(f"Persona agregada con ID {person_id}")
                    messagebox.showinfo("Éxito", f"Persona agregada exitosamente con ID {person_id}", parent=informe_window)
                else:
                    print("Persona agregada, pero no se pudo obtener el ID")
                    messagebox.showinfo("Éxito", "Persona agregada, pero no se pudo obtener el ID", parent=informe_window)
            else:
                messagebox.showerror("Error", "No se pudo agregar la persona en Hikvision", parent=informe_window)
                return
        else:
            print("Persona ya existe en Hikvision con ID:", person_id)
            messagebox.showinfo("Información", f"Persona ya existe en Hikvision con ID: {person_id}", parent=informe_window)

        # Asignar nivel de acceso
        if person_id:
            privilege_group_mapping = {group['privilegeGroupName']: group['privilegeGroupId'] for group in module_access.get_privilege_groups(module_access.external_signature_privilege_list)}
            selected_access_level = "horario normal"  # Fijar el nivel de acceso a "horario normal"
            if selected_access_level in privilege_group_mapping:
                privilege_group_id = privilege_group_mapping[selected_access_level]
                module_access.assign_access_level(person_id, privilege_group_id)
                treeview.set(item, 'access', selected_access_level)  # Actualiza el nivel de acceso en el Treeview

                # Actualizar la base de datos
                try:
                    cursor.execute("UPDATE clientes SET acceso = %s WHERE cedula = %s", (selected_access_level, ci))
                    mydb.commit()
                    print("Base de datos actualizada con éxito")
                except Exception as e:
                    print(f"Error al actualizar la base de datos: {e}")
                
                messagebox.showinfo("Éxito", "Nivel de acceso 'horario normal' asignado correctamente", parent=informe_window)
            else:
                messagebox.showerror("Error", "Nivel de acceso seleccionado no válido", parent=informe_window)

    def on_double_click(event):
        item = treeview.selection()[0]  # Obtiene el item seleccionado
        ci = treeview.item(item, "values")[2]  # Obtiene la cédula del item seleccionado
        nombre = treeview.item(item, "values")[1]  # Obtiene el nombre del item seleccionado
        handle_user_update(ci, nombre, item)

    def on_update_click():
        for item in treeview.selection():
            ci = treeview.item(item, "values")[2]  # Obtiene la cédula del item seleccionado
            nombre = treeview.item(item, "values")[1]  # Obtiene el nombre del item seleccionado
            handle_user_update(ci, nombre, item)

    treeview.bind("<Double-1>", on_double_click)

    update_button = tk.Button(informe_window, text="Actualizar", command=on_update_click,
                              bg='#F9E79F', width=10, height=1, bd=1, font=('noto sans', 8, 'bold'))
    update_button.place(relx=0.48, rely=0.025, anchor='center')

    informe_window.mainloop()
"""
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Esconde la ventana principal ya que no la necesitamos
    informe_users(root)
    root.mainloop()
"""
