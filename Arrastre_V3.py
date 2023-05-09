# Importing Libraries
import serial
import time
import tkinter
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from playsound import playsound

# Importamos los arduinos
A_arrastre = serial.Serial(port='COM4', baudrate=9600, timeout=.1)
A_ordenador = serial.Serial(port='COM7', baudrate=9600, timeout=.1)
A_embobinado = serial.Serial(port='COM6', baudrate=9600, timeout=.1)
RPM_Extrusora = serial.Serial(port='COM9', baudrate=9600, timeout=.1)

time.sleep(2)

# gráfica
# variable globales
RPM = np.array([])
data = np.array([])
RPM_A = np.array([])
Vel_Prom = np.array([])
flag_plot_data = False

# Variables de Arduino
enable_mitutoyo = 1
enable_temperatura = 1
id_rpm_arrastre = '0'
id_en_arrastre = '1'
id_dir_arrastre = '2'

id_rpm_ordenador = '3'
id_en_ordenador = '4'
id_dir_ordenador = '5'
id_home_ordenador = '6'

id_rpm_embobinado = '7'
id_en_embobinado = '8'
id_dir_embobinado = '9'

id_ventiladores = '10'
flag_RPMext = 0
flag_RPM_Arrastre = 1
j = 0
valor_embobinado = 0
valor_arrastre = 0
valor_arrastre_prev = 0
valor_ordenador = 0
valor_rpm_extrusora = 0
start_t = 0
flag_update_metros = 0
metros_embobinados = 0
Sensor_buffer = 'K'
f_r = 0.80
RPM_ref = 0
median = 0
vt = 0
RPM_prev = 0
pid_diametro = 0
start_pid = 0
rpm_ext_prev = 0
ei = 0
da = 0
cpr = 0
ctr = 0
rpm_nueva = 0
fs100 = 0
fs200 = 0
fs300 = 0
fs350 = 0
flag_fcd = 0
start_fcd = 0

# Creamos la ventana
ventana = tkinter.Tk()
ventana.iconbitmap('images/favicon.ico')
ventana.title("Estacion de embobinado")
ventana.geometry("1600x900+0+0")

# Variables ventilador
texto = 'Habilitar'
estado = 1
estado_arrastre = 1
estado_ordenador = 1
estado_embobinado = 1
estado_inicio = 1
valor2 = 0
u = 1
i = 0
k = 0
Kp = 0
da_prev = 0
tdi = 5
tds = 0
diam_prev = 0
rpme_prev = 0
nombre_archivo = ' '
nombre_archivo_ext = ' '
flag_archivo = 0
flag_ctrlp = 0
nueva_rpm_arrastre = 0
flag_temperatura_tanque = 1
# Creamos nuestra imagen de fondo
bg = tkinter.PhotoImage(file="images/BG2.png")

fondo = tkinter.Label(ventana, image=bg)
fondo.place(x=0, y=0, relwidth=1, relheight=1)

# Creamos título
titulo = tkinter.Label(ventana, text="Línea extrusión de filamento", font=("Kelson Sans", 30), fg="white", bg='#34393b')
titulo.place(x=550, y=10)

# cosas de gráfica
fig = Figure()
ax = fig.add_subplot(111)
ax.set_title('Medición de diámetro')
ax.set_xlabel('Muestras')
ax.set_ylabel('Diámetro (mm)')
ax.set_xlim(0, 300)
ax.set_ylim(1.6, 1.9)
ax.grid(True)

fig2 = Figure()
bx = fig2.add_subplot(111)
bx.set_title('PID Arrastre')
bx.set_xlabel('Muestras')
bx.set_ylabel('RPM')
bx.set_xlim(0, 150)
bx.set_ylim(30, 45)#35,50
bx.grid(True) 

lines = ax.plot([], [])[0]
target = ax.plot([], [])[0]
limsup = ax.plot([], [])[0]
liminf = ax.plot([], [])[0]
lrpma = bx.plot([], [])[0]

data_ext = np.array([])
flag_plot_data_Ext = False

canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().place(x=25, y=400, width=550, height=380)
canvas.draw()

canvas2 = FigureCanvasTkAgg(fig2, master=ventana)
canvas2.get_tk_widget().place(x=595, y=400, width=550, height=380)
canvas2.draw()
RPM_C = 0
flag_senal = 0
rpma_f = 0


