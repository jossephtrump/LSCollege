import tkinter as tk
from tkinter import messagebox, ttk
from module_funciones import search_button, error_cedula, name_data, mail_data, phone_data, close_button
from databaseManager import cursor, mydb
from datetime import datetime, timedelta
from tkcalendar import Calendar
import module_person
import module_access 

class FacturacionApp:
    def __init__(self, root):
        self.root = root
        self.payment_methods = []   # Lista para almacenar los combobox de métodos de pago
        self.monto_entries = []     # Lista para almacenar las entradas de montos
        self.zelle = "0"            # Variables para los montos por método de pago
        self.usdt = "0"
        self.efectivo = "0"
        self.bolivares = "0"
        self.initialize_ui()

    def initialize_ui(self):
        self.notebook = ttk.Notebook(self.root) # Crear un widget de tipo Notebook
        self.notebook.place(relx=0, rely=0.1, relwidth=1, relheight=0.9) 

        self.fact_frame = ttk.Frame(self.notebook) # Crear un frame dentro del notebook
        self.notebook.add(self.fact_frame, text="Facturación")
        
        self.fact_frame.configure(borderwidth=2, relief=tk.SUNKEN)
        
        self.create_widgets()
        close_button(self.fact_frame, self.notebook, self.fact_frame)  # Llamada a close_button

    def create_widgets(self):
        # Aquí creas todos los widgets necesarios dentro de self.fact_frame
        a = 26
        w = 440
        r = 0.385
        rx = 0.5
        font = ('noto sans', 10, 'bold')
        # campo cedula
        self.ci_label = tk.Label(self.fact_frame, text="CEDULA", font=font, bd=0, bg='#F0F3F4')
        self.ci_label.place(relx=r, rely=0.08, anchor='w')
        self.ci_entry = ttk.Entry(self.fact_frame, font=font, style='TEntry')
        self.ci_entry.insert(0, 'Ingrese la cédula del cliente') # Texto por defecto
        self.ci_entry.bind("<FocusIn>", lambda event: self.ci_entry.delete(0, 'end')) # Borrar el texto al hacer clic
        self.ci_entry.bind("<Return>", lambda event: self.fill_entries()) # Para teclados normales
        self.ci_entry.bind("<KP_Enter>", lambda event: self.fill_entries()) # Para teclados numéricos
        self.ci_entry.place(relx=rx, rely=0.12, anchor='center', width=w, height=a)
        
        # campo nombre
        self.name_label = tk.Label(self.fact_frame, text="NOMBRE", font=font, bd=0, bg='#F0F3F4')
        self.name_label.place(relx=r, rely=0.16, anchor='w')
        self.name_entry = ttk.Entry(self.fact_frame, style='TEntry')
        self.name_entry.place(relx=rx, rely=0.20, anchor='center', width=w, height=a)
        
        # campo correo
        self.correo_label = tk.Label(self.fact_frame, text="CORREO", font=font, bd=0, bg='#F0F3F4')
        self.correo_label.place(relx=r, rely=0.24, anchor='w')
        self.correo_entry = ttk.Entry(self.fact_frame, style='TEntry')
        self.correo_entry.place(relx=rx, rely=0.28, anchor='center', width=w, height=a)
            
        # campo telefono
        self.tlf_label = tk.Label(self.fact_frame, text="TELÉFONO", font=font, bd=0, bg='#F0F3F4')
        self.tlf_label.place(relx=r, rely=0.32, anchor='w')
        self.tlf_entry = ttk.Entry(self.fact_frame, style='TEntry')
        self.tlf_entry.place(relx=rx, rely=0.36, anchor='center', width=w, height=a)
               
        # campo suscripcion
        self.sus_label = tk.Label(self.fact_frame, text="SUSCRIPCIÓN", font=font, bd=0, bg='#F0F3F4')
        self.sus_label.place(relx=r, rely=0.40, anchor='w')
        self.sus_comb = ttk.Combobox(self.fact_frame, values=['Diario', 'Semanal','Mensual','Trimestral' ,'Anual'], 
                                      width=53, style='TCombobox', font=('Noto Sans', 11))
        self.sus_comb.insert(0, 'Seleccione la suscripción') # Texto por defecto
        self.sus_comb.place(relx=0.5, rely=0.44, anchor='center')
        
         # campo meses
        self.meses_label = tk.Label(self.fact_frame, text="MES", font=font, bd=0, bg='#F0F3F4')
        self.meses_label.place(relx=r, rely=0.48, anchor='w')
        self.meses_comb = ttk.Combobox(self.fact_frame, values=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                                                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], 
                                       width=53, style='TCombobox', font=('Noto Sans', 11))
        self.meses_comb.insert(0, 'Seleccione el mes') # Texto por defecto
        self.meses_comb.place(relx=0.5, rely=0.52, anchor='center')
        
        # campo metodo de pago
        self.metodo_label = tk.Label(self.fact_frame, text="MÉTODO DE PAGO", font=font, bd=0, bg='#F0F3F4')
        self.metodo_label.place(relx=r, rely=0.56, anchor='w')
        self.metodo_comb = ttk.Combobox(self.fact_frame, values=["Efectivo $", "Zelle", "USDT", "Pago Movil",  "Efectivo Bs" ], 
                                        width=27, style='TCombobox', font=('Noto Sans', 10))
        self.metodo_comb.insert(0, 'Seleccione el método de pago') # Texto por defecto
        self.metodo_comb.place(relx=0.44, rely=0.60, anchor='center')
        
        # campo monto
        self.monto_label = tk.Label(self.fact_frame, text="MONTO", font=font, bd=0, bg='#F0F3F4')
        self.monto_label.place(relx=0.525, rely=0.56, anchor='w')
        self.monto_entry = ttk.Entry(self.fact_frame, font=('Noto Sans', 8), width=10, style='TEntry')
        self.monto_entry.place(relx=0.54, rely=0.60, anchor='center')
        
        # Agregar el método de pago y el monto inicial a las listas
        self.payment_methods.append(self.metodo_comb)
        self.monto_entries.append(self.monto_entry)
        
        # Botón para añadir método de pago
        add_button = tk.Button(self.fact_frame, text=" + ", justify='center', bg='green', bd=0, font=font,
                               command=self.add_payment_method)
        add_button.place(relx=0.595, rely=0.61, anchor='se')

        # Botón para eliminar método de pago
        remove_button = tk.Button(self.fact_frame, text=" x ", font=font, bd=0, bg="IndianRed2",
                                  command=self.remove_payment_method)
        remove_button.place(relx=0.618, rely=0.61, anchor='se')

        # Agregar el combobox para el nivel de acceso
        self.access_level_label = tk.Label(self.fact_frame, text="NIVEL DE ACCESO", font=font, bd=0, bg='#F0F3F4')
        self.access_level_label.place(relx=r, rely=0.85, anchor='w')
        self.access_level_comb = ttk.Combobox(self.fact_frame, values=self.get_privilege_group_names(), 
                                              width=53, style='TCombobox', font=('Noto Sans', 11))
        self.access_level_comb.insert(0, 'Seleccione el nivel de acceso') # Texto por defecto
        self.access_level_comb.place(relx=0.5, rely=0.88, anchor='center')

        # Label y entry para mostrar el total
        self.total_label = tk.Label(self.fact_frame, text="", font=font, bg='#F0F3F4', bd=0, width=15, height=1)
        self.total_label.place(relx=0.71, rely=0.95, anchor='se')
        self.total_button = tk.Button(self.fact_frame, text="Total $", font=font, bg='#F9E79F', width=15, height=1, bd=0, 
                                      command=self.total_press) 
        self.total_button.place(relx=0.64, rely=0.95, anchor='se')

        # Label y entry para mostrar el total en Bolívares
        self.total_bs_label = tk.Label(self.fact_frame, text="", font=font, bg='#F0F3F4', bd=0, width=15, height=1)
        self.total_bs_label.place(relx=0.51, rely=0.95, anchor='se')  # Ajustar la posición según sea necesario
        self.total_bs_button = tk.Button(self.fact_frame, text="Total Bs", font=font, bg='#F9E79F', width=15, height=1, bd=0, 
                                         command=self.total_bs_press)
        self.total_bs_button.place(relx=0.44, rely=0.95, anchor='se')  # Ajustar la posición según sea necesario

        # Botón para facturar
        self.facturar_button = tk.Button(self.fact_frame, text="FACTURAR", font=font, bg='#F9E79F', width=15, height=1, bd=0,
                                        command=lambda: [self.on_facturar_button_click(), self.print_windows()])
        self.facturar_button.place(relx=0.90, rely=0.95, anchor='se')
        
        # Llamada a search_button dentro de create_widgets
        search_button(self.fact_frame, self.fill_entries, relx=0.603, rely=0.108)
        
    def get_privilege_group_names(self):
        privilege_groups = module_access.get_privilege_groups(module_access.external_signature_privilege_list)
        return [group['privilegeGroupName'] for group in privilege_groups if group['privilegeGroupName'].lower() not in ['morosos', 'empleados']]

    def add_payment_method(self):
        wx = 32
        new_pay_combobox = ttk.Combobox(self.fact_frame, values=["Efectivo $",  "Zelle", "USDT", "Pago Movil", "Efectivo Bs"], 
                                        width=wx, font=('Noto Sans', 8))
        new_pay_combobox.insert(0, 'Select')
        rely = 0.60 + len(self.payment_methods) * 0.06
        new_pay_combobox.place(relx=0.44, rely=rely, anchor='center')
        self.payment_methods.append(new_pay_combobox)

        new_monto_entry = ttk.Entry(self.fact_frame, font=('Noto Sans', 8), width=10, style='TEntry')
        new_monto_entry.insert(0, '$0.00')
        new_monto_entry.bind("<FocusIn>", lambda event: new_monto_entry.delete(0, 'end'))
        new_monto_entry.place(relx=0.54, rely=rely, anchor='center')
        self.monto_entries.append(new_monto_entry)

    def remove_payment_method(self):
        if self.payment_methods:
            last_pay_combobox = self.payment_methods.pop()
            last_pay_combobox.destroy()

        if self.monto_entries:
            last_monto_entry = self.monto_entries.pop()
            last_monto_entry.destroy()
    
    def total_press(self):
        self.zelle = "0"
        self.usdt = "0"
        self.efectivo = "0"
        self.bolivares = "0"

        for i in range(len(self.payment_methods)):
            method_var = self.payment_methods[i].get()
            monto_var = self.monto_entries[i].get()

            if method_var == "Efectivo $":
                self.efectivo = monto_var
            elif method_var == "Zelle":
                self.zelle = monto_var
            elif method_var == "USDT":
                self.usdt = monto_var
            elif method_var in ["Efectivo Bs", "Pago Movil"]:
                self.bolivares = monto_var

        try:
            total = float(self.zelle if self.zelle else 0) + float(self.efectivo if self.efectivo else 0) + float(self.usdt if self.usdt else 0) 
            self.total_label.config(text=f"${total:.2f}")
        except ValueError:
            self.total_label.config(text="Error en los montos")

    def total_bs_press(self):
        self.bolivares = "0"

        for i in range(len(self.payment_methods)):
            method_var = self.payment_methods[i].get()
            monto_var = self.monto_entries[i].get()

            if method_var in ["Efectivo Bs", "Pago Movil"]:
                self.bolivares = monto_var

        try:
            total_bs = float(self.bolivares if self.bolivares else 0)
            self.total_bs_label.config(text=f"{total_bs:.2f} Bs")
        except ValueError:
            self.total_bs_label.config(text="Error en los montos")
        
    def on_button_press(self):
        cedulaFact = self.ci_entry.get
        suscripcion = self.sus_comb.get()
        if not cedulaFact or not suscripcion:
            print("Debe ingresar cédula y suscripción")
            messagebox.showerror("Error", "Debe ingresar cédula y suscripción")
            return
        payment_method1 = self.metodo_comb.get()  # Ejemplo, deberías obtener este valor de algún widget

        if payment_method1 == "Efectivo $":
            self.efectivo = self.monto_entry.get()
            self.bolivares = ""
            self.zelle = ""
            self.usdt = ""
        elif payment_method1 == "Efectivo Bs":
            self.bolivares = self.monto_entry.get()
            self.efectivo = ""
            self.zelle = ""
            self.usdt = ""
        elif payment_method1 == "Zelle":
            self.zelle = self.monto_entry.get()
            self.bolivares = ""
            self.efectivo = ""
            self.usdt = ""
        elif payment_method1 == "USDT":
            self.usdt = self.monto_entry.get()
            self.bolivares = ""
            self.zelle = ""
            self.efectivo = ""
        elif payment_method1 == "Pago Movil":
            self.bolivares = self.monto_entry.get()
            self.efectivo = ""
            self.zelle = ""
            self.usdt = ""

        self.total_press()
        self.cedula_fact(cedulaFact, suscripcion, self.zelle, self.usdt, self.bolivares, self.efectivo)
               
    def fill_entries(self):
        cedulaFact = self.ci_entry.get()
        error_cedula(cedulaFact)  # Assuming error_cedula is accessible
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, name_data(cedulaFact))  # Assuming name_data is a function that returns a name based on cedula
        self.name_entry.config(state='normal')
        self.correo_entry.delete(0, 'end')
        self.correo_entry.insert(0, mail_data(cedulaFact))  # Assuming mail_data is a function that returns an email based on cedula
        self.correo_entry.config(state='normal')
        self.tlf_entry.delete(0, 'end')
        self.tlf_entry.insert(0, phone_data(cedulaFact))  # Assuming phone_data is a function that returns a phone number based on cedula
        self.tlf_entry.config(state='normal')
        
    def cedula_fact(self, cedulaFact, suscripcion, zelle, usdt, bolivares, efectivo):
        print(f"Cédula: {cedulaFact}, Suscripción: {suscripcion}, Zelle: {zelle}, USDT: {usdt}, Bolívares: {bolivares}, Efectivo: {efectivo}")

    # Función para insertar los datos en la base de datos     
    def on_facturar_button_click(self):
        cedula = self.ci_entry.get()
        suscripcion = self.sus_comb.get()
        mes = self.meses_comb.get()  # Obtener el mes seleccionado
        
        # Obtener la fecha actual
        fecha_actual = datetime.today()
        
        # Inicializar los montos para cada método de pago
        total_zelle = 0.0
        total_usdt = 0.0
        total_efectivo = 0.0
        total_bolivares = 0.0

        for i in range(len(self.payment_methods)):
            metodo_pago = self.payment_methods[i].get()
            monto = self.monto_entries[i].get()

            # Convertir el monto a float y sumarlo al total correspondiente
            try:
                monto = float(monto)
            except ValueError:
                monto = 0.0

            if metodo_pago == "Efectivo $":
                total_efectivo += monto
            elif metodo_pago == "Zelle":
                total_zelle += monto
            elif metodo_pago == "USDT":
                total_usdt += monto
            elif metodo_pago in ["Efectivo Bs", "Pago Movil"]:
                total_bolivares += monto

        # Insertar en la base de datos MySQL
        cursor.execute('''
            INSERT INTO facturacion (zelle, usdt, bolivares, efectivo, suscripcion, mes, cedula, fechaPago)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (total_zelle, total_usdt, total_bolivares, total_efectivo, suscripcion, mes, cedula, fecha_actual))
        mydb.commit()
        print("Datos insertados correctamente")
        messagebox.showinfo("Éxito", "Factura registrada correctamente.")
            
    # Manejar acceso
        access_level = self.access_level_comb.get()
        if access_level:
            # Obtener ID de grupo de privilegios
            privilege_groups = module_access.get_privilege_groups(module_access.external_signature_privilege_list)
            privilege_group_id = None
            for group in privilege_groups:
                if group['privilegeGroupName'].lower() == access_level.lower():
                    privilege_group_id = group['privilegeGroupId']
                    break

            if privilege_group_id:
                person_info = module_person.get_person_info(cedula, module_access.external_signature_list)
                if person_info:
                    person_id = person_info['personId']
                    # Eliminar acceso actual
                    current_privilege_group = None
                    for group in privilege_groups:
                        person_privileges = module_access.get_person_privileges(group['privilegeGroupId'], module_access.signature_privilege_group_person_list)
                        if any(person['id'] == person_id for person in person_privileges):
                            current_privilege_group = group
                            break

                    if current_privilege_group:
                        module_access.delete_all_access_levels(person_id, current_privilege_group['privilegeGroupId'])

                    # Asignar nuevo acceso
                    module_access.assign_access_level(person_id, privilege_group_id)

    def print_windows(self):
        entries_list = [self.ci_entry, self.name_entry, self.correo_entry, self.tlf_entry, self.monto_entry]

        def clear_entries():
            for entry in entries_list:
                entry.delete(0, 'end')
            self.total_label.config(text="")

        print_window = tk.Toplevel(self.root)
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
       
        # Botones en la ventana de impresión
        print_button = tk.Button(print_window, text="Imprimir",
                                  command=lambda: [print("Imprimir"), clear_entries(), print_window.destroy(), self.show_success_message()])
        print_button.place(relx=0.2, rely=0.5)

        exit_button = tk.Button(print_window, text="Salir", command=lambda: [clear_entries(), print_window.destroy()])
        exit_button.place(relx=0.6, rely=0.5)
        
    def show_success_message(self):
        messagebox.showinfo("Éxito", "El proceso se completó con éxito")
"""
def main():
    root = tk.Tk()
    root.title("Facturación")
    root.geometry("1366x768")
    root.configure(bg='#D9D9D9')
    root.iconbitmap('gym.ico')
    root.attributes('-topmost', True)
    #root.resizable(False, False)
    app = FacturacionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""