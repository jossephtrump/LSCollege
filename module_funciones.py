import tkinter as tk
from databaseManager import mydb
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
import re
import datetime

name_return = ""
tlf_return = ""
correo_return = ""
cedula_return = ""
usdt_return = ""
cash_return = ""

def cedula_fact(cedula, suscripcion, zelle, usdt, bolivares, efectivo):
    """
    Inserta los datos de la facturación en la base de datos.
    """
    cursor = mydb.cursor()
    # Se corrige agregando el paréntesis de cierre después de CURDATE()
    sql = "INSERT INTO facturacion(cedula, motivoPago, zelle, usdt, bolivares, efectivo, fechaPago) VALUES (%s, %s, %s, %s, %s, %s, CURDATE())"
    try:
        cursor.execute(sql, (cedula, suscripcion, zelle, usdt, bolivares, efectivo))
        mydb.commit()
        print(cursor.rowcount, "datos insertados.")
    except mysql.connector.Error as e:
        print("Hubo un error al insertar los datos:", e)

def error_cedula(cedula):
    """
    Muestra un mensaje de error si la cédula no se encuentra en la base de datos.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT cedula FROM clientes WHERE cedula = %s", (cedula,))
    resultado = cursor.fetchone()
    if resultado is None:
        messagebox.showerror("Error", "No se encontró la cédula.")
        return False
    else:
        print("Éxito", f"Cédula encontrada: {resultado[0]}")
        return True

def consulta_cedula(cedula):
    """
    Consulta si la cédula ingresada existe en la base de datos.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT cedula FROM clientes WHERE cedula = %s", (cedula,))
    resultado = cursor.fetchone()
    if resultado is None:
        return False
    else:
        print("Éxito", f"Cédula encontrada: {resultado[0]}")
        return True

def name_data(cedula):
    """
    Obtiene el nombre de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT nombre FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        print("No se encontró ningún cliente con esa cédula.")
        return ""

def mail_data(cedula):
    """
    Obtiene el correo de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT email FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        print("No se encontró ningún cliente con esa cédula.")
        return ""

def phone_data(cedula):
    """
    Obtiene el teléfono de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT telefono FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        print("No se encontró ningún cliente con esa cédula.")
        return ""

def birth_data(cedula):
    """
    Obtiene la fecha de nacimiento de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT fechaNac FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        fecha_return, = result
    else:
        print("No se encontró ningún cliente con esa cédula.")
        fecha_return = ""
    return fecha_return

def dir_data(cedula):
    """
    Obtiene la dirección de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT direccion FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    # Cierra la conexión con la base de datos
    if result is not None:
        dir_return, = result
    else:
        print("No se encontró ningún cliente con esa cédula.")
        dir_return = ""
    return dir_return

def genero_data(cedula):
    """
    Obtiene el género de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT genero FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        genero_return, = result
    else:
        print("No se encontró ningún cliente con esa cédula.")
        genero_return = ""
    return genero_return

def ig_data(cedula):
    """
    Obtiene el Instagram de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT socialMedia FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        ig_return, = result
    else:
        print("No se encontró ningún cliente con esa cédula.")
        ig_return = ""
    return ig_return

def zelle_select(cedula):
    """
    Obtiene el Zelle de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT zelle FROM facturacion WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        print("No se encontró ningún cliente con esa cédula.")
        return ""

def cash_select(cedula):
    """
    Obtiene el efectivo de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT email FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        cash_result, = result
    else:
        print("No se encontró ningún cliente con esa cédula.")
        cash_result = ""
    return cash_result

def usdt_select(cedula):
    """
    Obtiene el USDT de un cliente a partir de su cédula.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT email FROM clientes WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    if result is not None:
        usdt_result, = result
    else:
        print("No se encontró ningún cliente con esa cédula.")
        usdt_result = ""
    return usdt_result

