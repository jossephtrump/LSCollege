import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from databaseManager import mydb
import xlsxwriter  # Necesitas instalar esta librería: pip install XlsxWriter

class CobranzaApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.sort_column = None
        self.sort_reverse = False
        self.initialize_ui()

    def initialize_ui(self):
        # Usar el Notebook existente en el parent_frame
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        self.cobranza_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cobranza_frame, text="Cobranza")
        self.cobranza_frame.configure(borderwidth=2, relief=tk.SUNKEN)

        self.create_widgets()

        close_button = tk.Button(self.cobranza_frame, text=" X ", font=('noto sans', 10, 'bold'),
                                 bg='red2', fg='white', bd=1, command=self.close_tab)
        close_button.place(relx=0.999, rely=0.001, anchor='ne')

    def create_widgets(self):
        font = ('noto sans', 10, 'bold')
        font_2 = ("noto sans", 8)

        # Campo para la búsqueda por cédula de alumno
        cedula_label = tk.Label(self.cobranza_frame, text="Cédula Alumno:", font=font)
        cedula_label.place(relx=0.02, rely=0.02)
        self.cedula_entry = ttk.Entry(self.cobranza_frame, font=font)
        self.cedula_entry.bind("<Return>", lambda event: self.buscar_por_cedula())
        self.cedula_entry.bind("<KP_Enter>", lambda event: self.buscar_por_cedula())
        self.cedula_entry.place(relx=0.15, rely=0.02, width=150)
        buscar_cedula_button = tk.Button(self.cobranza_frame, text="Buscar", font=("noto sans", 8), command=self.buscar_por_cedula, bg="lightblue")
        buscar_cedula_button.place(relx=0.262, rely=0.018)

        # Campo para la búsqueda por cédula de representante
        cedula_rep_label = tk.Label(self.cobranza_frame, text="Cédula Representante:", font=font)
        cedula_rep_label.place(relx=0.5, rely=0.02)
        self.cedula_rep_entry = ttk.Entry(self.cobranza_frame, font=font)
        self.cedula_rep_entry.bind("<Return>", lambda event: self.buscar_por_representante())
        self.cedula_rep_entry.bind("<KP_Enter>", lambda event: self.buscar_por_representante())
        self.cedula_rep_entry.place(relx=0.65, rely=0.02, width=150)
        buscar_cedula_rep_button = tk.Button(self.cobranza_frame, text="Buscar", font=font_2, command=self.buscar_por_representante, bg="lightblue")
        buscar_cedula_rep_button.place(relx=0.762, rely=0.018)

        # Lista desplegable con los cursos disponibles
        curso_label = tk.Label(self.cobranza_frame, text="Curso:", font=font)
        curso_label.place(relx=0.02, rely=0.1)
        cursos = self.obtener_cursos()
        cursos.insert(0, "Todos")  # Agregar opción "Todos"
        self.curso_combobox = ttk.Combobox(self.cobranza_frame, font=font, values=cursos)
        self.curso_combobox.place(relx=0.15, rely=0.1, width=150)
        self.curso_combobox.set("Todos")
        buscar_curso_button = tk.Button(self.cobranza_frame, text="Buscar", font=font_2, command=self.buscar_por_curso, bg="lightblue")
        buscar_curso_button.place(relx=0.262, rely=0.095)

        # Campo para la búsqueda por mes
        mes_label = tk.Label(self.cobranza_frame, text="Mes:", font=font)
        mes_label.place(relx=0.55, rely=0.1)
        meses = [
            "Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.mes_combobox = ttk.Combobox(self.cobranza_frame, font=font, values=meses)
        self.mes_combobox.place(relx=0.65, rely=0.1, width=150)
        self.mes_combobox.set("Todos")
        buscar_mes_button = tk.Button(self.cobranza_frame, text="Buscar", font=font_2, command=self.buscar_por_mes, bg="lightblue")
        buscar_mes_button.place(relx=0.762, rely=0.095)

        # Botón para limpiar el Treeview
        limpiar_button = tk.Button(self.cobranza_frame, text="Limpiar", font=font, command=self.limpiar_treeview, bg="yellow")
        limpiar_button.place(relx=0.85, rely=0.92)

        # Botón para exportar datos
        exportar_button = tk.Button(self.cobranza_frame, text="Exportar", font=font, command=self.exportar_datos, bg="green", fg="white")
        exportar_button.place(relx=0.95, rely=0.92)

        # Crear el Treeview para mostrar los pagos
        columns = ('cedula_estudiante', 'nombre_alumno', 'curso', 'mes', 'monto', 'tipo_pago')
        self.tree = ttk.Treeview(self.cobranza_frame, columns=columns, show='headings')

        # Definir encabezados con funcionalidad de ordenamiento
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(), command=lambda _col=col: self.sort_treeview_column(_col, False))

        # Definir anchos de columnas
        self.tree.column('cedula_estudiante', width=120)
        self.tree.column('nombre_alumno', width=150)
        self.tree.column('curso', width=80)
        self.tree.column('mes', width=80)
        self.tree.column('monto', width=100)
        self.tree.column('tipo_pago', width=120)

        self.tree.place(relx=0.02, rely=0.2, relwidth=0.96, relheight=0.7)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.cobranza_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.2, relheight=0.7)

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
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula.")
            return

        try:
            cursor = mydb.cursor()
            query = """
            SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago
            FROM registro_pagos rp
            WHERE rp.cedula_estudiante = %s
            """
            cursor.execute(query, (cedula,))
            result = cursor.fetchall()
            cursor.close()

            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos para este alumno.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def buscar_por_representante(self):
        cedula_representante = self.cedula_rep_entry.get().strip()
        if not cedula_representante:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de representante.")
            return

        try:
            cursor = mydb.cursor()
            # Obtener los alumnos asociados al representante
            query_alumnos = "SELECT cedula FROM alumno WHERE cedula_representante = %s"
            cursor.execute(query_alumnos, (cedula_representante,))
            alumnos = cursor.fetchall()

            if alumnos:
                cedulas_alumnos = [alumno[0] for alumno in alumnos]

                # Obtener los pagos de los alumnos asociados
                query_pagos = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago
                FROM registro_pagos rp
                WHERE rp.cedula_estudiante IN (%s)
                """ % ','.join(['%s'] * len(cedulas_alumnos))

                cursor.execute(query_pagos, cedulas_alumnos)
                result = cursor.fetchall()
                cursor.close()

                if result:
                    self.actualizar_treeview(result)
                else:
                    messagebox.showinfo("Sin Resultados", "No se encontraron pagos para los alumnos asociados a este representante.")
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron alumnos asociados a este representante.")
                cursor.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def buscar_por_curso(self):
        curso = self.curso_combobox.get().strip()
        if not curso:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un curso.")
            return

        try:
            cursor = mydb.cursor()
            if curso == "Todos":
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago
                FROM registro_pagos rp
                """
                cursor.execute(query)
            else:
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago
                FROM registro_pagos rp
                WHERE rp.curso = %s
                """
                cursor.execute(query, (curso,))
            result = cursor.fetchall()
            cursor.close()

            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos para este curso.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def buscar_por_mes(self):
        mes = self.mes_combobox.get().strip()
        if not mes:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un mes.")
            return

        try:
            cursor = mydb.cursor()
            if mes == "Todos":
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago
                FROM registro_pagos rp
                """
                cursor.execute(query)
            else:
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago
                FROM registro_pagos rp
                WHERE rp.mes = %s
                """
                cursor.execute(query, (mes,))
            result = cursor.fetchall()
            cursor.close()

            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos para este mes.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def actualizar_treeview(self, data):
        # Guardar los datos para ordenamiento y exportación
        self.tree_data = data

        # Limpiar el Treeview antes de cargar nuevos datos
        for record in self.tree.get_children():
            self.tree.delete(record)

        # Insertar nuevos registros y resaltar a los morosos
        for row in data:
            tag = 'moroso' if row[5].lower() == 'moroso' else 'al_dia'
            self.tree.insert('', 'end', values=row, tags=(tag,))

        # Resaltar los morosos en rojo
        self.tree.tag_configure('moroso', background='red')
        self.tree.tag_configure('al_dia', background='white')

    def limpiar_treeview(self):
        for record in self.tree.get_children():
            self.tree.delete(record)
        self.tree_data = []

        # Limpiar los campos de cédula
        self.cedula_entry.delete(0, tk.END)
        self.cedula_rep_entry.delete(0, tk.END)

        # Restablecer los Combobox a "Todos"
        self.curso_combobox.set("Todos")
        self.mes_combobox.set("Todos")

    def sort_treeview_column(self, col, reverse):
        # Obtener los datos actuales del Treeview
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        # Intentar convertir a número para ordenar correctamente
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0], reverse=reverse)

        # Reordenar los ítems en el Treeview
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

        # Alternar el estado de ordenamiento
        self.tree.heading(col, command=lambda: self.sort_treeview_column(col, not reverse))

    def exportar_datos(self):
        if not hasattr(self, 'tree_data') or not self.tree_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if not file_path:
            return  # El usuario canceló el diálogo

        try:
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()

            # Definir formatos
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
            red_format = workbook.add_format({'bg_color': '#FFC7CE'})

            # Escribir encabezados
            headers = ['Cédula Estudiante', 'Nombre Alumno', 'Curso', 'Mes', 'Monto', 'Tipo de Pago']
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header, header_format)

            # Escribir datos
            for row_num, row_data in enumerate(self.tree_data, start=1):
                for col_num, cell_data in enumerate(row_data):
                    if row_data[5].lower() == 'moroso':
                        worksheet.write(row_num, col_num, cell_data, red_format)
                    else:
                        worksheet.write(row_num, col_num, cell_data)

            workbook.close()
            messagebox.showinfo("Éxito", f"Datos exportados exitosamente a {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar los datos: {e}")

    def close_tab(self):
        self.notebook.forget(self.cobranza_frame)
        self.notebook.destroy()
