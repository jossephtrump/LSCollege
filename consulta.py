from tkinter import *
import tkinter as tkinter
from customtkinter import *
import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
import MySQLdb as mysql
from datetime import *
import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.platypus import Paragraph , Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
from reportlab.platypus import Table, TableStyle

from tkinter import ttk
mydb = mysql.connect(host='localhost',user='root',passwd='',db='colegio')
cur = mydb.cursor()

#----------------------------------------------+++++++++ MODULO CONSULTA ALUMNOS ++++++++++++------------------------------------------------------------#
def consulta_alumnos():  
    def vaciar_tabla():
        filas = tvEstudiante.get_children()
        for fila in filas:
            tvEstudiante.delete(fila)

    def llenar_tabla():
        vaciar_tabla()
        mydb = mysql.connect(host='localhost', user='root', passwd='', db='colegio')
        cur = mydb.cursor()

        sql="select cedula,cedula_representante,nombre,direccion,telefono,curso,matricula from alumno where cedula = '{0}'".format(cedula_entry.get())
        cur.execute(sql)
        filas = cur.fetchall()
        while True:
            for fila in filas:
                cedula= fila[0]
                tvEstudiante.insert("", END,cedula , text=cedula, values= fila )
                break
            else:
                messagebox.showinfo("AVISO", "No registrado ", parent=mwindow)
                break

#creacion variables
    global mwindow, cedula_entry
    cedula_entry = StringVar()
#create ventana
    mwindow = ctk.CTk()
    mwindow.geometry("1000x500")
    mwindow.title("Consultas")
    #mwindow.resizable(False, False)
    mwindow.config(background="#213141")
    main_title = ctk.CTkLabel(mwindow, text="INFORMACION | ALUMNOS", font=("Cambria", 20),
                              fg_color="gray21", width=500, height=3)
    main_title.pack(fill="x")
#styling tabla
    tvEstudiante = ttk.Treeview(mwindow)
    style = ttk.Style(tvEstudiante)
    style.configure("Treeview", background="#dcdcdc", foreground="black", font=("Cambria", 14),
                    borderwidth=2, highlightthickness=1)
    style.configure("Treeview.Heading", background="black", foreground="black", font=("Cambria", 14, "bold"))
    tvEstudiante.pack(fill="x", expand=True, side="top", anchor="n")
#styling columnas 
    a = 110
    tvEstudiante["columns"]=("cedula","representante","nombre","direccion","telefono","curso","matricula")
    tvEstudiante.column("#0", width=0, stretch=NO)
    tvEstudiante.column("cedula", width=a, anchor=CENTER)
    tvEstudiante.column("representante", width=a, anchor=CENTER)
    tvEstudiante.column("nombre", width=a, anchor=CENTER)
    tvEstudiante.column("direccion", width=a, anchor=CENTER)
    tvEstudiante.column("telefono", width=a, anchor=CENTER)
    tvEstudiante.column("matricula", width=a, anchor=CENTER)
    tvEstudiante.column("curso", width=a, anchor=CENTER)
#styling encabezados
    tvEstudiante.heading("#0", text="")
    tvEstudiante.heading("cedula",text="Cedula",anchor=CENTER)
    tvEstudiante.heading("representante",text="Representante",anchor=CENTER)
    tvEstudiante.heading("nombre",text="Nombre",anchor=CENTER)
    tvEstudiante.heading("direccion",text="Direccion",anchor=CENTER)
    tvEstudiante.heading("telefono",text="Telefono",anchor=CENTER)
    tvEstudiante.heading("matricula",text="Matricula",anchor=CENTER)
    tvEstudiante.heading("curso",text="Curso",anchor=CENTER)
