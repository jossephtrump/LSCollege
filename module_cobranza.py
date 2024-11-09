"""
Este archivo contiene la clase CobranzaApp que se encarga de gestionar los pagos
de estudiantes en una institución educativa. Incluye funcionalidades para buscar pagos,
filtrar morosos y mejorar la experiencia del usuario.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import mysql.connector
import xlsxwriter
import logging
import datetime
import locale

# Configurar logging
logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Establecer la configuración regional a español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para sistemas Unix/Linux
except:
    locale.setlocale(locale.LC_TIME, 'Spanish_Spain')  # Para sistemas Windows


class DataManager:
    """Clase para manejar las operaciones de base de datos."""

    def obtener_conexion(self):
        """Crea una nueva conexión a la base de datos."""
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="colegio"  # Cambia esto al nombre de tu base de datos
            )
            return mydb
        except mysql.connector.Error as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
            raise

    def obtener_pagos(self, cedula=None, cedula_representante=None, curso=None, mes=None, fecha_inicio=None, fecha_fin=None):
        """Obtiene los pagos realizados según los filtros seleccionados."""
        try:
            mydb = self.obtener_conexion()
            cursor = mydb.cursor()

            query = """
            SELECT rp.cedula_estudiante, rp.nombre_alumno, rp.curso, rp.mes, rp.monto,
                   rp.tipo_pago, a.cedula_representante
            FROM registro_pagos rp
            JOIN alumno a ON rp.cedula_estudiante = a.cedula
            """

            condiciones = []
            parametros = []

            if cedula:
                condiciones.append("rp.cedula_estudiante = %s")
                parametros.append(cedula)

            if cedula_representante:
                condiciones.append("a.cedula_representante = %s")
                parametros.append(cedula_representante)

            if curso and curso != "Todos":
                condiciones.append("rp.curso = %s")
                parametros.append(curso)

            if mes and mes != "Todos":
                condiciones.append("rp.mes = %s")
                parametros.append(mes)

            if fecha_inicio and fecha_fin:
                condiciones.append("rp.fecha_pago BETWEEN %s AND %s")
                parametros.extend([fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d')])

            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)

            cursor.execute(query, parametros)
            result = cursor.fetchall()
            cursor.close()
            mydb.close()
            return result
        except Exception as e:
            logging.error(f"Error al consultar pagos: {e}")
            raise

    def obtener_cursos(self):
        """Obtiene una lista de todos los cursos disponibles."""
        try:
            mydb = self.obtener_conexion()
            cursor = mydb.cursor()
            query = "SELECT DISTINCT curso FROM alumno ORDER BY curso"
            cursor.execute(query)
            result = cursor.fetchall()
            cursos = [row[0] for row in result]
            cursor.close()
            mydb.close()
            return cursos
        except Exception as e:
            logging.error(f"Error al consultar los cursos: {e}")
            raise

    def obtener_meses(self, fecha_inicio=None, fecha_fin=None):
        """Obtiene una lista de meses en español entre dos fechas."""
        meses = []
        if fecha_inicio and fecha_fin:
            start_month = fecha_inicio.month
            start_year = fecha_inicio.year
            end_month = fecha_fin.month
            end_year = fecha_fin.year

            # Crear un rango de meses entre las fechas
            current_year = start_year
            current_month = start_month
            while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
                meses.append((current_year, current_month))
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
        else:
            # Si no se proporcionan fechas, asumimos desde agosto hasta el mes actual
            today = datetime.date.today()
            current_month = today.month
            current_year = today.year

            if current_month >= 8:
                start_month = 8
                start_year = current_year
            else:
                start_month = 8
                start_year = current_year - 1

            while (start_year < current_year) or (start_year == current_year and start_month <= current_month):
                meses.append((start_year, start_month))
                if start_month == 12:
                    start_month = 1
                    start_year += 1
                else:
                    start_month += 1

        # Convertir los meses a nombres de meses en español
        meses_nombres = []
        for year, month in meses:
            nombre_mes = datetime.date(year, month, 1).strftime('%B').capitalize()
            meses_nombres.append(nombre_mes)

        return meses_nombres

    def obtener_morosos(self, cedula=None, cedula_representante=None, curso=None, mes=None, fecha_inicio=None, fecha_fin=None):
        """Obtiene los alumnos morosos según los filtros seleccionados."""
        try:
            mydb = self.obtener_conexion()
            cursor = mydb.cursor()

            # Obtener los meses que se deben considerar
            if mes and mes != "Todos":
                meses_faltantes = [mes]
            else:
                meses_faltantes = self.obtener_meses(fecha_inicio, fecha_fin)

            # Convertir los nombres de meses a título para coincidir con el formato de los datos
            meses_faltantes = [m.capitalize() for m in meses_faltantes]

            # Construir la consulta base para obtener alumnos
            query = """
            SELECT a.cedula, a.nombre, a.curso, a.cedula_representante
            FROM alumno a
            """
            condiciones = []
            parametros = []

            if cedula:
                condiciones.append("a.cedula = %s")
                parametros.append(cedula)

            if cedula_representante:
                condiciones.append("a.cedula_representante = %s")
                parametros.append(cedula_representante)

            if curso and curso != "Todos":
                condiciones.append("a.curso = %s")
                parametros.append(curso)

            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)

            cursor.execute(query, parametros)
            alumnos = cursor.fetchall()

            morosos = []

            for alumno in alumnos:
                cedula_alumno = alumno[0]
                nombre_alumno = alumno[1]
                curso_alumno = alumno[2]
                cedula_rep = alumno[3]

                # Verificar los pagos realizados por el alumno
                if meses_faltantes:
                    placeholders = ','.join(['%s'] * len(meses_faltantes))
                    query_pagos = f"""
                    SELECT DISTINCT mes FROM registro_pagos
                    WHERE cedula_estudiante = %s AND mes IN ({placeholders})
                    """
                    parametros_pagos = [cedula_alumno] + meses_faltantes

                    cursor.execute(query_pagos, parametros_pagos)
                    pagos_realizados = cursor.fetchall()
                    meses_pagados = {pago[0] for pago in pagos_realizados}

                    # Obtener los meses que el alumno debe
                    meses_pendientes = set(meses_faltantes) - meses_pagados

                    for mes_pendiente in meses_pendientes:
                        morosos.append((
                            cedula_alumno,
                            nombre_alumno,
                            curso_alumno,
                            mes_pendiente,
                            '50$',  # Monto predeterminado
                            '',     # Tipo de pago en blanco
                            cedula_rep
                        ))
            cursor.close()
            mydb.close()
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
        # Campo para la búsqueda por cédula de alumno
        ttk.Label(self.cobranza_frame, text="Cédula Alumno:").place(relx=0.02, rely=0.02)
        self.cedula_entry = ttk.Entry(self.cobranza_frame)
        self.cedula_entry.place(relx=0.15, rely=0.02, width=150)

        # Campo para la búsqueda por cédula de representante
        ttk.Label(self.cobranza_frame, text="Cédula Representante:").place(relx=0.5, rely=0.02)
        self.cedula_rep_entry = ttk.Entry(self.cobranza_frame)
        self.cedula_rep_entry.place(relx=0.65, rely=0.02, width=150)

        # Lista desplegable con los cursos disponibles
        ttk.Label(self.cobranza_frame, text="Curso:").place(relx=0.02, rely=0.08)
        cursos = self.data_manager.obtener_cursos()
        cursos.insert(0, "Todos")  # Agregar opción "Todos"
        self.curso_combobox = ttk.Combobox(self.cobranza_frame, values=cursos, state="readonly")
        self.curso_combobox.place(relx=0.15, rely=0.08, width=150)
        self.curso_combobox.set("Todos")

        # Campo para la búsqueda por mes
        ttk.Label(self.cobranza_frame, text="Mes:").place(relx=0.5, rely=0.08)
        meses = [
            "Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.mes_combobox = ttk.Combobox(self.cobranza_frame, values=meses, state="readonly")
        self.mes_combobox.place(relx=0.65, rely=0.08, width=150)
        self.mes_combobox.set("Todos")

        # Campos para el rango de fechas
        ttk.Label(self.cobranza_frame, text="Fecha Inicio:").place(relx=0.02, rely=0.14)
        self.fecha_inicio_entry = DateEntry(self.cobranza_frame, date_pattern='yyyy-mm-dd', state='readonly', locale='es_ES')
        self.fecha_inicio_entry.place(relx=0.15, rely=0.14, width=150)

        ttk.Label(self.cobranza_frame, text="Fecha Fin:").place(relx=0.5, rely=0.14)
        self.fecha_fin_entry = DateEntry(self.cobranza_frame, date_pattern='yyyy-mm-dd', state='readonly', locale='es_ES')
        self.fecha_fin_entry.place(relx=0.65, rely=0.14, width=150)

        # Botón para buscar pagos
        buscar_button = ttk.Button(self.cobranza_frame, text="Buscar Pagos", command=self.buscar_pagos)
        buscar_button.place(relx=0.02, rely=0.20)

        # Botón para filtrar morosos
        morosos_button = ttk.Button(self.cobranza_frame, text="Filtrar Morosos", command=self.filtrar_morosos)
        morosos_button.place(relx=0.15, rely=0.20)

        # Botón para limpiar el Treeview
        limpiar_button = ttk.Button(self.cobranza_frame, text="Limpiar", command=self.limpiar_treeview)
        limpiar_button.place(relx=0.85, rely=0.92)

        # Botón para exportar datos
        exportar_button = ttk.Button(self.cobranza_frame, text="Exportar", command=self.exportar_datos)
        exportar_button.place(relx=0.92, rely=0.92)

        # Crear el Treeview para mostrar los pagos
        columns = ('cedula_estudiante', 'nombre_alumno', 'curso', 'mes', 'monto', 'tipo_pago', 'cedula_representante')
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
        self.tree.column('cedula_representante', width=120)

        self.tree.place(relx=0.02, rely=0.25, relwidth=0.96, relheight=0.65)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.cobranza_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.25, relheight=0.65)

    def es_cedula_valida(self, cedula):
        """Valida que la cédula sea numérica."""
        return cedula.isdigit()

    def buscar_pagos(self):
        """Busca pagos según los filtros seleccionados."""
        cedula = self.cedula_entry.get().strip()
        cedula_representante = self.cedula_rep_entry.get().strip()
        curso = self.curso_combobox.get().strip()
        mes = self.mes_combobox.get().strip()
        fecha_inicio = self.fecha_inicio_entry.get_date()
        fecha_fin = self.fecha_fin_entry.get_date()

        # Validar cédulas
        if cedula and not self.es_cedula_valida(cedula):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de alumno válida.")
            return

        if cedula_representante and not self.es_cedula_valida(cedula_representante):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de representante válida.")
            return

        # Validar fechas
        if fecha_inicio > fecha_fin:
            messagebox.showwarning("Entrada Inválida", "La fecha de inicio no puede ser posterior a la fecha fin.")
            return

        # Determinar filtros
        filtro_curso = curso if curso != "Todos" else None
        filtro_mes = mes if mes != "Todos" else None
        filtro_fecha_inicio = fecha_inicio if fecha_inicio != fecha_fin else None
        filtro_fecha_fin = fecha_fin if fecha_inicio != fecha_fin else None

        try:
            result = self.data_manager.obtener_pagos(
                cedula=cedula if cedula else None,
                cedula_representante=cedula_representante if cedula_representante else None,
                curso=filtro_curso,
                mes=filtro_mes,
                fecha_inicio=filtro_fecha_inicio,
                fecha_fin=filtro_fecha_fin
            )
            if result:
                self.actualizar_treeview(result)
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron pagos con los filtros seleccionados.")
        except Exception as e:
            logging.error(f"Error al buscar pagos: {e}")
            messagebox.showerror("Error", "Ocurrió un error al consultar los pagos. Por favor, inténtelo más tarde.")

    def filtrar_morosos(self):
        """Filtra y muestra a los alumnos morosos según los filtros aplicados."""
        cedula = self.cedula_entry.get().strip()
        cedula_representante = self.cedula_rep_entry.get().strip()
        curso = self.curso_combobox.get().strip()
        mes = self.mes_combobox.get().strip()
        fecha_inicio = self.fecha_inicio_entry.get_date()
        fecha_fin = self.fecha_fin_entry.get_date()

        # Validar cédulas
        if cedula and not self.es_cedula_valida(cedula):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de alumno válida.")
            return

        if cedula_representante and not self.es_cedula_valida(cedula_representante):
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de representante válida.")
            return

        # Validar fechas
        if fecha_inicio > fecha_fin:
            messagebox.showwarning("Entrada Inválida", "La fecha de inicio no puede ser posterior a la fecha fin.")
            return

        # Determinar filtros
        filtro_curso = curso if curso != "Todos" else None
        filtro_mes = mes if mes != "Todos" else None
        filtro_fecha_inicio = fecha_inicio if fecha_inicio != fecha_fin else None
        filtro_fecha_fin = fecha_fin if fecha_inicio != fecha_fin else None

        try:
            morosos = self.data_manager.obtener_morosos(
                cedula=cedula if cedula else None,
                cedula_representante=cedula_representante if cedula_representante else None,
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
                    cedula_alumno, nombre, curso_alumno, mes_pendiente, monto, tipo_pago, cedula_rep = alumno
                    self.tree.insert('', 'end', values=(cedula_alumno, nombre, curso_alumno, mes_pendiente, monto, tipo_pago, cedula_rep), tags=('moroso',))
                    self.tree_data.append((cedula_alumno, nombre, curso_alumno, mes_pendiente, monto, tipo_pago, cedula_rep))

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

        # Insertar nuevos registros
        for row in data:
            self.tree.insert('', 'end', values=row)

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
                headers = ['Cédula Estudiante', 'Nombre Alumno', 'Curso', 'Mes', 'Monto', 'Tipo de Pago', 'Cédula Representante']
                worksheet.write_row(0, 0, headers, header_format)

                # Escribir datos
                for row_num, row_data in enumerate(self.tree_data, start=1):
                    format_to_apply = red_format if 'Moroso' in row_data else normal_format
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
