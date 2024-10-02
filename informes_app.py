"""
Este archivo contiene la clase InformesApp que se encarga de mostrar los informes
de alumnos y representantes con funcionalidades mejoradas.
Ahora incluye un botón de 'Limpiar'.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import mysql.connector
from databaseManager import mydb
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import landscape, letter
from datetime import date

class InformesApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.sort_column = None
        self.sort_reverse = False
        self.initialize_ui()

    def initialize_ui(self):
        # Usar el Notebook existente en el parent_frame
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        self.informes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.informes_frame, text="Informes")
        self.informes_frame.configure(borderwidth=2, relief=tk.SUNKEN)

        self.create_widgets()
        close_button = tk.Button(self.informes_frame, text=" X ", font=('noto sans', 10, 'bold'),
                                 bg='red2', fg='white', bd=1, command=self.close_tab)
        close_button.place(relx=0.999, rely=0.001, anchor='ne')

    def create_widgets(self):
        font = ('noto sans', 10, 'bold')

        # Búsqueda por cédula
        cedula_label = tk.Label(self.informes_frame, text="Cédula:", font=font)
        cedula_label.place(relx=0.02, rely=0.02)
        self.cedula_entry = ttk.Entry(self.informes_frame, font=font)
        self.cedula_entry.focus()
        self.cedula_entry.bind("<Return>", lambda event: self.buscar_por_cedula())
        self.cedula_entry.bind("<KP_Enter>", lambda event: self.buscar_por_cedula())
        self.cedula_entry.place(relx=0.08, rely=0.02, width=150)
        buscar_cedula_button = tk.Button(self.informes_frame, text="Buscar", font=("noto sans", 8),
                                         command=self.buscar_por_cedula, width=5, bg='lightblue')
        buscar_cedula_button.place(relx=0.192, rely=0.018)

        # Botón para limpiar
        limpiar_button = tk.Button(self.informes_frame, text="Limpiar", font=("noto sans", 8),
                                   command=self.limpiar_filtros, bg='lightblue')
        limpiar_button.place(relx=0.25, rely=0.018)

        # Selección de curso
        curso_label = tk.Label(self.informes_frame, text="Curso:", font=font)
        curso_label.place(relx=0.02, rely=0.08)
        self.curso_combobox = ttk.Combobox(self.informes_frame, font=font, values=self.obtener_cursos())
        self.curso_combobox.place(relx=0.08, rely=0.08, width=150)
        self.curso_combobox.bind("<<ComboboxSelected>>", self.aplicar_filtros)

        # Filtro por género
        genero_label = tk.Label(self.informes_frame, text="Género:", font=font)
        genero_label.place(relx=0.3, rely=0.08)
        self.genero_var = tk.StringVar()
        self.genero_combobox = ttk.Combobox(self.informes_frame, font=font, textvariable=self.genero_var)
        self.genero_combobox['values'] = ('Todos', 'Masculino', 'Femenino')
        self.genero_combobox.current(0)
        self.genero_combobox.place(relx=0.36, rely=0.08, width=120)
        self.genero_combobox.bind("<<ComboboxSelected>>", self.aplicar_filtros)

        # Botón para aplicar filtros
        filtrar_button = tk.Button(self.informes_frame, text="Aplicar Filtros", font=("noto sans", 8),
                                   command=self.aplicar_filtros, bg='lightblue')
        filtrar_button.place(relx=0.5, rely=0.08)

        # Etiqueta para mostrar la cantidad total de alumnos
        self.total_label = tk.Label(self.informes_frame, text="Total de Alumnos: 0", font=font)
        self.total_label.place(relx=0.7, rely=0.08)

        # Crear el Treeview para mostrar los alumnos
        columns = ('cedula', 'nombre', 'curso', 'genero', 'direccion', 'telefono', 'fecha_nacimiento')
        self.tree = ttk.Treeview(self.informes_frame, columns=columns, show='headings')

        # Definir encabezados
        self.tree.heading('cedula', text='Cédula', command=lambda: self.sort_column_data('cedula'))
        self.tree.heading('nombre', text='Nombre', command=lambda: self.sort_column_data('nombre'))
        self.tree.heading('curso', text='Curso', command=lambda: self.sort_column_data('curso'))
        self.tree.heading('genero', text='Género', command=lambda: self.sort_column_data('genero'))
        self.tree.heading('direccion', text='Dirección', command=lambda: self.sort_column_data('direccion'))
        self.tree.heading('telefono', text='Teléfono', command=lambda: self.sort_column_data('telefono'))
        self.tree.heading('fecha_nacimiento', text='Fecha Nacimiento', command=lambda: self.sort_column_data('fecha_nacimiento'))

        # Definir anchos de columnas
        self.tree.column('cedula', width=100)
        self.tree.column('nombre', width=150)
        self.tree.column('curso', width=80)
        self.tree.column('genero', width=80)
        self.tree.column('direccion', width=200)
        self.tree.column('telefono', width=100)
        self.tree.column('fecha_nacimiento', width=100)

        self.tree.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.informes_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.15, relheight=0.7)

        # Botón para imprimir
        print_button = tk.Button(self.informes_frame, text="Imprimir", font=font, command=self.imprimir_datos, bg='indianred1')
        print_button.place(relx=0.02, rely=0.9, width=100)

        # Botón para eliminar registros
        delete_button = tk.Button(self.informes_frame, text="Eliminar", font=font, command=self.eliminar_registro, bg='lightgoldenrod1')
        delete_button.place(relx=0.14, rely=0.9, width=100)

        # Asignar evento de doble clic para editar
        self.tree.bind("<Double-1>", self.editar_registro)

    def obtener_cursos(self):
        try:
            cursor = mydb.cursor()
            query = "SELECT DISTINCT curso FROM alumno ORDER BY curso"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            cursos = [row[0] for row in result]
            return cursos
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar los cursos: {e}", parent=self.parent_frame)
            return []

    def buscar_por_cedula(self):
        cedula = self.cedula_entry.get().strip()
        if not cedula:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula.", parent=self.parent_frame)
            return

        try:
            cursor = mydb.cursor()
            # Buscar en la tabla de representantes
            query = "SELECT cedula, nombre, direccion FROM representante WHERE cedula = %s"
            cursor.execute(query, (cedula,))
            result = cursor.fetchone()
            if result:
                # Mostrar información del representante
                info = f"Cédula: {result[0]}\nNombre: {result[1]}\nDirección: {result[2]}"
                messagebox.showinfo("Información del Representante", info, parent=self.parent_frame)

                # Obtener alumnos asociados al representante
                query_alumnos = """
                SELECT cedula, nombre, curso, genero, direccion, telefono, fecha_nacimiento
                FROM alumno WHERE cedula_representante = %s
                """
                cursor.execute(query_alumnos, (cedula,))
                alumnos = cursor.fetchall()
                if alumnos:
                    # Limpiar el Treeview
                    self.limpiar_treeview()
                    # Insertar los alumnos en el Treeview
                    for alumno in alumnos:
                        self.tree.insert('', 'end', values=alumno)
                    # Actualizar el total de alumnos
                    total_alumnos = len(alumnos)
                    self.total_label.config(text=f"Total de Alumnos: {total_alumnos}")
                else:
                    messagebox.showinfo("Sin Alumnos", "No se encontraron alumnos asociados a este representante.", parent=self.parent_frame)
            else:
                # Buscar en la tabla de alumnos
                query = """
                SELECT cedula, nombre, curso, genero, direccion, telefono, fecha_nacimiento
                FROM alumno WHERE cedula = %s
                """
                cursor.execute(query, (cedula,))
                result = cursor.fetchone()
                if result:
                    # Mostrar información del alumno
                    info = f"Cédula: {result[0]}\nNombre: {result[1]}\nCurso: {result[2]}\nGénero: {result[3]}"
                    messagebox.showinfo("Información del Alumno", info, parent=self.parent_frame)
                    # Mostrar el alumno en el Treeview
                    self.limpiar_treeview()
                    self.tree.insert('', 'end', values=result)
                    # Actualizar el total de alumnos
                    self.total_label.config(text="Total de Alumnos: 1")
                else:
                    messagebox.showinfo("No encontrado", "No se encontró ningún representante o alumno con esa cédula.", parent=self.parent_frame)
            cursor.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.parent_frame)

    def aplicar_filtros(self, event=None):
        curso = self.curso_combobox.get()
        genero = self.genero_combobox.get()

        try:
            cursor = mydb.cursor()
            query = """
            SELECT cedula, nombre, curso, genero, direccion, telefono, fecha_nacimiento
            FROM alumno WHERE 1=1
            """
            params = []

            if curso:
                query += " AND curso = %s"
                params.append(curso)

            if genero and genero != 'Todos':
                query += " AND genero = %s"
                params.append(genero)

            query += " ORDER BY nombre"

            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()

            # Limpiar el Treeview
            self.limpiar_treeview()

            # Guardar los datos en una variable para el ordenamiento
            self.alumno_data = result

            # Insertar los registros en el Treeview
            for row in result:
                self.tree.insert('', 'end', values=row)

            # Actualizar el total de alumnos
            total_alumnos = len(result)
            self.total_label.config(text=f"Total de Alumnos: {total_alumnos}")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.parent_frame)

    def limpiar_treeview(self):
        # Limpiar el Treeview
        for record in self.tree.get_children():
            self.tree.delete(record)

    def limpiar_filtros(self):
        # Limpiar los campos de entrada y filtros
        self.cedula_entry.delete(0, tk.END)
        self.curso_combobox.set('')
        self.genero_combobox.set('Todos')
        self.limpiar_treeview()
        self.total_label.config(text="Total de Alumnos: 0")

    def sort_column_data(self, col):
        # Ordenar los datos de acuerdo a la columna seleccionada
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_column = col

        # Obtener los datos actuales del Treeview
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        # Intentar convertir a número para ordenar correctamente
        try:
            data.sort(key=lambda t: float(t[0]), reverse=self.sort_reverse)
        except ValueError:
            data.sort(reverse=self.sort_reverse)

        # Reordenar los ítems en el Treeview
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

    def editar_registro(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
        column = self.tree.identify_column(event.x)
        column_index = int(column.replace('#', '')) - 1
        column_name = self.tree['columns'][column_index]

        x, y, width, height = self.tree.bbox(item_id, column)
        value = self.tree.set(item_id, column_name)

        # Crear una ventana emergente para editar el valor
        self.edit_popup = tk.Toplevel(self.parent_frame)
        self.edit_popup.title("Editar Valor")
        self.edit_popup.geometry(f"250x100+{event.x_root}+{event.y_root}")
        tk.Label(self.edit_popup, text=f"Editar {column_name}:", font=('noto sans', 10)).pack(pady=5)
        self.edit_entry = ttk.Entry(self.edit_popup, font=('noto sans', 10))
        self.edit_entry.insert(0, value)
        self.edit_entry.pack(pady=5)
        tk.Button(self.edit_popup, text="Guardar", command=lambda: self.guardar_cambios(item_id, column_name)).pack(pady=5)

    def guardar_cambios(self, item_id, column_name):
        nuevo_valor = self.edit_entry.get().strip()
        cedula_alumno = self.tree.set(item_id, 'cedula')

        try:
            cursor = mydb.cursor()
            query = f"UPDATE alumno SET {column_name} = %s WHERE cedula = %s"
            cursor.execute(query, (nuevo_valor, cedula_alumno))
            mydb.commit()
            cursor.close()

            # Actualizar el valor en el Treeview
            self.tree.set(item_id, column_name, nuevo_valor)
            self.edit_popup.destroy()
            messagebox.showinfo("Éxito", "Información actualizada correctamente.", parent=self.parent_frame)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al actualizar la base de datos: {e}", parent=self.parent_frame)

    def eliminar_registro(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "No hay registros seleccionados.", parent=self.parent_frame)
            return

        confirm = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar los registros seleccionados?", parent=self.parent_frame)
        if confirm:
            try:
                cursor = mydb.cursor()
                for item_id in selected_items:
                    cedula_alumno = self.tree.set(item_id, 'cedula')
                    query = "DELETE FROM alumno WHERE cedula = %s"
                    cursor.execute(query, (cedula_alumno,))
                    # También podrías eliminar registros relacionados en otras tablas si es necesario

                mydb.commit()
                cursor.close()

                # Eliminar los registros del Treeview
                for item_id in selected_items:
                    self.tree.delete(item_id)

                messagebox.showinfo("Éxito", "Registros eliminados correctamente.", parent=self.parent_frame)
                # Actualizar el total de alumnos
                total_alumnos = len(self.tree.get_children())
                self.total_label.config(text=f"Total de Alumnos: {total_alumnos}")
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error al eliminar de la base de datos: {e}", parent=self.parent_frame)

    def imprimir_datos(self):
        # Seleccionar ubicación para guardar el archivo
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if not file_path:
            return  # El usuario canceló el diálogo

        # Obtener los datos del Treeview
        data = [['Cédula', 'Nombre', 'Curso', 'Género', 'Dirección', 'Teléfono', 'Fecha Nacimiento']]  # Encabezados de la tabla
        for row in self.tree.get_children():
            data.append(self.tree.item(row)["values"])

        # Generar el archivo PDF usando DocTemplate
        try:
            pdf = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []

            # Añadir título al PDF
            styles = getSampleStyleSheet()
            title = Paragraph("Informe de Alumnos", styles['Title'])
            elements.append(title)
            elements.append(Paragraph("<br/><br/>", styles['BodyText']))  # Espacio en blanco

            # Crear la tabla con los datos
            table = Table(data, colWidths=[1.0 * inch, 2.5 * inch, 1.0 * inch, 1.0 * inch, 2.5 * inch, 1.5 * inch, 1.5 * inch])

            # Añadir estilo a la tabla
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris en la primera fila (encabezados)
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco en los encabezados
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centrar el texto en la tabla
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para los encabezados
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # Tamaño de la fuente
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espacio bajo los encabezados
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo beige para el resto de la tabla
                ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Añadir líneas de la cuadrícula
            ])
            table.setStyle(style)

            # Añadir tabla a los elementos
            elements.append(table)

            # Construir el documento PDF
            pdf.build(elements)

            messagebox.showinfo("Éxito", f"Datos guardados en {file_path}", parent=self.parent_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo PDF: {e}", parent=self.parent_frame)

    def close_tab(self):
        self.notebook.forget(self.informes_frame)
        self.notebook.place_forget()  # Oculta el notebook