#create label & button
    cedula_label = Label(mwindow, text="Ingrese Cedula", font=("Arial", 16),
                        width=20, height=1, fg="white", anchor="center",
                        justify="center", bg="#213141")
    cedula_label.pack(anchor=CENTER, pady=22)

    cedula_entry = Entry(mwindow, textvariable=cedula_entry, font=("Arial", 16),justify='center',
                          width=20)
    cedula_entry.pack(anchor=CENTER, pady=21)

    submit_btn = CTkButton(mwindow, text="BUSCAR", font=("Arial", 18),
                           width=30, height=20, anchor="center", 
                         command=llenar_tabla) 
    submit_btn.pack(anchor=CENTER, pady=20)  
    mwindow.mainloop()

#------------------------------------+++++++++++++++++++++++ VENTANA PARA HACER CONSULTA SECCION ++++++++++++++++++++++++-----------------------------------------#
def consulta_seccion():
    def vaciar_tabla():
        filas = tvEstudiante.get_children()
        for fila in filas:
            tvEstudiante.delete(fila)

    def llenar_tabla():
        vaciar_tabla()
        mydb = mysql.connect(host='localhost', user='root', passwd='', db='colegio')
        cur = mydb.cursor()
        sql="""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY a.nombre) AS numero,
            r.cedula AS cedula_representante,
            r.nombre AS nombre_representante,
            a.nombre AS nombre_alumno,
            r.direccion AS direccion_representante,
            r.telefono AS telefono_representante,
            a.matricula AS matricula_alumno
        FROM 
            alumno a
        INNER JOIN 
            representante r ON a.cedula_representante = r.cedula
        WHERE 
            a.curso = '{0}'
        ORDER BY 
            a.nombre
        """.format(egrado_combobox.get())
        cur.execute(sql)
        filas = cur.fetchall()
        for fila in filas:
            cedula = fila[0]
            tvEstudiante.insert("", END,  text=cedula, values=fila)

#creacion variables
    global mwindow  
    global cedula_entry
    global egrado_entry
    global egrado_combobox
    cedula_entry = StringVar()
    egrado_entry= StringVar()
#create ventana
    mwindow = ctk.CTk()
    mwindow.geometry("1280x720")
    mwindow.title("Consultas")
    mwindow.config(background="#213141")
    main_title = ctk.CTkLabel(mwindow, text="INFORMACION | SECCION", font=("Arial", 20),
                              fg_color="gray21", width=500, height=3)
    main_title.pack(fill="x")
#styling tabla
    tvEstudiante = ttk.Treeview(mwindow)
    style = ttk.Style(tvEstudiante)
    style.configure("Treeview", background="#dcdcdc", foreground="black", font=("Arial", 14),
                    borderwidth=2, highlightthickness=1)
    style.configure("Treeview.Heading", background="black", foreground="black", font=("Arial", 14, "bold"))
    tvEstudiante.pack(fill="both", expand=True, side="top", anchor="n")

#styling columnas 
    a = 110
    tvEstudiante["columns"]=("cedula","representante","nombre","direccion","telefono","matricula")
    tvEstudiante.column("#0", width=0, stretch=NO)
    tvEstudiante.column("cedula", width=a, anchor=CENTER)
    tvEstudiante.column("representante", width=a, anchor=CENTER)
    tvEstudiante.column("nombre", width=a, anchor=CENTER)
    tvEstudiante.column("direccion", width=a, anchor=CENTER)
    tvEstudiante.column("telefono", width=a, anchor=CENTER)
    tvEstudiante.column("matricula", width=a, anchor=CENTER)
    
#styling encabezados
    tvEstudiante.heading("#0", text="")
    tvEstudiante.heading("cedula",text="N°",anchor=CENTER)
    tvEstudiante.heading("representante",text="CI Representante",anchor=CENTER)
    tvEstudiante.heading("nombre",text="REPRESENTANTE",anchor=CENTER)
    tvEstudiante.heading("direccion",text="Alumno",anchor=CENTER)
    tvEstudiante.heading("telefono",text="Direccion",anchor=CENTER)
    tvEstudiante.heading("matricula",text="Telefono",anchor=CENTER)
    
