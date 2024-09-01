import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import mysql.connector

# Conexión a la base de datos
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="colegio"  # Cambia esto al nombre de tu base de datos
)

class FacturacionApp:
    def __init__(self, root):
        self.root = root
        self.alumnos_comboboxes = []   # Lista para almacenar los combobox de alumnos
        self.meses_comboboxes = []     # Lista para almacenar los combobox de meses
        self.tipos_comboboxes = []     # Lista para almacenar los combobox de tipo de pago
        self.monto_entries = []        # Lista para almacenar las entradas de montos
        self.initialize_ui()

    def initialize_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        self.fact_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fact_frame, text="Facturación")
        self.fact_frame.configure(borderwidth=2, relief=tk.SUNKEN)

        self.create_widgets()
        close_button = tk.Button(self.fact_frame, text=" X ", font=('noto sans', 10, 'bold'), 
                                 bg='red2', fg='white', bd=1, command=self.close_tab)
        close_button.place(relx=0.999, rely=0.001, anchor='ne')

    def create_widgets(self):
        a = 26
        w = 150
        r1 = 0.14
        r2 = 0.18
        font = ('noto sans', 10, 'bold')

        # Campo Cédula Representante
        self.ci_label = tk.Label(self.fact_frame, text="CI REPRESENTANTE", font=font, bd=0, bg='#F0F3F4')
        self.ci_label.place(relx=0.35, rely=0.05, anchor='center')
        self.ci_entry = ttk.Entry(self.fact_frame, font=font, style='TEntry')
        self.ci_entry.insert(0, 'Ingrese La Cédula del Representante')
        self.ci_entry.bind('<FocusIn>', lambda event: self.ci_entry.delete(0, 'end')) # Elimina el texto de marcador de posición
        self.ci_entry.bind("<KP_Enter>", lambda event: self.fill_entries()) # Evento para la tecla Enter
        self.ci_entry.bind("<Return>", lambda event: self.fill_entries()) # Evento para la tecla Enter
        self.ci_entry.place(relx=0.46, rely=0.05, anchor='center', width=w, height=a)

        # Botón Buscar
        search_button = tk.Button(self.fact_frame, text="Buscar", font=font, bg='DeepSkyBlue2', width=5, height=1, bd=1, command=self.fill_entries)
        search_button.place(relx=0.56, rely=0.05, anchor='e')

        # Campo Alumno
        self.alumno_label = tk.Label(self.fact_frame, text="ALUMNO", font=font, bd=0, bg='#F0F3F4')
        self.alumno_label.place(relx=0.2, rely=r1, anchor='w')
        self.alumno_combobox = ttk.Combobox(self.fact_frame, values=[], font=font, style='TCombobox')
        self.alumno_combobox.place(relx=0.2, rely=r2, anchor='w', width=w, height=a)
        self.alumnos_comboboxes.append(self.alumno_combobox)

        # Campo Mes y Tipo de Pago
        self.meses_label = tk.Label(self.fact_frame, text="MES", font=font, bd=0, bg='#F0F3F4')
        self.meses_label.place(relx=0.32, rely=r1, anchor='w')
        self.meses_combobox = ttk.Combobox(self.fact_frame, values=[
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ], font=font, style='TCombobox')
        self.meses_combobox.place(relx=0.32, rely=r2, anchor='w', width=w, height=a)
        self.meses_comboboxes.append(self.meses_combobox)

        self.tipo_label = tk.Label(self.fact_frame, text="TIPO DE PAGO", font=font, bd=0, bg='#F0F3F4')
        self.tipo_label.place(relx=0.44, rely=r1, anchor='w')
        self.tipo_combobox = ttk.Combobox(self.fact_frame, values=["Mensualidad", "Inscripción"], font=font, style='TCombobox')
        self.tipo_combobox.place(relx=0.44, rely=r2, anchor='w', width=w, height=a)
        self.tipos_comboboxes.append(self.tipo_combobox)
        self.tipo_combobox.set("Mensualidad")

        # Campo Monto
        # Crear el estilo personalizado
        self.monto_label = tk.Label(self.fact_frame, text="MONTO A PAGAR", font=font, bd=0, bg='#F0F3F4')
        self.monto_label.place(relx=0.56, rely=r1, anchor='w')
        self.monto_entry = ttk.Entry(self.fact_frame, font=font, style='TEntry', justify='center')
        self.monto_entry.place(relx=0.56, rely=r2, anchor='w', width=w, height=a)
        self.monto_entries.append(self.monto_entry)

        # Botón para agregar otro alumno
        add_button = tk.Button(self.fact_frame, text="Agregar Alumno", justify='center', bg='#F9E79F', bd=1, font=font,
                               command=self.add_another_alumno)
        add_button.place(relx=0.8, rely=0.20, anchor='se')

        # Botón para facturar
        self.facturar_button = tk.Button(self.fact_frame, text="FACTURAR", font=font, bg='#F9E79F', width=15, height=1, bd=1,
                                         command=self.on_facturar_button_click)
        self.facturar_button.place(relx=0.95, rely=0.90, anchor='se')

    def fill_entries(self):
        cedulaFact = self.ci_entry.get()
        alumnos = self.get_alumnos_by_representante(cedulaFact)
        if alumnos:
            self.alumno_combobox['values'] = alumnos
            self.alumno_combobox.current(0)
        else:
            messagebox.showwarning("No encontrado", "No se encontraron alumnos para este representante.")

    def get_alumnos_by_representante(self, cedula_representante):
        cursor = mydb.cursor()
        query = """
        SELECT a.nombre 
        FROM alumno a
        JOIN representante r ON a.cedula_representante = r.cedula
        WHERE r.cedula = %s
        """
        cursor.execute(query, (cedula_representante,))
        result = cursor.fetchall()
        cursor.close()
        return [row[0] for row in result]

    def add_another_alumno(self):
        # Crear otro set de widgets para alumno, mes, tipo y monto
        font = ('noto sans', 10, 'bold')
        w = 150
        rx = 0.65
        r = 0.385

        # Calcular la posición vertical de los nuevos widgets
        rely = 0.19 + len(self.alumnos_comboboxes) * 0.06

        alumno_combobox = ttk.Combobox(self.fact_frame, values=self.alumno_combobox['values'], font=font, style='TCombobox')
        alumno_combobox.place(relx=0.2, rely=rely, anchor='w', width=w, height=26)
        self.alumnos_comboboxes.append(alumno_combobox)

        meses_combobox = ttk.Combobox(self.fact_frame, values=self.meses_combobox['values'], font=font, style='TCombobox')
        meses_combobox.place(relx=0.32, rely=rely, anchor='w', width=w, height=26)
        self.meses_comboboxes.append(meses_combobox)

        tipo_combobox = ttk.Combobox(self.fact_frame, values=self.tipo_combobox['values'], font=font, style='TCombobox')
        tipo_combobox.place(relx=0.44, rely=rely, anchor='w', width=w, height=26)
        self.tipos_comboboxes.append(tipo_combobox)
        self.tipo_combobox.set("Mensualidad")

        monto_entry = ttk.Entry(self.fact_frame, font=font, style='TEntry')
        monto_entry.place(relx=0.56, rely=rely, anchor='w', width=w, height=26)
        self.monto_entries.append(monto_entry)

        # Crear el botón "Eliminar" para esta fila
        delete_button = tk.Button(self.fact_frame, text="Eliminar", font=font, bg='red2', fg='white', bd=1, 
                                command=lambda: self.kill_widgets(alumno_combobox, meses_combobox, tipo_combobox, monto_entry, delete_button))
        delete_button.place(relx=0.75, rely=rely, anchor='w')

    def kill_widgets(self, alumno_combobox, meses_combobox, tipo_combobox, monto_entry, delete_button):
         # Eliminar los widgets de la interfaz y las listas
        alumno_combobox.destroy()
        meses_combobox.destroy()
        tipo_combobox.destroy()
        monto_entry.destroy()
        delete_button.destroy()

        # Actualizar las listas
        self.alumnos_comboboxes.remove(alumno_combobox)
        self.meses_comboboxes.remove(meses_combobox)
        self.tipos_comboboxes.remove(tipo_combobox)
        self.monto_entries.remove(monto_entry)


    def on_facturar_button_click(self):
        cedula = self.ci_entry.get()
        fecha_actual = datetime.today()

        cursor = mydb.cursor()

        for i in range(len(self.alumnos_comboboxes)):
            alumno = self.alumnos_comboboxes[i].get()
            mes = self.meses_comboboxes[i].get()
            tipo_pago = self.tipos_comboboxes[i].get()
            monto = self.monto_entries[i].get()

            query = """
            INSERT INTO registro_pagos (cedula_representante, nombre_alumno, mes, tipo_pago, monto, fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (cedula, alumno, mes, tipo_pago, monto, fecha_actual))

        mydb.commit()
        cursor.close()

        messagebox.showinfo("Éxito", "Factura registrada correctamente.")
        self.print_windows()

    def print_windows(self):
        entries_list = [self.ci_entry, *self.monto_entries]

        def clear_entries():
            for entry in entries_list:
                entry.delete(0, 'end')
            self.alumno_combobox.set('')
            self.meses_combobox.set('')
            self.tipo_combobox.set('')
            for combobox in self.alumnos_comboboxes:
                combobox.set('')
            for combobox in self.meses_comboboxes:
                combobox.set('')
            for combobox in self.tipos_comboboxes:
                combobox.set('Mensualidad')
            for entry in self.monto_entries:
                entry.delete(0, 'end')
            self.ci_entry.delete(0, 'end')
            

        print_window = tk.Toplevel(self.root)
        print_window.title("Facturar")
        print_window.configure(bg='#D9D9D9')
        print_window.overrideredirect(True)
        print_window.attributes('-topmost', True)

        window_width = 560
        window_height = 274
        print_window.geometry(f'{window_width}x{window_height}')

        screen_width = print_window.winfo_screenwidth()
        screen_height = print_window.winfo_screenheight()
        position_top = screen_height // 2 - window_height // 2
        position_right = screen_width // 2 - window_width // 2

        print_window.geometry("+{}+{}".format(position_right, position_top))

        print_button = tk.Button(print_window, text="Imprimir",
                                 command=lambda: [print("Imprimir"), clear_entries(), print_window.destroy(), self.show_success_message()] )
        print_button.place(relx=0.2, rely=0.5)

        exit_button = tk.Button(print_window, text="Salir", command=lambda: [clear_entries(), print_window.destroy()])
        exit_button.place(relx=0.6, rely=0.5)

    def show_success_message(self):
        messagebox.showinfo("Éxito", "El proceso se completó con éxito")

    def close_tab(self):
        self.notebook.forget(self.fact_frame)
        self.notebook.place_forget()  # Oculta el notebook
        
"""
def main():
    root = tk.Tk()
    root.title("Facturación")
    root.geometry("1366x768")
    root.configure(bg='#D9D9D9')
    app = FacturacionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""