def loop():
    global flag_plot_data, data, flag_update_metros, start, valor_embobinado, flag_archivo, i, RPM_A, pid_diametro, da
    global da_prev, rpm_ext_prev, flag_ctrlp, k, RPM, Kp, valor2, RPM_ref, u, median, data_ext,flag_fcd
    global vt, valor_rpm_extrusora, id_rpm_arrastre, start_pid, ctr, cpr, rpm_nueva, diam_prev, start_fcd
    global flag_update_metros, start_t, valor_embobinado, metros_embobinados, flag_temperatura_tanque
    global tdi, tds, rpme_prev, Sensor_buffer, valor_arrastre, valor_arrastre_prev, j, flag_plot_data_Ext
    global nombre_archivo_ext, flag_RPMext, RPM_prev, flag_RPM_Arrastre, ei, Vel_Prom, nueva_rpm_arrastre
    global fs100, fs200, fs300, fs350, flag_senal, RPM_C, rpma_f
    if flag_plot_data:
        try:
            if diam_ser.in_waiting > 0:
                a = diam_ser.readline()
                diam_ser.reset_input_buffer()
                a.decode()
                a.strip()
                try:
                    da = a.decode()
                    da = float(da.strip())
                except:
                    da = diam_prev
                if type(da) is float and da > 2.5 or da < 1 or da == 2.0 or da == 1.0:
                    da = diam_prev
                else:
                    diam_prev = da
                if len(data) < 300:
                    data = np.append(data, float(str(da)[0:4]))
                else:
                    data[0:299] = data[1:300]
                    data[299] = float(str(da)[0:4])
                lines.set_xdata(np.arange(0, len(data)))
                lines.set_ydata(data)
                target.set_xdata(np.arange(0, len(data)))
                target.set_ydata(1.75)
                liminf.set_xdata(np.arange(0, len(data)))
                liminf.set_ydata(1.70)
                limsup.set_xdata(np.arange(0, len(data)))
                limsup.set_ydata(1.80)
                canvas.draw()
                if flag_archivo == 1:
                    try:
                        f = open(nombre_archivo, 'a+')
                        f.write(str(i) + ',' + str(round(metros_embobinados, 2)) + ',' + str(da) + ',' + '1.75' + '\n')
                        i += 1
                        f.close()
                        if flag_fcd == 1:
                            file_ext = open(nombre_archivo_ext, 'a+')
                            file_ext.write(str(da) + ',' + str(median) + ',' + str(vt) + ',' + str(nueva_rpm_arrastre) + ',' + str(rpma_f) + '\n')
                            file_ext.close()
                        else:
                            file_ext = open(nombre_archivo_ext, 'a+')
                            file_ext.write(
                                str(da) + ',' + str(median) + ',' + str(vt) + ',' + str(valor_arrastre) + ',' + str(rpma_f) + '\n')
                            file_ext.close()
                    except:
                        print("no se pudo arbrir el txt")
                    try:
                        if j>2:
                            file_ext = open(nombre_archivo_ext, 'a+')
                            file_ext.write(str(da) + ',' + str(median) + ',' + str(vt) + ',' + str(nueva_rpm_arrastre) + ',' + str(rpma_f) + '\n')
                            file_ext.close()
                    except:
                        print("no se pudo arbrir el txt_ext")
        except:
            print('Enciende el sensor')
            flag_plot_data = False
            popup()
    if flag_update_metros == 1:
        try:
            if A_embobinado.in_waiting > 0:
                rpm_nueva = A_embobinado.readline()
                A_embobinado.reset_input_buffer()
                rpm_nueva = rpm_nueva.decode()
                rpm_nueva = rpm_nueva.strip()
                rpm_nueva = round((float(rpm_nueva)*60)/6400, 2)
            if rpm_nueva == 0:
                d_embobinado_a["text"] = str(valor_embobinado)
            else:
                d_embobinado_a["text"] = str(rpm_nueva)
        except:
            rpm_nueva = 15
            print("Falla EM")
        try:
            end = time.time()
            actual = end - start_t
            start_t = time.time()
            pi = 3.1416
            diametro = 0.055
            arco = pi * diametro
            metros_embobinados += (valor_arrastre * arco / 60) * (1 * actual)
            d_metros_a["text"] = str(round(metros_embobinados, 2))
            delta = tds-tdi
            val_delta_diam["text"] = str(round(delta, 3))
            if da > tds:
                tds = da
                d_diam_max_a["text"] = str(round(tds, 3))
            elif da < tdi:
                tdi = da
                d_diam_min_a["text"] = str(round(tdi, 3))
        except:
            print('Enciende el sensor UM')
        try:
            if float(metros_embobinados) > 100 and fs100 == 0:
                fs100 = 1
                playsound('100_metros.wav', block=False)
                print("100")
        except:
            fs100 = 1
            print("Error Audio 100 metros")
        try:
            if float(metros_embobinados) > 200 and fs200 == 0:
                fs200 = 1
                playsound('200_metros.wav', block=False)
        except:
            fs200 = 1
            print("Error Audio 200 metros")
        try:
            if float(metros_embobinados) > 300 and fs300 == 0:
                fs300 = 1
                playsound('300_metros.wav', block=False)
        except:
            fs300 = 1
            print("Error Audio 300 metros")
        try:
            if float(metros_embobinados) >= 350 and fs350 == 0:
                fs350 = 1
                playsound('TF023.wav', block=False)
        except:
            fs350 = 1
            print("Error Audio")
    if flag_RPM_Arrastre == 1:
        try:
            if A_arrastre.in_waiting > 0 :
                rpma = A_arrastre.readline()
                A_arrastre.reset_input_buffer()
                if len(RPM_A) < 150:
                    RPM_A = np.append(RPM_A, float(rpma[0:4]))
                else:
                    RPM_A[0:149] = RPM_A[1:150]
                    RPM_A[149] = float(rpma[0:4])
                lrpma.set_xdata(np.arange(0, len(RPM_A)))
                lrpma.set_ydata(RPM_A)
                try:
                    rpma_f = rpma.decode()
                    rpma_f = float(rpma_f.strip())
                except:
                    print("rpma_f")
                canvas2.draw()
        except:
            a=1