#create label & button
    grado_values = ('S3', 'S4', 'S5', '1GU', '2GU', '3GU', '4GU', '5GU', '6GU',
                   '1AA', '1AB', '2AA', '2AB', '3AA', '3AB', '4AA', '4AB', '5AA', '5AB')

    egrado_combobox = ttk.Combobox(mwindow,textvariable=egrado_entry ,values=grado_values,
                                  font=("Arial", 16), justify='center',width=12)
    egrado_combobox.current(0)
    egrado_combobox.pack(anchor=CENTER, padx=5, pady=10)

    submit_buscar = CTkButton(mwindow, text="BUSCAR", font=("Cambria", 18),
                           width=10, height=10, anchor="center", 
                         command=llenar_tabla) 
    submit_buscar.pack(anchor=CENTER, padx=5, pady=10)

    submit_print = CTkButton(mwindow, text="PRINT", font=("Cambria", 18), fg_color="IndianRed3",
                           width=10, height=10, anchor="center", 
                         command=impresion_diaria) 
    submit_print.place(relx=0.90, rely=0.95)
   
    mwindow.mainloop()

def impresion_diaria():
    
    mydb = mysql.connect(host='localhost',user='root',passwd='',db='colegio')
    cur = mydb.cursor()
     # Suponiendo que 'fecha' es un widget de entrada de texto
    #fecha_formateada = datetime.strptime(fecha_seleccionada, '%d/%m/%y').strftime('%Y-%m-%d')

    # Crear carpeta de cierre diario si no existe
    if not os.path.exists("cierre_diario"):
        os.makedirs("cierre_diario")

    archivo = os.path.join('cierre_diario', 'resultados_{0}.pdf'.format(egrado_combobox.get()))

    if os.path.exists(archivo):
        # Modificar el nombre para incluir "(1)"
        contador = 1
        # Verificar si el archivo ya existe y ajustar el nombre
        print(f"El archivo ya existe. Nuevo nombre: {archivo}")
        while os.path.exists(archivo):
            archivo = os.path.join('cierre_diario', f"resultados_{egrado_combobox.get()}({contador}).pdf")
            contador += 1

    # Consulta SQL segura
    consulta = """
    SELECT 
    ROW_NUMBER() OVER (ORDER BY a.nombre) AS numero,
    r.cedula AS cedula_representante,
    a.cedula AS cedula_alumno,
    a.nombre AS nombre_alumno,
    r.nombre AS nombre_representante
FROM 
    alumno a
JOIN 
    representante r ON a.cedula_representante = r.cedula
WHERE 
    a.curso = '{0}'
ORDER BY 
    a.nombre
""".format(egrado_combobox.get())


    cur.execute(consulta)
    resultados = cur.fetchall()

    # Crear el documento PDF
    doc = SimpleDocTemplate(archivo, pagesize=letter)

    # Lista para almacenar los elementos de cada página
    elementos = []

    # Agregar la fecha formateada encima de la tabla
    estilo_fecha = getSampleStyleSheet()["Normal"]
    fecha_paragraph = Paragraph(f"Fecha: {egrado_combobox.get()}", estilo_fecha)
    elementos.append(fecha_paragraph)

    # Encabezados de la tabla
    encabezados = [ "N","cedula representante", "cedula alumno", "Nombre Representante", "Nombre Alumno "]
    data = [encabezados]

    # Contenido de la tabla
    for resultado in resultados:
        data.append(resultado)

    # Crear la tabla
    t = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    t.setStyle(style)

    # Agregar la tabla al documento
    elementos.append(t)

    # Construir el PDF
    doc.build(elementos)

    # Abrir el PDF
    os.startfile(archivo, "print")

