"""
Este archivo contiene la clase ReportesFacturacionApp que se encarga de mostrar los reportes de facturación
y generar un PDF con los resultados filtrados, incluyendo el total de los montos.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import mysql.connector
from datetime import datetime, date
from databaseManager import mydb

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

class ReportesFacturacionApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.initialize_ui()

    def initialize_ui(self):
        # Usar el Notebook existente en el parent_frame
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        self.reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reportes_frame, text="Reportes de Facturación")
        self.reportes_frame.configure(borderwidth=2, relief=tk.SUNKEN)

        self.create_widgets()
        close_button = tk.Button(self.reportes_frame, text=" X ", font=('noto sans', 10, 'bold'),
                                 bg='red2', fg='white', bd=1, command=self.close_tab)
        close_button.place(relx=0.999, rely=0.001, anchor='ne')

    def create_widgets(self):
        font = ('noto sans', 10, 'bold')

        # Etiqueta y campo de selección de fecha
        date_label = tk.Label(self.reportes_frame, text="Seleccionar Fecha:", font=font)
        date_label.place(relx=0.02, rely=0.02)

        self.date_entry = DateEntry(self.reportes_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, font=font, date_pattern='yyyy-mm-dd')
        self.date_entry.place(relx=0.15, rely=0.02)

        # Botón para filtrar
        filter_button = tk.Button(self.reportes_frame, text="Filtrar", font=font, command=self.filter_records)
        filter_button.place(relx=0.3, rely=0.02)

        # Botón para generar PDF
        pdf_button = tk.Button(self.reportes_frame, text="Generar PDF", font=font, command=self.generate_pdf)
        pdf_button.place(relx=0.4, rely=0.02)

        # Crear el Treeview para mostrar las facturas
        columns = ('cedula_representante', 'nombre_alumno', 'mes', 'tipo_pago', 'monto', 'fecha')
        self.tree = ttk.Treeview(self.reportes_frame, columns=columns, show='headings')

        # Definir encabezados
        self.tree.heading('cedula_representante', text='Cédula Representante')
        self.tree.heading('nombre_alumno', text='Nombre Alumno')
        self.tree.heading('mes', text='Mes')
        self.tree.heading('tipo_pago', text='Tipo de Pago')
        self.tree.heading('monto', text='Monto')
        self.tree.heading('fecha', text='Fecha')

        # Definir anchos de columnas
        self.tree.column('cedula_representante', width=120)
        self.tree.column('nombre_alumno', width=120)
        self.tree.column('mes', width=80)
        self.tree.column('tipo_pago', width=100)
        self.tree.column('monto', width=80)
        self.tree.column('fecha', width=100)

        self.tree.place(relx=0.02, rely=0.08, relwidth=0.96, relheight=0.85)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.reportes_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.08, relheight=0.85)

        # Cargar los registros del día actual
        self.load_records(date.today())

    def load_records(self, selected_date):
        # Limpiar el Treeview
        for record in self.tree.get_children():
            self.tree.delete(record)

        # Consultar los registros de facturación de la fecha seleccionada
        try:
            cursor = mydb.cursor()
            query = """
            SELECT cedula_representante, nombre_alumno, mes, tipo_pago, monto, fecha
            FROM registro_pagos
            WHERE DATE(fecha) = %s
            """
            cursor.execute(query, (selected_date,))
            result = cursor.fetchall()
            cursor.close()

            # Insertar los registros en el Treeview
            for row in result:
                self.tree.insert('', 'end', values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.parent_frame)

    def filter_records(self):
        selected_date = self.date_entry.get_date()
        self.load_records(selected_date)

    def generate_pdf(self):
        # Obtener la fecha seleccionada para incluirla en el PDF
        selected_date = self.date_entry.get_date()
        fecha_str = selected_date.strftime('%Y-%m-%d')

        # Obtener los datos del Treeview
        records = []
        for child in self.tree.get_children():
            record = self.tree.item(child)['values']
            # Formatear el monto y la fecha
            record[4] = f"${float(record[4]):,.2f}"
            record[5] = str(record[5])
            records.append(record)

        if not records:
            messagebox.showwarning("Sin datos", "No hay registros para generar el PDF.", parent=self.parent_frame)
            return

        # Crear el documento PDF
        try:
            # Usar filedialog para permitir al usuario elegir la ubicación y el nombre del archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Reporte_Facturacion_{fecha_str}.pdf",
                title="Guardar reporte como"
            )
            if not filename:
                return  # El usuario canceló la operación

            document = SimpleDocTemplate(filename, pagesize=letter)

            elements = []
            styles = getSampleStyleSheet()

            # Título del documento
            title_style = ParagraphStyle(
                name='TitleStyle',
                parent=styles['Title'],
                alignment=TA_CENTER
            )
            title = Paragraph(f"Reporte de Facturación - {fecha_str}", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Encabezados de la tabla
            encabezados = ['Cédula Representante', 'Nombre Alumno', 'Mes', 'Tipo de Pago', 'Monto', 'Fecha']

            # Datos de la tabla
            data = [encabezados] + records

            # Crear la tabla
            table = Table(data, colWidths=[80, 100, 60, 80, 60, 80])

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Fondo de los encabezados
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color de texto de los encabezados
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente de los encabezados
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaciado inferior de los encabezados
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
            ])

            table.setStyle(estilo_tabla)
            elements.append(table)

            # Calcular el total de los montos
            total_monto = sum(float(record[4].replace('$', '').replace(',', '')) for record in records)

            # Añadir un espacio antes del total
            elements.append(Spacer(1, 12))

            # Añadir el total al final del documento
            total_style = ParagraphStyle(
                name='TotalStyle',
                parent=styles['Normal'],
                alignment=TA_RIGHT,
                fontSize=12,
                leading=14,
            )
            total_paragraph = Paragraph(f"Total Monto: ${total_monto:,.2f}", total_style)
            elements.append(total_paragraph)

            # Construir el PDF
            document.build(elements)

            messagebox.showinfo("PDF Generado", f"El reporte ha sido generado como '{filename}'.", parent=self.parent_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}", parent=self.parent_frame)

    def close_tab(self):
        self.notebook.forget(self.reportes_frame)
        self.notebook.destroy()
