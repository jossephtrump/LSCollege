import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
import MySQLdb as mysql

# Configuración de la conexión a la base de datos
def connect_db():
    return mysql.connect(host='localhost', user='root', passwd='', db='colegio')

# Función para vaciar la tabla de datos en la interfaz
def vaciar_tabla(tvEstudiante):
    filas = tvEstudiante.get_children()
    for fila in filas:
        tvEstudiante.delete(fila)

# Función para mostrar un mensaje de error si la entrada es inválida
def mostrar_error(cedula_entry):
    valor1 = cedula_entry.get()
    cur.execute("SELECT * FROM representante WHERE cedula = %s", (valor1,))
    if valor1 == "":
        messagebox.showerror("Error", "Por favor, ingrese una cedula.")
        return True
    if cur.rowcount == 0:
        messagebox.showerror("Error", "Cedula no encontrada.")
        return True
    return False

# Función para crear la tabla en la interfaz
def crear_tabla(mwindow, columnas, encabezados):
    tvEstudiante = ttk.Treeview(mwindow, columns=columnas, show='headings')
    style = ttk.Style(tvEstudiante)
    style.configure("Treeview", background="#dcdcdc", foreground="black", font=("Arial", 12),
                    borderwidth=2, highlightthickness=1)
    style.configure("Treeview.Heading", background="black", foreground="black", font=("Arial", 14, "bold"))
    for col, heading in zip(columnas, encabezados):
        tvEstudiante.heading(col, text=heading, anchor=tk.CENTER)
        tvEstudiante.column(col, anchor=tk.CENTER)
    tvEstudiante.pack(fill="both", expand=True, side="top", anchor="n")
    return tvEstudiante

# Función para llenar la tabla con datos de la base de datos
def llenar_tabla(cur, sql, tvEstudiante):
    vaciar_tabla(tvEstudiante)
    cur.execute(sql)
    filas = cur.fetchall()
    for fila in filas:
        tvEstudiante.insert("", tk.END, values=fila)

# Función para imprimir datos en un archivo PDF
def imprimir_pdf(nombre_carpeta, nombre_archivo, encabezados, datos, subtitulo):
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta)
    archivo = os.path.join(nombre_carpeta, nombre_archivo)
    if os.path.exists(archivo):
        contador = 1
        while os.path.exists(archivo):
            archivo = os.path.join(nombre_carpeta, f"{nombre_archivo}({contador}).pdf")
            contador += 1
    doc = SimpleDocTemplate(archivo, pagesize=letter)
    elementos = [Paragraph(subtitulo, getSampleStyleSheet()["Normal"])]
    data = [encabezados] + datos
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elementos.append(t)
    doc.build(elementos)
    messagebox.showinfo("Guardado exitoso", "El archivo PDF se ha guardado exitosamente.")
    os.startfile(archivo, "print")

# Función para la cobranza por alumno
def cobranza_alumno():
    def buscar_alumno():
        if not mostrar_error(cedula_entry):
            sql = """
            SELECT m.numero_factura, rp.fecha, rp.hora, r.nombre, a.nombre, m.mes, m.cantidad
            FROM registro_pagos rp
            INNER JOIN alumno a ON rp.cedula_estudiante = a.cedula
            INNER JOIN representante r ON a.cedula_representante = r.cedula
            INNER JOIN mensualidades m ON rp.id = m.numero_factura
            WHERE r.cedula = %s
            """
            llenar_tabla(cur, sql, tvEstudiante)

    mydb = connect_db()
    cur = mydb.cursor()
    mwindow = tk.Tk()
    mwindow.geometry("1280x720")
    mwindow.title("Cobranza")
    mwindow.config(background="#213141")

    tk.Label(mwindow, text="PAGOS REALIZADOS", font=("Cambria", 20),
             fg="white", bg="#213141").pack(fill="x")

    columnas = ("numero_factura", "fecha", "hora", "nombre_representante", "nombre_alumno", "mes_pagado", "cantidad_pagada")
    encabezados = ("Factura", "Fecha", "Hora", "Representante", "Alumno", "Mes", "Monto")
    tvEstudiante = crear_tabla(mwindow, columnas, encabezados)

    tk.Label(mwindow, text="CI REPRESENTANTE", font=("Cambria", 16),
             fg="white", bg="#213141").pack(anchor=tk.CENTER, pady=20)
    cedula_entry = tk.Entry(mwindow, font=("Cambria", 16), justify='center')
    cedula_entry.pack(anchor=tk.CENTER, pady=10)

    tk.Button(mwindow, text="BUSCAR", font=("Cambria", 18),
              command=buscar_alumno).pack(anchor=tk.CENTER)
    tk.Button(mwindow, text="IMPRIMIR", font=("Cambria", 18), fg="IndianRed3",
              command=lambda: imprimir_pdf("cobranza_alumno", f"cobranza_{cedula_entry.get()}.pdf", encabezados, tvEstudiante, f"REPRESENTANTE: {cedula_entry.get()}")).pack(anchor=tk.CENTER)

    mwindow.mainloop()