#--------------------------+++++++++++++++++++++ MODULO REPRESENTANTES +++++++++++++++++++-----------------------------------------------------#
def consulta_representante():
    def vaciar_tabla():
        filas = tvEstudiante.get_children()
        for fila in filas:
            tvEstudiante.delete(fila)

    def llenar_tabla():
        vaciar_tabla()
        mydb = mysql.connect(host='localhost', user='root', passwd='', db='colegio')
        cur = mydb.cursor()
        sql="select * from representante where cedula= '{0}'".format(cedula_entry.get())
        cur.execute(sql)
        filas = cur.fetchall()
        if filas:
            fila = filas[0]
            cedula= fila[0]
            tvEstudiante.insert("", END,cedula , text=cedula, values= fila )
            llenar_tabla2()
        else: 
            messagebox.showinfo("AVISO", "No Registrado ", parent=mwindow)
            
#cREACION SUBTABLA DE ALUMNOS
    def llenar_tabla2():
        mydb = mysql.connect(host='localhost', user='root', passwd='', db='colegio')
        cur = mydb.cursor()
        tvEstudiante.insert("", 'end', values=("Cedula","Nombre","Telefono","Curso","Matricula"), tags=("fila_color"))
        sql="select cedula,nombre,telefono,curso,matricula from alumno where cedula_representante = '{0}'".format(cedula_entry.get())
        cur.execute(sql)
        filas = cur.fetchall()
        
        for fila in filas:
            cedula= fila[0]
            tvEstudiante.insert("", END,cedula , text=cedula, values= fila  )

#errores en la busqueda del representante
    def mostar_error():
       value= cedula_entry.get()
       sql100="select * from representante where cedula = '{0}'".format(value)
       nonull= cur.execute(sql100)
       if value == "":
           messagebox.showinfo("AVISO", "Campo vacio", parent=mwindow)
           return True
       elif nonull == 0:
           messagebox.showinfo("AVISO", "Representante No Registrado", parent=mwindow)
           return True
            
#creating variables
    global cedula_entry, mwindow
    cedula_entry = StringVar()

#create window
    mwindow = ctk.CTk()
    mwindow.geometry("1200x600")
    mwindow.title("Consultas")
    #mwindow.resizable(False, False)
    mwindow.config(background="#213141")
    main_title = ctk.CTkLabel(mwindow,text="INFORMACION | REPRESENTANTES", font=("Arial", 20),
                              fg_color="gray21", width=500, height=3)
    main_title.pack(fill="x")
#styling tabla
    tvEstudiante = ttk.Treeview(mwindow)
    style = ttk.Style(tvEstudiante)

    tvEstudiante.tag_configure("fila_color", background="#213141")
    style.configure("Treeview", background="#dcdcdc", foreground="black", font=("Arial", 14),
                    borderwidth=2, highlightthickness=1)
    style.configure("Treeview.Heading", background="black", foreground="black", font=("Arial", 14, "bold"))
    tvEstudiante.pack(fill="x", expand=True, side="top", anchor="n")
#styling columnas
    a = 100
    tvEstudiante["columns"]=("cedula","nombre","direccion","telefono","numero_alumnos","correo")
    tvEstudiante.column("#0", width=0, stretch=NO) 
    tvEstudiante.column("cedula", width=90, anchor=CENTER)
    tvEstudiante.column("nombre", width=a, anchor=CENTER)
    tvEstudiante.column("direccion", width=a, anchor=CENTER)
    tvEstudiante.column("telefono", width=90, anchor=CENTER)
    tvEstudiante.column("numero_alumnos", width=15, anchor=CENTER)
    tvEstudiante.column("correo", width=130, anchor=CENTER)
#styling encabezado 
    tvEstudiante.heading("#0", text="")
    tvEstudiante.heading("cedula",text="Cedula",anchor=CENTER)
    tvEstudiante.heading("nombre",text="Nombre",anchor=CENTER)
    tvEstudiante.heading("direccion",text="Direccion",anchor=CENTER)
    tvEstudiante.heading("telefono",text="Telefono",anchor=CENTER)
    tvEstudiante.heading("numero_alumnos",text="Asociados",anchor=CENTER)
    tvEstudiante.heading("correo",text="Correo",anchor=CENTER)