#                                       BOTON RPM EXTRUSORA
    if flag_RPMext == 1:
        try:
            if RPM_Extrusora.in_waiting > 0:
                r = RPM_Extrusora.readline()
                r = r.decode()
                r = r.strip()
                w = float(r)
                w = round(w, 2)
                if w <= 1510:
                    rpm_ext_prev = w
                else:
                    w = rpm_ext_prev
                median = w
                RPM_C = w
                datum = round(2.85714286 * w - 4246.29143, 2)
                rev_husillo["text"] = str(w) +  '     Arrastre: '+str(datum)
        except:
            flag_RPMext = 1
            a=1
    if flag_fcd == 1:
        end_fcd = time.time()
        actual_fcd = end_fcd - start_fcd
        if actual_fcd >= 2:
            try:#Leemos el valor de RPM_ext
                rpm_random = RPM_C #random.uniform(1490, 1492)
                #Calculamos rpm arrastre
                nueva_rpm_arrastre = round(2.85714286 * rpm_random - 4246.29143, 2)
                #nueva_rpm_arrastre = round(0.33333333 * rpm_random - 458.23, 2)
                seree = id_rpm_arrastre + ',' + str(nueva_rpm_arrastre) + '\n'
                A_arrastre.write(seree.encode('ascii'))
                d_arrastre_a["text"] = str(nueva_rpm_arrastre)
            except:
                print("FCD")
            start_fcd = time.time()
    ventana.after(1, loop)


def a_arrastre():
    global valor_arrastre, valor_arrastre_prev
    try:
        valor_arrastre =float(i_arrastre.get())
        valor_arrastre_prev = float(i_arrastre.get())
        ser = id_rpm_arrastre + ',' + str(valor_arrastre) + '\n'
        #print(ser)
        A_arrastre.write(ser.encode('ascii'))
        d_arrastre_a["text"] = str(valor_arrastre) #puse indent de mas, si falla algo,quitar indent
    except:
        print("Error en función >a_arrastre<")


def h_arrastre():
    global estado_arrastre
    if estado_arrastre == 1:
        bh_arrastre["text"] = 'Deshabilitar'
        estado_arrastre = 0
        ser = id_en_arrastre + ',' + '0\n'
        A_arrastre.write(ser.encode('ascii'))
    elif estado_arrastre == 0:
        bh_arrastre["text"] = 'Habilitar'
        estado_arrastre = 1
        ser = id_en_arrastre + ',' + '1\n'
        A_arrastre.write(ser.encode('ascii'))