# Función para la cobranza por curso
def cobranza_curso():
    def buscar_curso():
        sql = """
        SELECT rp.id, rp.fecha, rp.hora, m.cantidad, m.mes, a.nombre, r.nombre
        FROM registro_pagos rp
        INNER JOIN alumno a ON rp.cedula_estudiante = a.cedula
        INNER JOIN representante r ON a.cedula_representante = r.cedula
        INNER JOIN mensualidades m ON rp.id = m.numero_factura
        WHERE a.curso = %s
        """
        llenar_tabla(cur, sql, tvEstudiante)

    mydb = connect_db()
    cur = mydb.cursor()
    mwindow = tk.Tk()
    mwindow.geometry("1280x720")
    mwindow.title("COBRANZA")
    mwindow.config(background="#213141")

    tk.Label(mwindow, text="PAGOS REALIZADOS | SECCION", font=("Cambria", 20),
             fg="white", bg="#213141").pack(fill="x")

    columnas = ("id", "fecha", "hora", "cantidad", "mes", "nombre_alumno", "nombre_representante")
    encabezados = ("Factura", "Fecha", "Hora", "Monto", "Mes", "Alumno", "Representante")
    tvEstudiante = crear_tabla(mwindow, columnas, encabezados)

    tk.Label(mwindow, text="Sección", font=("Cambria", 16),
             fg="white", bg="#213141").pack(anchor=tk.CENTER, pady=20)
    curso_entry = ttk.Combobox(mwindow, font=("Cambria", 16), justify='center')
    curso_entry.pack(anchor=tk.CENTER, pady=10)
    curso_entry['values'] = ('S3', 'S4', 'S5', '1GU', '2GU', '3GU', '4GU', '5GU', '6GU',
                             '1AA', '1AB', '2AA', '2AB', '3AA', '3AB', '4AA', '4AB', '5AA', '5AB')

    tk.Button(mwindow, text="BUSCAR", font=("Cambria", 18),
              command=buscar_curso).pack(anchor=tk.CENTER)
    tk.Button(mwindow, text="IMPRIMIR", font=("Cambria", 18), fg="IndianRed3",
              command=lambda: imprimir_pdf("cobranza_curso", f"cobranza_{curso_entry.get()}.pdf", encabezados, tvEstudiante, f"SECCION: {curso_entry.get()}")).pack(anchor=tk.CENTER)

    mwindow.mainloop()