#creating entry & buttons
    cedula_label = Label(mwindow, text="Ingrese Cedula", font=("Arial", 16),
                        width=20, height=1, fg="white", anchor="center",
                        justify="center", bg="#213141")
    cedula_label.pack(anchor=CENTER, pady=22)
    cedula_entry = Entry(mwindow, textvariable=cedula_entry, font=("Arial", 16),justify='center',
                          width=20)
    cedula_entry.pack(anchor=CENTER, pady=21)
    submit_btn = CTkButton(mwindow, text="BUSCAR", font=("Arial", 18),
                           width=30, height=20, anchor="center", 
                         command=lambda:[llenar_tabla() if not mostar_error() else NONE]) 
    submit_btn.pack(anchor=CENTER, pady=20)


    # Crear el botón de imprimir
    imprimir_btn = CTkButton(mwindow, text="PRINT", font=("Arial", 18),
                            width=20, height=20, anchor="center", fg_color="IndianRed3",
                            command=impresion_representante)
    imprimir_btn.place(relx=0.90, rely=0.95)

    mwindow.mainloop()

def impresion_representante():
    mydb = mysql.connect(host='localhost', user='root', passwd='', db='colegio')
    cur = mydb.cursor()
    fecha_hoy = datetime.today().date()
    fecha_formateada = fecha_hoy.strftime('%Y-%m-%d')
   
    # Crear carpeta de cierre diario si no existe
    if not os.path.exists("informacion-representante"):
        os.makedirs("informacion-representante")

    cedula_representante = cedula_entry.get()
    archivo = os.path.join('informacion-representante', f'representante_{cedula_representante}.pdf')

    if os.path.exists(archivo):
        contador = 1
        while os.path.exists(archivo):
            archivo = os.path.join('informacion-representante', f'representante_{cedula_representante}_({contador}).pdf')
            contador += 1

    # Consulta SQL segura para obtener la información del representante
    consulta_representante = """
    SELECT 
        cedula,
        nombre,
        direccion,
        telefono,
        correo
    FROM 
        representante
    WHERE 
        cedula = %s
    """
    cur.execute(consulta_representante, (cedula_representante,))
    representante = cur.fetchone()

    elementos = []

    # Crear la tabla de representante
    tabla_representante = Table([["Cédula", "Nombre", "Dirección", "Teléfono", "Correo"]] + [list(representante)])

    # Estilo de la tabla de representante
    estilo_representante = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    tabla_representante.setStyle(estilo_representante)

    # Agregar la tabla de representante al documento
    elementos.append(tabla_representante)

    # Añadir un espacio después de la tabla de representante
    elementos.append(Spacer(1, 20))

    # Consulta SQL segura para obtener la información de los alumnos asociados al representante
    consulta_alumnos = """
    SELECT 
        cedula,
        nombre,
        matricula
    FROM 
        alumno
    WHERE 
        cedula_representante = %s
    """
    cur.execute(consulta_alumnos, (cedula_representante,))
    alumnos = cur.fetchall()

    # Convertir tuplas de alumnos en listas y crear la tabla de alumnos
    alumnos_data = [["Cédula", "Nombre", "Matricula"]] + [list(alumno) for alumno in alumnos]
    tabla_alumnos = Table(alumnos_data)

    # Estilo de la tabla de alumnos
    estilo_alumnos = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    tabla_alumnos.setStyle(estilo_alumnos)

    # Agregar la tabla de alumnos al documento
    elementos.append(tabla_alumnos)

    # Construir el PDF
    doc = SimpleDocTemplate(archivo, pagesize=letter)
    doc.build(elementos)

    # Abrir el PDF
    os.startfile(archivo, "print")