def e_fcd():
    global flag_fcd, valor_arrastre, start_fcd,flag_senal
    start_fcd = time.time()
    if flag_fcd == 0:
        flag_fcd = 1
        b_fcd["text"] = 'Deshabilitar'
    elif flag_fcd == 1:
        flag_fcd = 0
        b_fcd["text"] = 'Habilitar'


def a_ordenador():
    global valor_ordenador, i_Kp
    try:
        valor = float(i_Kp.get()) * (6400 / 60)
        valor_ordenador = float(i_Kp.get())
        ser = id_rpm_ordenador + ',' + str(valor) + '\n'
        A_ordenador.write(ser.encode('ascii'))
    except:
        print("Error en función >a_ordenador<")


def h_ordenador():
    global estado_ordenador
    if estado_ordenador == 1:
        estado_ordenador = 0
        ser = id_en_ordenador + ',' + '0\n'
        A_ordenador.write(ser.encode('ascii'))
    elif estado_ordenador == 0:
        estado_ordenador = 1
        ser = id_en_ordenador + ',' + '1\n'
        A_ordenador.write(ser.encode('ascii'))


def home_ordenador():
    global metros_embobinados
    metros_embobinados = 0
    d_metros_a["text"] = '0.0'
    ser = id_home_ordenador + ',' + '0\n'
    A_ordenador.write(ser.encode('ascii'))


def a_embobinado():
    global valor_embobinado, rpm_nueva
    try:
        valor = float(i_embobinado.get()) * (6400 / 60)
        valor_embobinado = float(i_embobinado.get())
        rpm_nueva = valor_embobinado
        ##d_embobinado_a["text"] = str(valor_embobinado)
        ser = id_rpm_embobinado + ',' + str(valor) + '\n'
        A_embobinado.write(ser.encode('ascii'))
    except:
        print("Error en función >a_embobinado<")


def h_embobinado():
    global estado_embobinado, start_t, flag_update_metros, flag_archivo
    try:
        if estado_embobinado == 1:
            start_t = time.time()
            flag_update_metros = 1
            bh_embobinador["text"] = 'Deshabilitar'
            estado_embobinado = 0
            ser = id_en_embobinado + ',' + '0\n'
            A_embobinado.write(ser.encode('ascii'))
        elif estado_embobinado == 0:
            flag_update_metros = 0
            bh_embobinador["text"] = 'Habilitar'
            estado_embobinado = 1
            ser = id_en_embobinado + ',' + '1\n'
            A_embobinado.write(ser.encode('ascii'))
    except:
        print("Error en función >h_embobinado<")


def v_ventiladores():
    global estado
    if estado == 1:
        b_ventiladores["text"] = 'Deshabilitar'
        estado = 0
        ser = id_ventiladores + ',' + '255\n'
        A_ordenador.write(ser.encode('ascii'))
    elif estado == 0:
        b_ventiladores["text"] = 'Habilitar'
        estado = 1
        ser = id_ventiladores + ',' + '0\n'
        A_ordenador.write(ser.encode('ascii'))


def plot_start():
    global flag_plot_data
    flag_plot_data = True
    diam_ser.reset_input_buffer()


def plot_stop():
    global flag_plot_data, flag_ctrlp, j
    flag_plot_data = False
    flag_ctrlp = 0
    j = 0