# Función para el cierre diario de pagos
def cierre_diario():
    def buscar_cierre():
        fecha_str = fecha.get_date().strftime("%Y-%m-%d")
        sql = f"""
        SELECT rp.id, rp.fecha, rp.hora, m.cantidad, m.mes, a.nombre
        FROM registro_pagos rp
        JOIN mensualidades m ON rp.id = m.numero_factura
        JOIN alumno a ON m.cedula_alumno = a.cedula
        WHERE rp.fecha = '{fecha_str}'
        """
        llenar_tabla(cur, sql, tvEstudiante)

    mydb = connect_db()
    cur = mydb.cursor()
    mwindow = tk.Tk()
    mwindow.geometry("1280x720")
    mwindow.title("PAGOS")
    mwindow.config(background="#213141")

    tk.Label(mwindow, text="CIERRE | DIARIO", font=("Cambria", 20),
             fg="white", bg="#213141").pack(fill="x")

    columnas = ("id", "fecha", "hora", "cantidad", "mes", "nombre")
    encabezados = ("Factura", "Fecha", "Hora", "Monto", "Mes", "Alumno")
    tvEstudiante = crear_tabla(mwindow, columnas, encabezados)

    tk.Label(mwindow, text="Fecha", font=("Cambria", 16),
             fg="white", bg="#213141").pack(anchor=tk.CENTER, pady=20)
    fecha = DateEntry(mwindow, width=25, height=20, background='darkblue',
                      foreground='white', borderwidth=2)
    fecha.pack(pady=20, anchor=tk.CENTER)

    tk.Button(mwindow, text="BUSCAR", font=("Cambria", 18),
              command=buscar_cierre).pack(anchor=tk.CENTER)
    tk.Button(mwindow, text="IMPRIMIR", font=("Cambria", 18), fg="IndianRed3",
              command=lambda: imprimir_pdf("cierre_diario", f"cierre_{fecha.get_date().strftime('%Y-%m-%d')}.pdf", encabezados, tvEstudiante, f"Fecha: {fecha.get_date().strftime('%Y-%m-%d')}")).pack(anchor=tk.CENTER)

    mwindow.mainloop()

