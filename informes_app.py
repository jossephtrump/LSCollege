"""
Este archivo contiene la clase InformesApp que se encarga de mostrar los informes
de alumnos y representantes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from databaseManager import mydb
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import landscape, letter

class InformesApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
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
        self.cedula_entry.focus() # Enfocar el campo de cédula al abrir la pestaña
        self.cedula_entry.bind("<Return>", lambda event: self.buscar_por_cedula()) # Buscar al presionar Enter
        self.cedula_entry.bind("<KP_Enter>", lambda event: self.buscar_por_cedula()) # Buscar al presionar Enter en el teclado numérico
        self.cedula_entry.place(relx=0.08, rely=0.02, width=150)
        buscar_cedula_button = tk.Button(self.informes_frame, text="Buscar", font=("noto sans", 8), command=self.buscar_por_cedula, width=5, bg='lightblue')
        buscar_cedula_button.place(relx=0.192, rely=0.018)

        # Selección de curso
        curso_label = tk.Label(self.informes_frame, text="Curso:", font=font)
        curso_label.place(relx=0.02, rely=0.08)
        self.curso_combobox = ttk.Combobox(self.informes_frame, font=font, values=self.obtener_cursos())
        self.curso_combobox.place(relx=0.08, rely=0.08, width=150)
        self.curso_combobox.bind("<<ComboboxSelected>>", self.filtrar_por_curso)

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
        filtrar_button = tk.Button(self.informes_frame, text="Aplicar Filtros", font=("noto sans", 8), command=self.aplicar_filtros, bg='lightblue')
        filtrar_button.place(relx=0.45, rely=0.08)

        # Etiqueta para mostrar la cantidad total de alumnos
        self.total_label = tk.Label(self.informes_frame, text="Total de Alumnos: 0", font=font)
        self.total_label.place(relx=0.7, rely=0.08)

        # Crear el Treeview para mostrar los alumnos
        columns = ('cedula', 'nombre', 'curso', 'genero')
        self.tree = ttk.Treeview(self.informes_frame, columns=columns, show='headings')

        # Definir encabezados
        self.tree.heading('cedula', text='Cédula')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('curso', text='Curso')
        self.tree.heading('genero', text='Género')

        # Definir anchos de columnas
        self.tree.column('cedula', width=100)
        self.tree.column('nombre', width=150)
        self.tree.column('curso', width=80)
        self.tree.column('genero', width=80)

        self.tree.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.informes_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.15, relheight=0.7)

        # Botón para imprimir
        print_button = tk.Button(self.informes_frame, text="Imprimir", font=font, command=self.imprimir_datos)
        print_button.place(relx=0.02, rely=0.9, width=100)

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

        # Buscar en la tabla de representantes
        try:
            cursor = mydb.cursor()
            query = "SELECT cedula, nombre, direccion FROM representante WHERE cedula = %s"
            cursor.execute(query, (cedula,))
            result = cursor.fetchone()
            if result:
                # Mostrar información del representante
                info = f"Cédula: {result[0]}\nNombre: {result[1]}\nDirección: {result[2]}"
                messagebox.showinfo("Información del Representante", info, parent=self.parent_frame)
            else:
                # Buscar en la tabla de alumnos
                query = "SELECT cedula, nombre, curso, genero FROM alumno WHERE cedula = %s"
                cursor.execute(query, (cedula,))
                result = cursor.fetchone()
                if result:
                    # Mostrar información del alumno
                    info = f"Cédula: {result[0]}\nNombre: {result[1]}\nCurso: {result[2]}\nGénero: {result[3]}"
                    messagebox.showinfo("Información del Alumno", info, parent=self.parent_frame)
                else:
                    messagebox.showinfo("No encontrado", "No se encontró ningún representante o alumno con esa cédula.", parent=self.parent_frame)
            cursor.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.parent_frame)

    def filtrar_por_curso(self, event=None):
        self.aplicar_filtros()

    def aplicar_filtros(self, event=None):
        curso = self.curso_combobox.get()
        genero = self.genero_combobox.get()

        try:
            cursor = mydb.cursor()
            query = "SELECT cedula, nombre, curso, genero FROM alumno WHERE 1=1"
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
            for record in self.tree.get_children():
                self.tree.delete(record)

            # Insertar los registros en el Treeview
            for row in result:
                self.tree.insert('', 'end', values=row)

            # Actualizar el total de alumnos
            total_alumnos = len(result)
            self.total_label.config(text=f"Total de Alumnos: {total_alumnos}")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.parent_frame)

    def imprimir_datos(self):
         # Seleccionar ubicación para guardar el archivo
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if not file_path:
            return  # El usuario canceló el diálogo

        # Obtener los datos del Treeview
        data = [['Cédula', 'Nombre', 'Curso', 'Género']]  # Encabezados de la tabla
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
            table = Table(data, colWidths=[1.5 * inch, 4.0 * inch, 1.5 * inch, 1.5 * inch])

            # Añadir estilo a la tabla
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris en la primera fila (encabezados)
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco en los encabezados
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centrar el texto en la tabla
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para los encabezados
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Tamaño de la fuente
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