def iniciar():
    global valor_embobinado, valor_ordenador, valor_arrastre, start_t, flag_update_metros, estado_inicio, flag_archivo, tdi, tds
    global fs100, fs200, fs300, fs350
    valor_e = float(i_embobinado.get()) * (6400 / 60)
    valor_embobinado = float(i_embobinado.get())
    ser_e = id_rpm_embobinado + ',' + str(valor_e) + '\n'
    A_embobinado.write(ser_e.encode('ascii'))
    archivo_txt()
    if estado_inicio == 1:
        start_t = time.time()
        fs100 = 0
        fs200 = 0
        fs300 = 0
        fs350 = 0
        flag_update_metros = 1
        binicio["text"] = 'Parar'
        bh_embobinador["text"] = 'Deshabilitar'
        estado_inicio = 0
        ser_e = id_en_embobinado + ',' + '0\n'
        ser_o = id_en_ordenador + ',' + '0\n'
        A_embobinado.write(ser_e.encode('ascii'))
        #A_ordenador.write(ser_o.encode('ascii'))
    elif estado_inicio == 0:
        flag_update_metros = 0
        binicio["text"] = 'Iniciar'
        bh_embobinador["text"] = 'Habilitar'
        val_delta_diam["text"] = "0"
        home_ordenador()
        estado_inicio = 1
        ser_e = id_en_embobinado + ',' + '1\n'
        ser_o = id_en_ordenador + ',' + '1\n'
        A_embobinado.write(ser_e.encode('ascii'))
        #A_ordenador.write(ser_o.encode('ascii'))
        flag_archivo = 0
        tdi = 5
        tds = 0


def popup():
    info = tkinter.Toplevel()  # Popup -> Toplevel()
    info.geometry('500x100+0+0')
    info.title('¡Error!')
    info.configure(bg = 'red')
    tkinter.Label(info, text="Asegúrate de que el sensor está encendido e intenta nuevamente.", font=("Kelson Sans", 10),
                               fg="white",
                               bg='red').pack(padx=10, pady=5)
    tkinter.Button(info, text='Aceptar', command=info.destroy).pack(padx=10, pady=10)
    #tkinter.transient(pack)  # Popup reduction impossible
    #tkinter.grab_set()  # Interaction with window impossible game


def archivo_txt():
    global flag_archivo, i, nombre_archivo, nombre_archivo_ext
    nombre_archivo = str(datetime.datetime.now())
    nombre_archivo = nombre_archivo.replace(":", "_")
    nombre_archivo = nombre_archivo.replace(".", "_")
    nombre_archivo = nombre_archivo.replace(" ", "_")
    nombre_archivo_ext = nombre_archivo
    nombre_archivo = "G:/My Drive/Stamps/" + nombre_archivo + '.csv'
    nombre_archivo_ext = "G:/My Drive/Stamps/EXTRUSORA/" + nombre_archivo_ext + 'ext' + '.csv'
    try:
        f = open(nombre_archivo, 'a+')
        f.write("Muestra" + ',' + "Distance" + ',' + "Diametro" + ',' "Promedio" + '\n')
        f.close()
    except:
        print("no se pudo arbrir el txt")
    flag_archivo = 1
    i = 1


def iniciarRPM():
    global flag_RPMext
    flag_RPMext = 1


def reset_diametros():
    global tdi, tds
    tdi = 5
    tds = 0


def Serial_Mitutoyo():
    global enable_mitutoyo, diam_ser
    if enable_mitutoyo == 1:
        diam_ser = serial.Serial(port='COM8', baudrate=9600, timeout=.3)
        enable_mitutoyo = 0
        b_mitutoyo["text"] = 'Cerrar puerto'
    elif enable_mitutoyo == 0:
        diam_ser.close()
        b_mitutoyo["text"] = 'Abrir puerto'
        enable_mitutoyo = 1


# Creamos frame
frame = tkinter.Frame(ventana, bg='#34393b')
frame.place(x=20, y=55)

# Creamos Descripciones
d_arrastre = tkinter.Label(ventana, text="Ingresa las RPM del módulo de arrastre:", font=("Kelson Sans", 15), fg="white",
                           bg='#34393b').place(x = 25, y =68)
d_arrastre_a = tkinter.Label(ventana, text="0", font=("Kelson Sans", 15),
                             fg="yellow", bg='#34393b')
d_arrastre_a.place(x = 500, y =68)
d_embobinado = tkinter.Label(ventana, text="Ingresa las RPM del módulo de embobinado:", font=("Kelson Sans", 15),
                             fg="white", bg='#34393b').place(x = 25, y =115)
d_embobinado_a = tkinter.Label(ventana, text="0", font=("Kelson Sans", 15),
                             fg="yellow", bg='#34393b')
d_embobinado_a.place(x = 500, y =115)
d_ventiladores = tkinter.Label(ventana, text="Ventiladores de enfriamiento:", font=("Kelson Sans", 15), fg="white",
                               bg='#34393b').place(x = 25, y =160)
