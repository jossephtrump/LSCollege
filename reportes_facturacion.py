"""
Este archivo contiene la clase ReportesFacturacionApp que se encarga de mostrar los reportes de facturación,
permitiendo generar un PDF con los resultados filtrados, incluyendo el total de los montos, y anular facturas en caso de error.
Ahora incluye un filtro para mostrar facturas anuladas.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import mysql.connector
from datetime import date
from databaseManager import mydb
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

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

        # Etiqueta y campo de selección de fecha inicial
        date_label = tk.Label(self.reportes_frame, text="Fecha Inicio:", font=font)
        date_label.place(relx=0.02, rely=0.02)

        self.start_date_entry = DateEntry(self.reportes_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, font=font, date_pattern='yyyy-mm-dd')
        self.start_date_entry.place(relx=0.12, rely=0.02)

        # Etiqueta y campo de selección de fecha final
        end_date_label = tk.Label(self.reportes_frame, text="Fecha Fin:", font=font)
        end_date_label.place(relx=0.25, rely=0.02)

        self.end_date_entry = DateEntry(self.reportes_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, font=font, date_pattern='yyyy-mm-dd')
        self.end_date_entry.place(relx=0.35, rely=0.02)

        # Filtro de estado de factura (Activa, Anulada, Todas)
        status_label = tk.Label(self.reportes_frame, text="Estado:", font=font)
        status_label.place(relx=0.48, rely=0.02)

        self.status_var = tk.StringVar()
        self.status_var.set("Activas")  # Valor predeterminado

        status_options = ["Activas", "Anuladas", "Todas"]
        self.status_menu = ttk.OptionMenu(self.reportes_frame, self.status_var, "Activas", *status_options)
        self.status_menu.place(relx=0.55, rely=0.02)

        # Botón para filtrar
        filter_button = tk.Button(self.reportes_frame, text="Filtrar", font=font, command=self.filter_records, bg='DodgerBlue2', fg='white')
        filter_button.place(relx=0.68, rely=0.02)

        # Botón para generar PDF
        pdf_button = tk.Button(self.reportes_frame, text="Generar PDF", font=font, command=self.generate_pdf, bg='IndianRed3', fg='white')
        pdf_button.place(relx=0.76, rely=0.02)

        # Botón para limpiar
        clear_button = tk.Button(self.reportes_frame, text="Limpiar", font=font, command=self.clear_records, bg='orange2')
        clear_button.place(relx=0.86, rely=0.02)

        # Botón para anular factura
        anular_button = tk.Button(self.reportes_frame, text="Anular", font=font, command=self.anular_factura, bg='pink4', fg='white')
        anular_button.place(relx=0.93, rely=0.02)

        # Crear el Treeview para mostrar las facturas
        columns = ('id_factura', 'cedula_representante', 'nombre_alumno', 'mes', 'tipo_pago', 'monto', 'fecha', 'estado')
        self.tree = ttk.Treeview(self.reportes_frame, columns=columns, show='headings')

        # Definir encabezados
        self.tree.heading('id_factura', text='ID Factura')
        self.tree.heading('cedula_representante', text='Cédula Representante')
        self.tree.heading('nombre_alumno', text='Nombre Alumno')
        self.tree.heading('mes', text='Mes')
        self.tree.heading('tipo_pago', text='Tipo de Pago')
        self.tree.heading('monto', text='Monto')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('estado', text='Estado')

        # Definir anchos de columnas
        self.tree.column('id_factura', width=80)
        self.tree.column('cedula_representante', width=120)
        self.tree.column('nombre_alumno', width=120)
        self.tree.column('mes', width=80)
        self.tree.column('tipo_pago', width=100)
        self.tree.column('monto', width=80)
        self.tree.column('fecha', width=100)
        self.tree.column('estado', width=80)

        self.tree.place(relx=0.02, rely=0.08, relwidth=0.96, relheight=0.85)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.reportes_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.08, relheight=0.85)

        # Cargar los registros del día actual
        self.load_records(date.today(), date.today())

    def load_records(self, start_date, end_date):
        # Limpiar el Treeview
        for record in self.tree.get_children():
            self.tree.delete(record)

        # Obtener el estado seleccionado
        estado = self.status_var.get()

        # Construir la cláusula WHERE para el estado
        estado_clause = ""
        if estado == "Activas":
            estado_clause = "AND anulado = 0"
        elif estado == "Anuladas":
            estado_clause = "AND anulado = 1"
        elif estado == "Todas":
            estado_clause = ""  # No se agrega ninguna condición

        # Consultar los registros de facturación del rango de fechas seleccionado
        try:
            cursor = mydb.cursor()
            query = f"""
            SELECT id_factura, cedula_representante, nombre_alumno, mes, tipo_pago, monto, fecha, anulado
            FROM registro_pagos
            WHERE DATE(fecha) BETWEEN %s AND %s
            {estado_clause}
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchall()
            cursor.close()

            # Insertar los registros en el Treeview
            for row in result:
                id_factura, cedula_representante, nombre_alumno, mes, tipo_pago, monto, fecha, anulado = row
                estado_factura = "Anulada" if anulado else "Activa"
                self.tree.insert('', 'end', values=(id_factura, cedula_representante, nombre_alumno, mes, tipo_pago, monto, fecha, estado_factura))
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.parent_frame)

    def filter_records(self):
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        self.load_records(start_date, end_date)

    def generate_pdf(self):
        # Obtener las fechas seleccionadas para incluirlas en el PDF
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Obtener los datos del Treeview
        records = []
        for child in self.tree.get_children():
            record = self.tree.item(child)['values']
            # Formatear el monto y la fecha
            record[5] = f"${float(record[5]):,.2f}"  # Monto
            record[6] = str(record[6])  # Fecha
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
                initialfile=f"Reporte_Facturacion_{start_date_str}_to_{end_date_str}.pdf",
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
            title = Paragraph(f"Reporte de Facturación - {start_date_str} a {end_date_str}", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Encabezados de la tabla
            encabezados = ['ID Factura', 'Cédula Representante', 'Nombre Alumno', 'Mes', 'Tipo de Pago', 'Monto', 'Fecha', 'Estado']

            # Datos de la tabla
            data = [encabezados] + records

            # Crear la tabla
            table = Table(data, colWidths=[60, 80, 100, 60, 80, 60, 80, 60])

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

            # Calcular el total de los montos (solo facturas activas)
            total_monto = sum(
                float(record[5].replace('$', '').replace(',', ''))
                for record in records if record[7] == "Activa"
            )

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
            total_paragraph = Paragraph(f"Total Monto (Facturas Activas): ${total_monto:,.2f}", total_style)
            elements.append(total_paragraph)

            # Construir el PDF
            document.build(elements)

            messagebox.showinfo("PDF Generado", f"El reporte ha sido generado como '{filename}'.", parent=self.parent_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}", parent=self.parent_frame)

    def clear_records(self):
        # Restablecer los campos de fecha al día actual
        today = date.today()
        self.start_date_entry.set_date(today)
        self.end_date_entry.set_date(today)
        # Restablecer el filtro de estado
        self.status_var.set("Activas")
        # Limpiar el Treeview
        for record in self.tree.get_children():
            self.tree.delete(record)

    def anular_factura(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una factura para anular.", parent=self.parent_frame)
            return

        # Obtener los datos de la factura seleccionada
        factura = self.tree.item(selected_item)['values']
        id_factura = factura[0]
        estado_actual = factura[7]

        if estado_actual == "Anulada":
            messagebox.showinfo("Información", f"La factura ID {id_factura} ya está anulada.", parent=self.parent_frame)
            return

        # Confirmar anulación
        respuesta = messagebox.askyesno("Confirmar anulación", f"¿Está seguro de que desea anular la factura ID {id_factura}?", parent=self.parent_frame)
        if respuesta:
            try:
                cursor = mydb.cursor()
                # Actualizar el estado de la factura a 'anulado'
                query = "UPDATE registro_pagos SET anulado = 1 WHERE id_factura = %s"
                cursor.execute(query, (id_factura,))
                mydb.commit()
                cursor.close()

                messagebox.showinfo("Factura anulada", f"La factura ID {id_factura} ha sido anulada.", parent=self.parent_frame)

                # Actualizar la vista
                self.filter_records()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo anular la factura: {e}", parent=self.parent_frame)

    def close_tab(self):
        self.notebook.forget(self.reportes_frame)
        self.notebook.destroy()
