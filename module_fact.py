"""
Módulo de facturación: este módulo se encarga de la facturación de los alumnos, basado en la cédula del representante.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import logging
import os

# Configurar logging
logging.basicConfig(
    filename='facturacion_app.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Conexión a la base de datos
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="colegio"  # Cambia esto al nombre de tu base de datos
    )
except mysql.connector.Error as e:
    messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
    exit()


class FacturacionApp:
    def __init__(self, root):
        self.root = root
        self.school_info = """U.E LS COLLEGE
URB. ZONA NORTE
MUNICIPIO MARACAIBO
EDO ZULIA RIF J-402317450"""
        self.alumnos_comboboxes = []   # Lista para almacenar los combobox de alumnos
        self.meses_comboboxes = []     # Lista para almacenar los combobox de meses
        self.tipos_comboboxes = []     # Lista para almacenar los combobox de tipo de pago
        self.monto_entries = []        # Lista para almacenar las entradas de montos
        self.delete_buttons = []       # Lista para almacenar los botones de eliminar
        self.registros = []            # Lista para almacenar los registros de facturación
        self.alumnos_cursos = {}       # Diccionario para almacenar los alumnos y sus cursos y cédulas
        self.initialize_ui()

    def initialize_ui(self):
        self.style = ttk.Style()
        self.style.configure('TButton', font=('noto sans', 10))
        self.style.configure('TLabel', font=('noto sans', 10))
        self.style.configure('TEntry', font=('noto sans', 10))
        self.style.configure('TCombobox', font=('noto sans', 10))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        self.fact_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fact_frame, text="Facturación")
        self.fact_frame.configure(borderwidth=2, relief=tk.SUNKEN)

        self.create_widgets()
        close_button = ttk.Button(self.fact_frame, text=" X ", style='TButton',
                                  command=self.close_tab)
        close_button.place(relx=0.999, rely=0.001, anchor='ne')

    def create_widgets(self):
        altura = 26
        ancho = 200
        pos_label_y = 0.10
        pos_entry_y = 0.14
        font = ('noto sans', 10)

        # Campo Cédula Representante
        self.ci_label = ttk.Label(self.fact_frame, text="Cédula Representante:", font=font)
        self.ci_label.place(relx=0.02, rely=0.02)
        self.ci_entry = ttk.Entry(self.fact_frame, font=font)
        self.ci_entry.place(relx=0.15, rely=0.02, width=ancho, height=altura)
        self.ci_entry.bind("<Return>", lambda event: self.fill_entries())
        self.ci_entry.bind("<KP_Enter>", lambda event: self.fill_entries())

        # Botón Buscar
        search_button = ttk.Button(self.fact_frame, text="Buscar", style='TButton', command=self.fill_entries)
        search_button.place(relx=0.35, rely=0.018)

        # Campo Alumno
        self.alumno_label = ttk.Label(self.fact_frame, text="Alumno", font=font)
        self.alumno_label.place(relx=0.02, rely=pos_label_y)
        self.alumno_combobox = ttk.Combobox(self.fact_frame, values=[], font=font, state='readonly')
        self.alumno_combobox.place(relx=0.02, rely=pos_entry_y, width=ancho, height=altura)
        self.alumnos_comboboxes.append(self.alumno_combobox)

        # Campo Mes
        self.meses_label = ttk.Label(self.fact_frame, text="Mes", font=font)
        self.meses_label.place(relx=0.24, rely=pos_label_y)
        self.meses_combobox = ttk.Combobox(self.fact_frame, values=[
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ], font=font, state='readonly')
        self.meses_combobox.place(relx=0.24, rely=pos_entry_y, width=ancho, height=altura)
        self.meses_comboboxes.append(self.meses_combobox)

        # Campo Tipo de Pago
        self.tipo_label = ttk.Label(self.fact_frame, text="Tipo de Pago", font=font)
        self.tipo_label.place(relx=0.46, rely=pos_label_y)
        self.tipo_combobox = ttk.Combobox(self.fact_frame, values=["Mensualidad", "Inscripción"], font=font, state='readonly')
        self.tipo_combobox.place(relx=0.46, rely=pos_entry_y, width=ancho, height=altura)
        self.tipos_comboboxes.append(self.tipo_combobox)
        self.tipo_combobox.set("Mensualidad")

        # Campo Monto
        self.monto_label = ttk.Label(self.fact_frame, text="Monto a Pagar", font=font)
        self.monto_label.place(relx=0.68, rely=pos_label_y)
        self.monto_entry = ttk.Entry(self.fact_frame, font=font)
        self.monto_entry.place(relx=0.68, rely=pos_entry_y, width=ancho, height=altura)
        self.monto_entries.append(self.monto_entry)

        # Botón para agregar otro alumno
        add_button = ttk.Button(self.fact_frame, text="Agregar Alumno", style='TButton', command=self.add_another_alumno)
        add_button.place(relx=0.9, rely=0.14)

        # Botón para facturar
        self.facturar_button = ttk.Button(self.fact_frame, text="Facturar", style='TButton', command=self.on_facturar_button_click)
        self.facturar_button.place(relx=0.9, rely=0.90)

    def fill_entries(self):
        cedula_fact = self.ci_entry.get().strip()
        if not self.es_cedula_valida(cedula_fact):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula válida.", parent=self.root)
            return

        alumnos = self.get_alumnos_by_representante(cedula_fact)
        if alumnos:
            for combobox in self.alumnos_comboboxes:
                combobox['values'] = alumnos
                if not combobox.get():
                    combobox.current(0)
        else:
            messagebox.showwarning("No encontrado", "No se encontraron alumnos para este representante.", parent=self.root)

    def es_cedula_valida(self, cedula):
        """Valida que la cédula sea numérica."""
        return cedula.isdigit()

    def get_alumnos_by_representante(self, cedula_representante):
        try:
            cursor = mydb.cursor()
            query = """
            SELECT nombre, curso, cedula
            FROM alumno
            WHERE cedula_representante = %s
            """
            cursor.execute(query, (cedula_representante,))
            result = cursor.fetchall()
            cursor.close()
            # Guardar cursos y cédulas de alumnos en un diccionario
            self.alumnos_cursos = {row[0]: {'curso': row[1], 'cedula': row[2]} for row in result}
            return list(self.alumnos_cursos.keys())
        except mysql.connector.Error as e:
            logging.error(f"Error al obtener alumnos por representante: {e}")
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.root)
            return []

    def add_another_alumno(self):
        # Crear otro set de widgets para alumno, mes, tipo y monto
        font = ('noto sans', 10)
        ancho = 200

        # Calcular la posición vertical de los nuevos widgets
        idx = len(self.alumnos_comboboxes)
        rely_label = 0.10 + idx * 0.08
        rely_entry = 0.14 + idx * 0.08

        alumno_combobox = ttk.Combobox(self.fact_frame, values=self.alumno_combobox['values'], font=font, state='readonly')
        alumno_combobox.place(relx=0.02, rely=rely_entry, width=ancho, height=26)
        self.alumnos_comboboxes.append(alumno_combobox)

        meses_combobox = ttk.Combobox(self.fact_frame, values=self.meses_combobox['values'], font=font, state='readonly')
        meses_combobox.place(relx=0.24, rely=rely_entry, width=ancho, height=26)
        self.meses_comboboxes.append(meses_combobox)

        tipo_combobox = ttk.Combobox(self.fact_frame, values=self.tipo_combobox['values'], font=font, state='readonly')
        tipo_combobox.place(relx=0.46, rely=rely_entry, width=ancho, height=26)
        self.tipos_comboboxes.append(tipo_combobox)
        tipo_combobox.set("Mensualidad")

        monto_entry = ttk.Entry(self.fact_frame, font=font)
        monto_entry.place(relx=0.68, rely=rely_entry, width=ancho, height=26)
        self.monto_entries.append(monto_entry)

        # Crear el botón "Eliminar" para esta fila
        delete_button = ttk.Button(self.fact_frame, text="Eliminar", style='TButton',
                                   command=lambda: self.kill_widgets(idx))
        delete_button.place(relx=0.9, rely=rely_entry)
        self.delete_buttons.append(delete_button)

    def kill_widgets(self, idx):
        # Eliminar los widgets de la interfaz y las listas
        self.alumnos_comboboxes[idx].destroy()
        self.meses_comboboxes[idx].destroy()
        self.tipos_comboboxes[idx].destroy()
        self.monto_entries[idx].destroy()
        self.delete_buttons[idx].destroy()

        # Actualizar las listas
        self.alumnos_comboboxes.pop(idx)
        self.meses_comboboxes.pop(idx)
        self.tipos_comboboxes.pop(idx)
        self.monto_entries.pop(idx)
        self.delete_buttons.pop(idx)

        # Reordenar los widgets restantes
        self.reorder_widgets()

    def reorder_widgets(self):
        # Reposicionar los widgets después de eliminar uno
        font = ('noto sans', 10)
        ancho = 200
        for idx in range(len(self.alumnos_comboboxes)):
            rely_label = 0.10 + idx * 0.08
            rely_entry = 0.14 + idx * 0.08
            self.alumnos_comboboxes[idx].place_configure(relx=0.02, rely=rely_entry)
            self.meses_comboboxes[idx].place_configure(relx=0.24, rely=rely_entry)
            self.tipos_comboboxes[idx].place_configure(relx=0.46, rely=rely_entry)
            self.monto_entries[idx].place_configure(relx=0.68, rely=rely_entry)
            self.delete_buttons[idx].place_configure(relx=0.9, rely=rely_entry)

    def verificar_pago_inscripcion(self, cedula_estudiante, tipo_pago):
        """
        Verifica si ya existe un pago de inscripción registrado para el alumno en el año escolar actual.
        """
        if tipo_pago.lower() == "inscripción":
            try:
                cursor = mydb.cursor()
                query = """
                SELECT COUNT(*) FROM registro_pagos 
                WHERE cedula_estudiante = %s AND tipo_pago = %s AND YEAR(fecha_pago) = YEAR(CURDATE())
                """
                cursor.execute(query, (cedula_estudiante, tipo_pago))
                result = cursor.fetchone()
                cursor.close()
                if result[0] > 0:
                    return True  # Existe un pago de inscripción registrado
            except mysql.connector.Error as e:
                logging.error(f"Error al verificar el pago de inscripción: {e}")
                messagebox.showerror("Error", f"Error al verificar el pago de inscripción: {e}", parent=self.root)
        return False

    def on_facturar_button_click(self):
        cedula_representante = self.ci_entry.get().strip()
        if not self.es_cedula_valida(cedula_representante):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula válida del representante.", parent=self.root)
            return

        fecha_actual = datetime.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now().strftime('%H:%M:%S')
        self.registros = []

        for i in range(len(self.alumnos_comboboxes)):
            alumno = self.alumnos_comboboxes[i].get()
            mes = self.meses_comboboxes[i].get()
            tipo_pago = self.tipos_comboboxes[i].get()
            monto = self.monto_entries[i].get()

            # Validaciones
            if not alumno or not mes or not tipo_pago or not monto:
                messagebox.showwarning("Campos Incompletos", f"Por favor, complete todos los campos en la fila {i+1}.", parent=self.root)
                return

            try:
                monto_float = float(monto)
                if monto_float <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Monto Inválido", f"El monto debe ser un número positivo en la fila {i+1}.", parent=self.root)
                return

            # Obtener la cédula y curso del alumno desde el diccionario
            alumno_info = self.alumnos_cursos.get(alumno)
            if alumno_info:
                cedula_estudiante = alumno_info.get('cedula')
                curso = alumno_info.get('curso')
            else:
                messagebox.showwarning("No encontrado", f"No se encontró la información del alumno '{alumno}'.", parent=self.root)
                return

            # Verificar si ya existe un pago de inscripción para este alumno
            if self.verificar_pago_inscripcion(cedula_estudiante, tipo_pago):
                messagebox.showwarning(
                    "Pago de Inscripción Existente",
                    f"El alumno '{alumno}' ya tiene registrado un pago de inscripción para este año escolar.",
                    parent=self.root
                )
                return  # Detener el proceso si ya existe un pago de inscripción

            # Registrar la información
            self.registros.append((fecha_actual, hora_actual, cedula_estudiante, alumno, cedula_representante, monto_float, tipo_pago, mes, curso))

        # Confirmación antes de registrar
        if messagebox.askyesno("Confirmar", "¿Desea registrar estos pagos?", parent=self.root):
            try:
                cursor = mydb.cursor()
                query = """
                INSERT INTO registro_pagos (fecha_pago, hora, cedula_estudiante, nombre_alumno, cedula_representante, monto, tipo_pago, mes, curso)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(query, self.registros)
                mydb.commit()
                cursor.close()
                messagebox.showinfo("Éxito", "Factura registrada correctamente.", parent=self.root)
                self.print_windows()
            except mysql.connector.Error as e:
                logging.error(f"Error al registrar los pagos: {e}")
                messagebox.showerror("Error", f"No se pudo registrar los pagos: {e}", parent=self.root)
        else:
            messagebox.showinfo("Cancelado", "La operación ha sido cancelada.", parent=self.root)

    def print_windows(self):
        # Ventana emergente de impresión
        self.print_window = tk.Toplevel(self.root)
        self.print_window.title("Imprimir Factura")
        self.print_window.configure(bg='#D9D9D9')
        self.print_window.overrideredirect(True)
        self.print_window.attributes('-topmost', True)

        window_width = 400
        window_height = 200
        self.print_window.geometry(f'{window_width}x{window_height}')

        screen_width = self.print_window.winfo_screenwidth()
        screen_height = self.print_window.winfo_screenheight()
        position_top = screen_height // 2 - window_height // 2
        position_right = screen_width // 2 - window_width // 2

        self.print_window.geometry("+{}+{}".format(position_right, position_top))

        print_button = ttk.Button(self.print_window, text="Imprimir", command=self.on_imprimir_button_click)
        print_button.place(relx=0.3, rely=0.5)

        exit_button = ttk.Button(self.print_window, text="Salir", command=lambda: [self.clear_entries(), self.print_window.destroy()])
        exit_button.place(relx=0.6, rely=0.5)

    def on_imprimir_button_click(self):
        # Cerrar la ventana de impresión primero
        self.print_window.destroy()
        self.root.update()  # Actualiza la interfaz para reflejar el cierre de la ventana

        # Generar el PDF y mostrar mensajes después
        self.generate_pdf()
        self.clear_entries()
        self.show_success_message()

    def get_representante_info(self, cedula_representante):
        try:
            cursor = mydb.cursor()
            query = """
            SELECT nombre, direccion
            FROM representante
            WHERE cedula = %s
            """
            cursor.execute(query, (cedula_representante,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                nombre = result[0]
                direccion = result[1] if result[1] else "No proporcionada"
                return nombre, direccion
            else:
                return "No encontrado", "No encontrado"
        except mysql.connector.Error as e:
            logging.error(f"Error al obtener información del representante: {e}")
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}", parent=self.root)
            return "Error", "Error"

    def generate_pdf(self):
        # Generar un PDF con la información de facturación
        try:
            # Abrir un cuadro de diálogo para elegir la ubicación y nombre del archivo PDF
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
                title="Guardar PDF",
                initialfile="recibo_factura.pdf",
                parent=self.root
            )
            if not filename:
                # El usuario canceló el diálogo
                return

            document = SimpleDocTemplate(filename, pagesize=letter)

            elements = []
            styles = getSampleStyleSheet()

            # Obtener la información del representante
            cedula_representante = self.registros[0][4]
            nombre_representante, direccion_representante = self.get_representante_info(cedula_representante)

            # Información de la escuela
            school_info = self.school_info

            # Fecha actual
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Estilos personalizados
            school_style = ParagraphStyle(
                name='SchoolStyle',
                parent=styles['Normal'],
                alignment=TA_LEFT,
                fontSize=10,
                leading=12,
            )

            rep_info_style = ParagraphStyle(
                name='RepInfoStyle',
                parent=styles['Normal'],
                alignment=TA_RIGHT,
                fontSize=10,
                leading=12,
            )

            # Formatear la información del colegio con saltos de línea
            school_paragraph = Paragraph(school_info.replace('\n', '<br/>'), school_style)

            # Formatear la información del representante
            rep_info = f"""
            Fecha: {fecha}<br/>
            Cédula Representante: {cedula_representante}<br/>
            Nombre: {nombre_representante}<br/>
            Dirección: {direccion_representante}
            """
            rep_info_paragraph = Paragraph(rep_info, rep_info_style)

            # Crear una tabla para la cabecera con dos columnas
            header_data = [
                [school_paragraph, rep_info_paragraph]
            ]

            header_table = Table(header_data, colWidths=[270, 270])  # Ajustar los anchos según sea necesario

            # Estilo de la tabla del encabezado
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Alineación de la primera celda (colegio)
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),   # Alineación de la segunda celda (representante)
            ]))

            elements.append(header_table)

            # Espacio
            elements.append(Spacer(1, 20))

            # Encabezados de la tabla
            encabezados = ['Alumno', 'Mes', 'Tipo de Pago', 'Monto', 'Curso']

            # Datos de la tabla
            data = [encabezados]

            total = 0
            for reg in self.registros:
                fila = [reg[3], reg[7], reg[6], f"${reg[5]:,.2f}", reg[8]]
                data.append(fila)
                total += reg[5]

            # Crear la tabla sin el total
            table = Table(data, colWidths=[150, 100, 150, 80, 80])

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Fondo de los encabezados
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color de texto de los encabezados
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente de los encabezados
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaciado inferior de los encabezados
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo de las filas de datos
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
            ])

            table.setStyle(estilo_tabla)

            elements.append(table)

            # Añadir un espacio antes del total
            elements.append(Spacer(1, 20))

            # Estilo para el "Total a Pagar" alineado a la derecha
            right_aligned_style = ParagraphStyle(
                name='RightAligned',
                parent=styles['Normal'],
                alignment=TA_RIGHT,
                fontSize=12,
                leading=14,
                spaceAfter=20,
                spaceBefore=20,
            )

            # Añadir el "Total a Pagar" como un párrafo alineado a la derecha
            total_paragraph = Paragraph(f"Total a Pagar: ${total:,.2f}", right_aligned_style)
            elements.append(total_paragraph)

            # Construir el PDF
            document.build(elements)

            messagebox.showinfo("PDF Generado", f"El recibo ha sido generado como '{os.path.basename(filename)}'.", parent=self.root)
        except Exception as e:
            logging.error(f"Error al generar el PDF: {e}")
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}", parent=self.root)

    def clear_entries(self):
        # Limpiar todos los campos
        self.ci_entry.delete(0, 'end')
        for combobox in self.alumnos_comboboxes:
            combobox.set('')
        for combobox in self.meses_comboboxes:
            combobox.set('')
        for combobox in self.tipos_comboboxes:
            combobox.set('Mensualidad')
        for entry in self.monto_entries:
            entry.delete(0, 'end')
        self.registros.clear()

    def show_success_message(self):
        messagebox.showinfo("Éxito", "El proceso se completó con éxito", parent=self.root)

    def close_tab(self):
        self.notebook.forget(self.fact_frame)
        self.notebook.place_forget()  # Oculta el notebook


# Ejecución principal
def main():
    root = tk.Tk()
    root.title("Facturación")
    root.geometry("1024x768")
    root.configure(bg='#D9D9D9')
    app = FacturacionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