d_metros_o = tkinter.Label(ventana, text="Objetivo en Metros:         350", font=("Kelson Sans", 12), fg="white",
                               bg='#34393b').place(x = 1325, y =68)
d_metros = tkinter.Label(ventana, text="Metros embobinados:", font=("Kelson Sans", 12), fg="white",
                               bg='#34393b').place(x = 1325, y =138)
d_metros_a = tkinter.Label(ventana, text="0", font=("Kelson Sans", 12), fg="red",
                               bg='#34393b')
d_metros_a.place(x = 1505, y =138)
d_diam_max = tkinter.Label(ventana, text="Diámetro máximo:", font=("Kelson Sans", 12), fg="white",
                               bg='#34393b').place(x = 1325, y =208)
d_diam_max_a = tkinter.Label(ventana, text="0", font=("Kelson Sans", 12), fg="white",
                               bg='#34393b')
d_diam_max_a.place(x = 1505, y =208)
d_diam_min = tkinter.Label(ventana, text="Diámetro mínimo:", font=("Kelson Sans", 12), fg="white",
                               bg='#34393b').place(x = 1325, y =278)
d_diam_min_a = tkinter.Label(ventana, text="0", font=("Kelson Sans", 12), fg="green",
                               bg='#34393b')
d_diam_min_a.place(x = 1505, y =278)
delta_diam = tkinter.Label(ventana, text="Delta:", font=("Kelson Sans", 12), fg="white",
                               bg='#34393b').place(x = 1325, y =348)
val_delta_diam = tkinter.Label(ventana, text="0", font=("Kelson Sans", 12), fg="blue",
                               bg='#34393b')
val_delta_diam.place(x = 1505, y =348)
# Creamos entradas
i_arrastre = tkinter.Entry(ventana, width =5)
i_arrastre.place(x = 430, y =68)
i_embobinado = tkinter.Entry(ventana, width =5)
i_embobinado.place(x = 430, y =115)

# Creamos botones
b_arrastre = tkinter.Button(ventana, text="Aplicar", command=a_arrastre).place(x = 575, y =68)
bh_arrastre = tkinter.Button(ventana, text="Habilitar", command=h_arrastre)
bh_arrastre.place(x = 675, y =68)
bhome_ordenador = tkinter.Button(ventana, text="Reset", command=home_ordenador).place(x = 750,y = 95)
binicio = tkinter.Button(ventana, text="Iniciar", command=lambda: iniciar())
binicio.place(x = 810,y = 95)
b_embobinador = tkinter.Button(ventana, text="Aplicar", command=a_embobinado).place(x = 575,y = 115)
bh_embobinador = tkinter.Button(ventana, text="Habilitar", command=h_embobinado)
bh_embobinador.place(x = 675,y = 115)

b_ventiladores = tkinter.Button(ventana, text="Habilitar", command=v_ventiladores)
b_ventiladores.place(x = 375,y = 160)

b_fcd = tkinter.Button(ventana, text="Habilitar", command=e_fcd)
b_fcd.place(x = 375,y = 215)


b_reset_diametros = tkinter.Button(ventana, text="Reset", command=reset_diametros)
b_reset_diametros.place(x = 1325, y =418)

# gráfica
# Creamos botones
ventana.update()
start = tkinter.Button(ventana, text="Iniciar medición", command=lambda: plot_start())
start.place(x=320, y=800)
ventana.update()
stop = tkinter.Button(ventana, text="Parar", command=lambda: plot_stop())
stop.place(x=start.winfo_x() + start.winfo_reqwidth() + 20, y=800)
b_mitutoyo = tkinter.Button(ventana, text="Abrir puerto", command=Serial_Mitutoyo)
b_mitutoyo.place(x=stop.winfo_x() + stop.winfo_reqwidth() + 20, y =800)

##########################################
bRPMe = tkinter.Button(ventana, text="RPM Ext", command=lambda: iniciarRPM())
bRPMe.place(x = 25,y = 365)
rev_husillo = tkinter.Label(ventana, text="0", font=("Kelson Sans", 13), fg="white",
                               bg='#34393b')
rev_husillo.place(x = 88, y =365)

ventana.after(1, loop)
#ventana_ext.after(1, loop_ext)
ventana.state('zoomed')
ventana.mainloop()
#ventana_ext.mainloop()