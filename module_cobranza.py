"""
Este archivo contiene la clase CobranzaApp que se encarga de gestionar los pagos
de estudiantes en una institución educativa. Incluye funcionalidades para buscar pagos,
exportar datos y mejorar la experiencia del usuario.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from databaseManager import mydb
import xlsxwriter
import logging
import datetime

# Configurar logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')


class DataManager:
    """Clase para manejar las operaciones de base de datos."""

    def __init__(self):
        self.mydb = mydb

    def obtener_pagos_por_cedula(self, cedula):
        try:
            cursor = self.mydb.cursor()
            query = """
            SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
            FROM registro_pagos rp
            WHERE rp.cedula_estudiante = %s
            """
            cursor.execute(query, (cedula,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"Error al consultar pagos por cédula: {e}")
            raise

    def obtener_pagos_por_representante(self, cedulas_alumnos):
        try:
            cursor = self.mydb.cursor()
            placeholders = ','.join(['%s'] * len(cedulas_alumnos))
            query = f"""
            SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
            FROM registro_pagos rp
            WHERE rp.cedula_estudiante IN ({placeholders})
            """
            cursor.execute(query, cedulas_alumnos)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"Error al consultar pagos por representante: {e}")
            raise

    def obtener_pagos_por_curso(self, curso):
        try:
            cursor = self.mydb.cursor()
            if curso == "Todos":
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
                FROM registro_pagos rp
                """
                cursor.execute(query)
            else:
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
                FROM registro_pagos rp
                WHERE rp.curso = %s
                """
                cursor.execute(query, (curso,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"Error al consultar pagos por curso: {e}")
            raise

    def obtener_pagos_por_mes(self, mes):
        try:
            cursor = self.mydb.cursor()
            if mes == "Todos":
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
                FROM registro_pagos rp
                """
                cursor.execute(query)
            else:
                query = """
                SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
                FROM registro_pagos rp
                WHERE rp.mes = %s
                """
                cursor.execute(query, (mes,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"Error al consultar pagos por mes: {e}")
            raise

    def obtener_pagos_por_rango_fecha(self, fecha_inicio, fecha_fin):
        try:
            cursor = self.mydb.cursor()
            query = """
            SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto, rp.tipo_pago, rp.fecha_pago
            FROM registro_pagos rp
            WHERE rp.fecha_pago BETWEEN %s AND %s
            """
            cursor.execute(query, (fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d')))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logging.error(f"Error al consultar pagos por rango de fechas: {e}")
            raise

    def obtener_cursos(self):
        try:
            cursor = self.mydb.cursor()
            query = "SELECT DISTINCT curso FROM alumno ORDER BY curso"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            cursos = [row[0] for row in result]
            return cursos
        except Exception as e:
            logging.error(f"Error al consultar los cursos: {e}")
            raise

    def obtener_alumnos_por_representante(self, cedula_representante):
        try:
            cursor = self.mydb.cursor()
            query_alumnos = "SELECT cedula FROM alumno WHERE cedula_representante = %s"
            cursor.execute(query_alumnos, (cedula_representante,))
            alumnos = cursor.fetchall()
            cursor.close()
            cedulas_alumnos = [alumno[0] for alumno in alumnos]
            return cedulas_alumnos
        except Exception as e:
            logging.error(f"Error al obtener alumnos por representante: {e}")
            raise

    def obtener_morosos(self, curso=None, mes=None, fecha_inicio=None, fecha_fin=None):
        try:
            cursor = self.mydb.cursor()

            # Construir la consulta para obtener alumnos
            query_alumnos = "SELECT cedula, nombre, curso FROM alumno"
            condiciones_alumnos = []
            parametros_alumnos = []

            if curso:
                condiciones_alumnos.append("curso = %s")
                parametros_alumnos.append(curso)

            if condiciones_alumnos:
                query_alumnos += " WHERE " + " AND ".join(condiciones_alumnos)

            cursor.execute(query_alumnos, parametros_alumnos)
            alumnos = cursor.fetchall()
            alumnos_dict = {alumno[0]: alumno for alumno in alumnos}

            # Si no hay alumnos, retornar lista vacía
            if not alumnos_dict:
                cursor.close()
                return []

            # Construir la consulta para obtener pagos
            query_pagos = "SELECT DISTINCT cedula_estudiante FROM registro_pagos"
            condiciones_pagos = []
            parametros_pagos = []

            if fecha_inicio and fecha_fin:
                condiciones_pagos.append("fecha_pago BETWEEN %s AND %s")
                parametros_pagos.extend([fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d')])
            elif mes:
                condiciones_pagos.append("mes = %s")
                parametros_pagos.append(mes)
            else:
                # Si no se especifica mes ni fechas, usar el mes actual
                mes_actual = datetime.datetime.now().strftime('%B')
                condiciones_pagos.append("mes = %s")
                parametros_pagos.append(mes_actual)

            if curso:
                condiciones_pagos.append("curso = %s")
                parametros_pagos.append(curso)

            if condiciones_pagos:
                query_pagos += " WHERE " + " AND ".join(condiciones_pagos)

            cursor.execute(query_pagos, parametros_pagos)
            pagos_realizados = cursor.fetchall()
            cedulas_pagadas = {pago[0] for pago in pagos_realizados}

            # Filtrar alumnos que no están en la lista de pagos realizados
            morosos = [alumnos_dict[cedula] for cedula in alumnos_dict if cedula not in cedulas_pagadas]

            cursor.close()
            return morosos
        except Exception as e:
            logging.error(f"Error al obtener morosos: {e}")
            raise


class CobranzaApp:
    """Aplicación para gestionar pagos de estudiantes."""

    def __init__(self, parent_frame):
        """Inicializa la aplicación de cobranza."""
        self.parent_frame = parent_frame
        self.sort_column = None
        self.sort_reverse = False
        self.data_manager = DataManager()
        self.initialize_ui()

    def initialize_ui(self):
        """Inicializa la interfaz de usuario."""
        # Configurar estilos
        self.style = ttk.Style()
        self.style.configure('TButton', font=('noto sans', 10))
        self.style.configure('TLabel', font=('noto sans', 10))
        self.style.configure('TEntry', font=('noto sans', 10))
        self.style.configure('TCombobox', font=('noto sans', 10))
        self.style.configure('TDateEntry', font=('noto sans', 10))

        # Usar el Notebook existente en el parent_frame
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.cobranza_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cobranza_frame, text="Cobranza")
        self.cobranza_frame.configure(borderwidth=2, relief=tk.SUNKEN)

        self.create_widgets()

        close_button = tk.Button(self.cobranza_frame, text=" X ", font=('noto sans', 10, 'bold'),
                                 bg='red2', fg='white', bd=1, command=self.close_tab)
        close_button.place(relx=0.999, rely=0.001, anchor='ne')

    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        font = ('noto sans', 10)
        font_2 = ("noto sans", 8)

        # Campo para la búsqueda por cédula de alumno
        cedula_label = ttk.Label(self.cobranza_frame, text="Cédula Alumno:")
        cedula_label.place(relx=0.02, rely=0.02)
        self.cedula_entry = ttk.Entry(self.cobranza_frame)
        self.cedula_entry.place(relx=0.15, rely=0.02, width=150)
        self.cedula_entry.bind("<Return>", lambda event: self.buscar_por_cedula())
        self.cedula_entry.bind("<KP_Enter>", lambda event: self.buscar_por_cedula())
        buscar_cedula_button = ttk.Button(self.cobranza_frame, text="Buscar", command=self.buscar_por_cedula)
        buscar_cedula_button.place(relx=0.31, rely=0.018)

        # Campo para la búsqueda por cédula de representante
        cedula_rep_label = ttk.Label(self.cobranza_frame, text="Cédula Representante:")
        cedula_rep_label.place(relx=0.5, rely=0.02)
        self.cedula_rep_entry = ttk.Entry(self.cobranza_frame)
        self.cedula_rep_entry.place(relx=0.65, rely=0.02, width=150)
        self.cedula_rep_entry.bind("<Return>", lambda event: self.buscar_por_representante())
        self.cedula_rep_entry.bind("<KP_Enter>", lambda event: self.buscar_por_representante())
        buscar_cedula_rep_button = ttk.Button(self.cobranza_frame, text="Buscar", command=self.buscar_por_representante)
        buscar_cedula_rep_button.place(relx=0.81, rely=0.018)

        # Lista desplegable con los cursos disponibles
        curso_label = ttk.Label(self.cobranza_frame, text="Curso:")
        curso_label.place(relx=0.02, rely=0.08)
        cursos = self.data_manager.obtener_cursos()
        cursos.insert(0, "Todos")  # Agregar opción "Todos"
        self.curso_combobox = ttk.Combobox(self.cobranza_frame, values=cursos, state="readonly")
        self.curso_combobox.place(relx=0.15, rely=0.08, width=150)
        self.curso_combobox.set("Todos")
        buscar_curso_button = ttk.Button(self.cobranza_frame, text="Buscar", command=self.buscar_por_curso)
        buscar_curso_button.place(relx=0.31, rely=0.078)

        # Campo para la búsqueda por mes
        mes_label = ttk.Label(self.cobranza_frame, text="Mes:")
        mes_label.place(relx=0.5, rely=0.08)
        meses = [
            "Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.mes_combobox = ttk.Combobox(self.cobranza_frame, values=meses, state="readonly")
        self.mes_combobox.place(relx=0.65, rely=0.08, width=150)
        self.mes_combobox.set("Todos")
        buscar_mes_button = ttk.Button(self.cobranza_frame, text="Buscar", command=self.buscar_por_mes)
        buscar_mes_button.place(relx=0.81, rely=0.078)

        # Campos para el rango de fechas
        fecha_inicio_label = ttk.Label(self.cobranza_frame, text="Fecha Inicio:")
        fecha_inicio_label.place(relx=0.02, rely=0.14)
        self.fecha_inicio_entry = DateEntry(self.cobranza_frame, date_pattern='yyyy-mm-dd', state='readonly')
        self.fecha_inicio_entry.place(relx=0.15, rely=0.14, width=150)

        fecha_fin_label = ttk.Label(self.cobranza_frame, text="Fecha Fin:")
        fecha_fin_label.place(relx=0.5, rely=0.14)
        self.fecha_fin_entry = DateEntry(self.cobranza_frame, date_pattern='yyyy-mm-dd', state='readonly')
        self.fecha_fin_entry.place(relx=0.65, rely=0.14, width=150)

        buscar_fecha_button = ttk.Button(self.cobranza_frame, text="Buscar", command=self.buscar_por_fecha)
        buscar_fecha_button.place(relx=0.81, rely=0.138)

        # Botón para filtrar morosos
        morosos_button = ttk.Button(self.cobranza_frame, text="Filtrar Morosos", command=self.filtrar_morosos)
        morosos_button.place(relx=0.02, rely=0.20)

        # Botón para limpiar el Treeview
        limpiar_button = ttk.Button(self.cobranza_frame, text="Limpiar", command=self.limpiar_treeview)
        limpiar_button.place(relx=0.85, rely=0.92)

        # Botón para exportar datos
        exportar_button = ttk.Button(self.cobranza_frame, text="Exportar", command=self.exportar_datos)
        exportar_button.place(relx=0.92, rely=0.92)

        # Crear el Treeview para mostrar los pagos
        columns = ('cedula_estudiante', 'nombre_alumno', 'curso', 'mes', 'monto', 'tipo_pago', 'fecha_pago')
        self.tree = ttk.Treeview(self.cobranza_frame, columns=columns, show='headings')

        # Definir encabezados con funcionalidad de ordenamiento
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(),
                              command=lambda _col=col: self.sort_treeview_column(_col, False))

        # Definir anchos de columnas
        self.tree.column('cedula_estudiante', width=120)
        self.tree.column('nombre_alumno', width=150)
        self.tree.column('curso', width=80)
        self.tree.column('mes', width=80)
        self.tree.column('monto', width=100)
        self.tree.column('tipo_pago', width=120)
        self.tree.column('fecha_pago', width=100)

        self.tree.place(relx=0.02, rely=0.25, relwidth=0.96, relheight=0.65)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.cobranza_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.25, relheight=0.65)

    def es_cedula_valida(self, cedula):
        """Valida que la cédula sea numérica."""
        return cedula.isdigit()

    def buscar_por_cedula(self):
        """Busca pagos por cédula de alumno."""
        cedula = self.cedula_entry.get().strip()
        if not self.es_cedula_valida(cedula):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula válida.")
            return

        try:
            result = self.data_manager.obtener_pagos_por_cedula(cedula)
            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos para este alumno.")
        except Exception:
            messagebox.showerror("Error", "Ocurrió un error al consultar los pagos. Por favor, inténtelo más tarde.")

    def buscar_por_representante(self):
        """Busca pagos por cédula de representante."""
        cedula_representante = self.cedula_rep_entry.get().strip()
        if not self.es_cedula_valida(cedula_representante):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de representante válida.")
            return

        try:
            cedulas_alumnos = self.data_manager.obtener_alumnos_por_representante(cedula_representante)
            if cedulas_alumnos:
                result = self.data_manager.obtener_pagos_por_representante(cedulas_alumnos)
                if result:
                    self.actualizar_treeview(result)
                else:
                    messagebox.showinfo("Sin Resultados", "No se encontraron pagos para los alumnos asociados a este representante.")
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron alumnos asociados a este representante.")
        except Exception:
            messagebox.showerror("Error", "Ocurrió un error al consultar los pagos. Por favor, inténtelo más tarde.")

    def buscar_por_curso(self):
        """Busca pagos por curso."""
        curso = self.curso_combobox.get().strip()
        if not curso:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un curso.")
            return

        try:
            result = self.data_manager.obtener_pagos_por_curso(curso)
            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos para este curso.")
        except Exception:
            messagebox.showerror("Error", "Ocurrió un error al consultar los pagos. Por favor, inténtelo más tarde.")

    def buscar_por_mes(self):
        """Busca pagos por mes."""
        mes = self.mes_combobox.get().strip()
        if not mes:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un mes.")
            return

        try:
            result = self.data_manager.obtener_pagos_por_mes(mes)
            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos para este mes.")
        except Exception:
            messagebox.showerror("Error", "Ocurrió un error al consultar los pagos. Por favor, inténtelo más tarde.")

    def buscar_por_fecha(self):
        """Busca pagos por rango de fechas."""
        fecha_inicio = self.fecha_inicio_entry.get_date()
        fecha_fin = self.fecha_fin_entry.get_date()

        if fecha_inicio > fecha_fin:
            messagebox.showwarning("Entrada Inválida", "La fecha de inicio no puede ser posterior a la fecha fin.")
            return

        try:
            result = self.data_manager.obtener_pagos_por_rango_fecha(fecha_inicio, fecha_fin)
            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos en este rango de fechas.")
        except Exception:
            messagebox.showerror("Error", "Ocurrió un error al consultar los pagos. Por favor, inténtelo más tarde.")

    def filtrar_morosos(self):
        """Filtra y muestra a los alumnos morosos según los filtros aplicados."""
        curso = self.curso_combobox.get().strip()
        mes = self.mes_combobox.get().strip()
        fecha_inicio = self.fecha_inicio_entry.get_date()
        fecha_fin = self.fecha_fin_entry.get_date()

        # Validar fechas
        if fecha_inicio > fecha_fin:
            messagebox.showwarning("Entrada Inválida", "La fecha de inicio no puede ser posterior a la fecha fin.")
            return

        # Determinar los filtros aplicados
        filtro_curso = curso if curso != "Todos" else None
        filtro_mes = mes if mes != "Todos" else None
        filtro_fecha_inicio = fecha_inicio if fecha_inicio != fecha_fin else None
        filtro_fecha_fin = fecha_fin if fecha_inicio != fecha_fin else None

        try:
            morosos = self.data_manager.obtener_morosos(
                curso=filtro_curso,
                mes=filtro_mes,
                fecha_inicio=filtro_fecha_inicio,
                fecha_fin=filtro_fecha_fin
            )
            if morosos:
                # Limpiar el Treeview antes de cargar nuevos datos
                for record in self.tree.get_children():
                    self.tree.delete(record)
                self.tree_data = []

                # Insertar morosos en el Treeview
                for alumno in morosos:
                    cedula, nombre, curso = alumno
                    self.tree.insert('', 'end', values=(cedula, nombre, curso, '', '', 'Moroso', ''), tags=('moroso',))
                    self.tree_data.append((cedula, nombre, curso, '', '', 'Moroso', ''))

                # Cambiar el color del texto a rojo para morosos
                self.tree.tag_configure('moroso', foreground='red')
            else:
                messagebox.showinfo("Sin Resultados", "No hay alumnos morosos con los filtros seleccionados.")
        except Exception as e:
            logging.error(f"Error al filtrar morosos: {e}")
            messagebox.showerror("Error", "Ocurrió un error al obtener la lista de morosos. Por favor, inténtelo más tarde.")

    def actualizar_treeview(self, data):
        """Actualiza el Treeview con los datos proporcionados."""
        # Guardar los datos para ordenamiento y exportación
        self.tree_data = data

        # Limpiar el Treeview antes de cargar nuevos datos
        for record in self.tree.get_children():
            self.tree.delete(record)

        # Insertar nuevos registros y cambiar color del texto para morosos
        for row in data:
            tag = 'moroso' if row[5].lower() == 'moroso' else 'al_dia'
            self.tree.insert('', 'end', values=row, tags=(tag,))

        # Configurar el color del texto
        self.tree.tag_configure('moroso', foreground='red')
        self.tree.tag_configure('al_dia', foreground='black')

    def limpiar_treeview(self):
        """Limpia el Treeview y restablece los campos de entrada."""
        for record in self.tree.get_children():
            self.tree.delete(record)
        self.tree_data = []

        # Limpiar los campos de cédula
        self.cedula_entry.delete(0, tk.END)
        self.cedula_rep_entry.delete(0, tk.END)

        # Restablecer los Combobox a "Todos"
        self.curso_combobox.set("Todos")
        self.mes_combobox.set("Todos")

        # Restablecer fechas
        self.fecha_inicio_entry.set_date(datetime.date.today())
        self.fecha_fin_entry.set_date(datetime.date.today())

    def sort_treeview_column(self, col, reverse):
        """Ordena el Treeview según la columna seleccionada."""
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
        """Exporta los datos del Treeview a un archivo Excel."""
        if not hasattr(self, 'tree_data') or not self.tree_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if not file_path:
            return  # El usuario canceló el diálogo

        # Mostrar cursor de espera
        self.parent_frame.config(cursor="wait")
        self.parent_frame.update()

        try:
            with xlsxwriter.Workbook(file_path) as workbook:
                worksheet = workbook.add_worksheet()

                # Definir formatos
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
                red_format = workbook.add_format({'font_color': 'red'})
                normal_format = workbook.add_format()

                # Escribir encabezados
                headers = ['Cédula Estudiante', 'Nombre Alumno', 'Curso', 'Mes', 'Monto', 'Tipo de Pago', 'Fecha de Pago']
                worksheet.write_row(0, 0, headers, header_format)

                # Escribir datos
                for row_num, row_data in enumerate(self.tree_data, start=1):
                    format_to_apply = red_format if row_data[5].lower() == 'moroso' else normal_format
                    worksheet.write_row(row_num, 0, row_data, format_to_apply)

                # Ajustar ancho de columnas
                worksheet.set_column('A:G', 20)

            messagebox.showinfo("Éxito", f"Datos exportados exitosamente a {file_path}")
        except Exception as e:
            logging.error(f"Error al exportar los datos: {e}")
            messagebox.showerror("Error", "Ocurrió un error al exportar los datos. Por favor, inténtelo más tarde.")
        finally:
            # Restablecer el cursor
            self.parent_frame.config(cursor="")

    def close_tab(self):
        """Cierra la pestaña actual."""
        self.notebook.forget(self.cobranza_frame)
        self.notebook.destroy()