# Función para la cobranza total
def cobranza_total():
    def buscar_total():
        sql = """
        SELECT m.numero_factura, rp.fecha, rp.hora, m.cantidad, m.mes, a.nombre, a.curso, r.nombre
        FROM mensualidades m
        INNER JOIN registro_pagos rp ON m.numero_factura = rp.id
        INNER JOIN alumno a ON m.cedula_alumno = a.cedula
        INNER JOIN representante r ON a.cedula_representante = r.cedula
        """
        llenar_tabla(cur, sql, tvEstudiante)

    mydb = connect_db()
    cur = mydb.cursor()
    mwindow = tk.Tk()
    mwindow.geometry("1280x720")
    mwindow.title("COBRANZA")
    mwindow.config(background="#213141")

    tk.Label(mwindow, text="COBRO | TOTAL", font=("Cambria", 20, "bold"),
             fg="white", bg="#213141").pack(fill="x")

    columnas = ("id", "fecha", "hora", "cantidad", "mes", "nombre_alumno", "curso", "nombre_representante")
    encabezados = ("Factura", "Fecha", "Hora", "Monto", "Mes", "Alumno", "Sección", "Representante")
    tvEstudiante = crear_tabla(mwindow, columnas, encabezados)

    tk.Button(mwindow, text="BUSCAR", font=("Cambria", 18),
              command=buscar_total).pack(anchor=tk.CENTER, pady=20)
    tk.Button(mwindow, text="IMPRIMIR", font=("Cambria", 18), fg="IndianRed3",
              command=lambda: imprimir_pdf("cobranza_total", f"cobranza_total_{datetime.now().strftime('%Y-%m-%d')}.pdf", encabezados, tvEstudiante, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")).pack(anchor=tk.CENTER, pady=20)

    mwindow.mainloop()

# Función para mostrar deudores por curso
def consulta_curso():
    def buscar_deudores_curso():
        sql = """
        SELECT a.nombre, a.curso, r.nombre
        FROM alumno a
        LEFT JOIN representante r ON a.cedula_representante = r.cedula
        LEFT JOIN mensualidades m ON a.cedula = m.cedula_alumno AND m.mes = %s
        WHERE m.numero_factura IS NULL AND a.curso = %s
        """
        llenar_tabla(cur, sql, tvEstudiante)

    mydb = connect_db()
    cur = mydb.cursor()
    mwindow = tk.Tk()
    mwindow.geometry("1280x720")
    mwindow.title("MORA")
    mwindow.config(background="#213141")

    tk.Label(mwindow, text="DEUDORES | SECCION", font=("Arial", 20, "bold"),
             fg="white", bg="#213141").pack(fill="x")

    columnas = ("nombre_alumno", "curso", "nombre_representante")
    encabezados = ("Alumno", "Sección", "Representante")
    tvEstudiante = crear_tabla(mwindow, columnas, encabezados)

    meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
             'Octubre', 'Noviembre', 'Diciembre')
    meses_combobox = ttk.Combobox(mwindow, font=("Arial", 16), justify='center')
    meses_combobox['values'] = meses
    meses_combobox.pack(anchor=tk.CENTER, padx=10, pady=10)

    grado_values = ('S3', 'S4', 'S5', '1GU', '2GU', '3GU', '4GU', '5GU', '6GU',
                    '1AA', '1AB', '2AA', '2AB', '3AA', '3AB', '4AA', '4AB', '5AA', '5AB')
    egrado_combobox = ttk.Combobox(mwindow, font=("Arial", 16), justify='center')
    egrado_combobox['values'] = grado_values
    egrado_combobox.pack(anchor=tk.CENTER, padx=5, pady=10)

    tk.Button(mwindow, text="BUSCAR", font=("Arial", 18, "bold"),
              command=buscar_deudores_curso).pack(anchor=tk.CENTER, pady=15)
    tk.Button(mwindow, text="PRINT", font=("Arial", 16), fg="IndianRed3",
              command=lambda: imprimir_pdf("deudores_seccion", f"deudores_seccion_{egrado_combobox.get()}_{meses_combobox.get()}.pdf", encabezados, tvEstudiante, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}, mes a deber: {meses_combobox.get()}")).pack(anchor=tk.CENTER)

    mwindow.mainloop()

# Función para mostrar todos los deudores
def mora_total():
    def buscar_deudores_total():
        sql = """
        SELECT a.nombre, a.curso, r.nombre
        FROM alumno a
        LEFT JOIN representante r ON a.cedula_representante = r.cedula
        LEFT JOIN mensualidades m ON a.cedula = m.cedula_alumno AND m.mes = %s
        WHERE m.numero_factura IS NULL
        """
        llenar_tabla(cur, sql, tvEstudiante)

    mydb = connect_db()
    cur = mydb.cursor()
    mwindow = tk.Tk()
    mwindow.geometry("1280x720")
    mwindow.title("MORA")
    mwindow.config(background="#213141")

    tk.Label(mwindow, text="DEUDORES | TOTAL", font=("Arial", 20, "bold"),
             fg="white", bg="#213141").pack(fill="x")

    columnas = ("nombre_alumno", "curso", "nombre_representante")
    encabezados = ("Alumno", "Sección", "Representante")
    tvEstudiante = crear_tabla(mwindow, columnas, encabezados)

    meses = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
             'Octubre', 'Noviembre', 'Diciembre')
    meses_combobox = ttk.Combobox(mwindow, font=("Arial", 16), justify='center')
    meses_combobox['values'] = meses
    meses_combobox.pack(anchor=tk.CENTER, padx=10, pady=10)

    tk.Button(mwindow, text="BUSCAR", font=("Arial", 18, "bold"),
              command=buscar_deudores_total).pack(anchor=tk.CENTER, pady=15)
    tk.Button(mwindow, text="PRINT", font=("Arial", 16), fg="IndianRed3",
              command=lambda: imprimir_pdf("deudores_total", f"deudores_total_{meses_combobox.get()}.pdf", encabezados, tvEstudiante, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}, mes a deber: {meses_combobox.get()}")).pack(anchor=tk.CENTER)

    mwindow.mainloop()

# Ejecutar las funciones principales
if __name__ == "__main__":
    main_window = tk.Tk()
    main_window.title("Sistema de Gestión Escolar")
    main_window.geometry("800x600")
    main_window.config(bg="#213141")

    tk.Label(main_window, text="Sistema de Gestión Escolar", font=("Cambria", 24),
             bg="#213141", fg="white").pack(pady=20)

    buttons = [
        ("Cobranza Alumno", cobranza_alumno),
        ("Cobranza Curso", cobranza_curso),
        ("Cierre Diario", cierre_diario),
        ("Cobranza Total", cobranza_total),
        ("Consulta Deudores Curso", consulta_curso),
        ("Consulta Deudores Total", mora_total)
    ]

    for (text, command) in buttons:
        tk.Button(main_window, text=text, font=("Cambria", 16), width=20,
                  command=command).pack(pady=10)

    main_window.mainloop()