def print_window2():
    """
    Crea una ventana para imprimir la factura.
    """
    font = ('noto sans', 8, 'bold')
    print_window = tk.Toplevel()
    print_window.title("Facturar")
    print_window.configure(bg='#D9D9D9')
    print_window.overrideredirect(True) # Quita la barra de título
    print_window.attributes('-topmost', True) # Mantiene la ventana al frente
    # Establece el tamaño de la ventana
    window_width = 560
    window_height = 274
    print_window.geometry(f'{window_width}x{window_height}')
    # Obtiene el tamaño de la pantalla
    screen_width = print_window.winfo_screenwidth()
    screen_height = print_window.winfo_screenheight()
    # Calcula la posición de la nueva ventana para que esté centrada en la pantalla
    position_top = screen_height//2 - window_height//2
    position_right = screen_width//2 - window_width//2
    # Posiciona la nueva ventana
    print_window.geometry("+{}+{}".format(position_right, position_top))
    # Crea los botones de imprimir y salir
    print_button = tk.Button(print_window, text="Imprimir", bg='#F8EB79',
                             width=17, height=2, bd=0, font=font,
                             command=lambda: print("Imprimir"))
    print_button.place(relx=0.2, rely=0.5)
    # Crea un botón para salir de la ventana
    exit_button = tk.Button(print_window, text="Salir", bg='#F8EB79',
                            width=17, height=2, bd=0, font=font,
                            command=print_window.destroy)
    exit_button.place(relx=0.6, rely=0.5)

def search_button(frame, command,  relx=0.85, rely=0.129):
    """
    Crea un botón con una imagen de búsqueda.
    """
    # Get the directory of the script file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Use os.path.join to create the path to the image
    search_image_path = os.path.join(script_dir, 'search_image.jpg')
    search_image = Image.open(search_image_path)
    search_image = search_image.resize((20, 20), Image.Resampling.LANCZOS)
    button_search = ImageTk.PhotoImage(search_image)
    # Create a button that uses the image (use the "image" parameter)
    call_button = tk.Button(frame, image=button_search, bd=0, command=command)
    call_button.image = button_search  #
    call_button.place(relx=relx, rely=rely)


def close_tab(notebook, tab):
    """
    Cierra una pestaña del notebook.
    """
    notebook.forget(tab)  # Cierra la pestaña
    notebook.place_forget()  # Oculta el notebook

def close_button(frame, notebook, tab):
    """
    Crea un botón para cerrar una pestaña.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(script_dir, 'close.jpg')
    image = Image.open(image_path)
    round_button_image = ImageTk.PhotoImage(image.resize((48, 48), Image.Resampling.LANCZOS))
    close_button = tk.Button(tab, image=round_button_image,
                                        command=lambda: close_tab(notebook, tab),
                                        width=48, height=48, bd=0, highlightthickness=0)
    close_button.place(relx=1.0, rely=0.0, anchor='ne')
    close_button.image = round_button_image
    return close_button

def verificarCedula(cedula):
    """
    Verifica si la cédula ya está registrada en la base de datos.
    """
    cursor = mydb.cursor()
    cursor.execute("SELECT cedula FROM clientes WHERE cedula = %s", (cedula,))
    resultado = cursor.fetchone()
    if resultado:
        print("La cédula ya está registrada.")
        return False
    else:
        print("La cédula no está registrada.")
        return True

def insertClientes(cliente):
    """
    Inserta un nuevo cliente en la base de datos.
    """
    cursor = mydb.cursor()
    sql = (
        "INSERT INTO clientes (cedula, nombre, apellido, genero, fechaNac, direccion, telefono, email, socialMedia, acceso) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    try:
        cursor.execute(sql, (cliente.cedula, cliente.name, cliente.apellido, cliente.genero, cliente.fecha_nacimiento, cliente.direccion, cliente.telefono, cliente.email, cliente.social_media, cliente.acceso))
        mydb.commit()
        print("Cliente insertado con éxito.")
    except mysql.connector.Error as e:
        print("Error al insertar cliente:", e)
    finally:
        cursor.close()
