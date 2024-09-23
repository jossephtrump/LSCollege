import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from databaseManager import mydb

class CobranzaApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
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

        # Campo para la búsqueda por cédula de alumno
        cedula_label = tk.Label(self.cobranza_frame, text="Cédula Alumno:", font=font)
        cedula_label.place(relx=0.02, rely=0.02)
        self.cedula_entry = ttk.Entry(self.cobranza_frame, font=font)
        self.cedula_entry.place(relx=0.15, rely=0.02, width=150)
        buscar_cedula_button = tk.Button(self.cobranza_frame, text="Buscar", font=font, command=self.buscar_por_cedula)
        buscar_cedula_button.place(relx=0.32, rely=0.02)

        # Campo para la búsqueda por cédula de representante
        cedula_rep_label = tk.Label(self.cobranza_frame, text="Cédula Representante:", font=font)
        cedula_rep_label.place(relx=0.5, rely=0.02)
        self.cedula_rep_entry = ttk.Entry(self.cobranza_frame, font=font)
        self.cedula_rep_entry.place(relx=0.65, rely=0.02, width=150)
        buscar_cedula_rep_button = tk.Button(self.cobranza_frame, text="Buscar Representante", font=font, command=self.buscar_por_representante)
        buscar_cedula_rep_button.place(relx=0.82, rely=0.02)

        # Lista desplegable con los cursos disponibles
        curso_label = tk.Label(self.cobranza_frame, text="Curso:", font=font)
        curso_label.place(relx=0.02, rely=0.1)
        self.curso_combobox = ttk.Combobox(self.cobranza_frame, font=font, values=[
            "Preescolar", "Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Sexto",
            "Séptimo", "Octavo", "Noveno", "4to año", "5to año"
        ])
        self.curso_combobox.place(relx=0.15, rely=0.1, width=150)
        self.curso_combobox.set("Seleccione un curso")
        buscar_curso_button = tk.Button(self.cobranza_frame, text="Buscar Curso", font=font, command=self.buscar_por_curso)
        buscar_curso_button.place(relx=0.32, rely=0.1)

        # Campo para la búsqueda por mes
        mes_label = tk.Label(self.cobranza_frame, text="Mes:", font=font)
        mes_label.place(relx=0.5, rely=0.1)
        self.mes_combobox = ttk.Combobox(self.cobranza_frame, font=font, values=[
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        self.mes_combobox.place(relx=0.58, rely=0.1, width=150)
        buscar_mes_button = tk.Button(self.cobranza_frame, text="Buscar Mes", font=font, command=self.buscar_por_mes)
        buscar_mes_button.place(relx=0.75, rely=0.1)

        # Botón para limpiar el Treeview
        limpiar_button = tk.Button(self.cobranza_frame, text="Limpiar", font=font, command=self.limpiar_treeview)
        limpiar_button.place(relx=0.85, rely=0.1)

        # Crear el Treeview para mostrar los pagos
        columns = ('cedula_estudiante', 'nombre_alumno', 'curso', 'mes', 'monto', 'tipo_pago')
        self.tree = ttk.Treeview(self.cobranza_frame, columns=columns, show='headings')

        # Definir encabezados
        self.tree.heading('cedula_estudiante', text='Cédula Alumno')
        self.tree.heading('nombre_alumno', text='Nombre Alumno')
        self.tree.heading('curso', text='Curso')
        self.tree.heading('mes', text='Mes')
        self.tree.heading('monto', text='Monto')
        self.tree.heading('tipo_pago', text='Tipo de Pago')

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

    def buscar_por_cedula(self):
        """
        Método para buscar pagos realizados por un alumno utilizando su cédula.
        """
        cedula = self.cedula_entry.get().strip()
        if not cedula:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula.")
            return

        try:
            cursor = mydb.cursor()
            query = """
            SELECT cedula_estudiante, nombre_alumno, curso, mes, monto, tipo_pago
            FROM registro_pagos
            WHERE cedula_estudiante = %s
            """
            cursor.execute(query, (cedula,))
            result = cursor.fetchall()
            cursor.close()

            self.actualizar_treeview(result)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def buscar_por_representante(self):
        """
        Método para buscar alumnos asociados a un representante utilizando su cédula.
        """
        cedula_representante = self.cedula_rep_entry.get().strip()
        if not cedula_representante:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una cédula de representante.")
            return

        try:
            cursor = mydb.cursor()
            query = """
            SELECT cedula, nombre
            FROM alumno
            WHERE cedula_representante = %s
            """
            cursor.execute(query, (cedula_representante,))
            result = cursor.fetchall()
            cursor.close()

            if result:
                alumnos = [f"{alumno[0]} - {alumno[1]}" for alumno in result]
                messagebox.showinfo("Alumnos Asociados", "\n".join(alumnos))
            else:
                messagebox.showinfo("Sin Resultados", "No se encontraron alumnos asociados a este representante.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def buscar_por_curso(self):
        """
        Método para ver los pagos realizados por curso.
        """
        curso = self.curso_combobox.get().strip()
        if curso == "Seleccione un curso" or not curso:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un curso.")
            return

        try:
            cursor = mydb.cursor()
            query = """
            SELECT cedula_estudiante, nombre_alumno, curso, mes, monto, tipo_pago
            FROM registro_pagos
            WHERE curso = %s
            """
            cursor.execute(query, (curso,))
            result = cursor.fetchall()
            cursor.close()

            self.actualizar_treeview(result)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def buscar_por_mes(self):
        """
        Método para mostrar pagos por mes, verificando quiénes han pagado y quiénes no.
        """
        mes = self.mes_combobox.get().strip()
        if not mes:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un mes.")
            return

        try:
            cursor = mydb.cursor()
            query = """
            SELECT cedula_estudiante, nombre_alumno, curso, mes, monto, tipo_pago
            FROM registro_pagos
            WHERE mes = %s
            """
            cursor.execute(query, (mes,))
            result = cursor.fetchall()
            cursor.close()

            self.actualizar_treeview(result)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")

    def actualizar_treeview(self, data):
        """
        Método para actualizar el Treeview con los datos obtenidos y resaltar a los morosos.
        """
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
        """
        Método para limpiar todos los registros del Treeview.
        """
        for record in self.tree.get_children():
            self.tree.delete(record)

    def close_tab(self):
        self.notebook.forget(self.cobranza_frame)
        self.notebook.destroy()
