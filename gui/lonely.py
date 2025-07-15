import os
import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import sys


script_dir = os.path.dirname(os.path.abspath(__file__))  
os.chdir(script_dir)


FFMPEG_PATH = os.path.join(script_dir, "bin", "ffmpeg.exe")

def obtener_ruta_recurso(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(script_dir, relative_path)

def run_ffmpeg_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Ocurrió un error al ejecutar FFmpeg:\n{e}")
        return False


def abrir_carpeta_de_archivo(ruta_archivo):
    carpeta = os.path.dirname(ruta_archivo)
    try:
        os.startfile(carpeta) 
    except Exception as e:
        messagebox.showwarning("Advertencia", f"No se pudo abrir la carpeta:\n{e}")


def seleccionar_archivo():
    filepath = filedialog.askopenfilename(
        title="Selecciona un archivo de video",
        filetypes=[("Archivos de video", "*.mp4 *.mov"), ("Todos los archivos", "*.*")]
    )
    return filepath


def seleccionar_resolucion():
    opciones = [
        "-2:-2 (Igual - sin reescalar)",
        "720:-2 (SD)",
        "1280:-2 (HD)",
        "1920:-2 (Full HD)",
        "2560:-2 (QHD)",
        "3840:-2 (4K Ultra HD)",
        "Personalizada..."
    ]

    resolucion_seleccionada = tk.StringVar()
    resolucion_seleccionada.set(opciones[0])

    def confirmar():
        seleccion = resolucion_seleccionada.get()
        if seleccion == "Personalizada...":
            custom = simpledialog.askstring("Resolución personalizada", "Ingresa la resolución (ancho:alto, usa -2 para mantener proporción):")
            if custom:
                ventana.destroy()
                callback(custom)
        else:
            ventana.destroy()
            callback(seleccion.split(" ")[0])  # Solo toma "1920:-2", etc.

    def callback(res):
        ventana.resultado = res

    ventana = tk.Toplevel(root)
    ventana.title("Selecciona la resolución")
    tk.Label(ventana, text="Selecciona una resolución:").pack(padx=10, pady=10)

    menu = tk.OptionMenu(ventana, resolucion_seleccionada, *opciones)
    menu.pack(padx=10, pady=5)

    tk.Button(ventana, text="Aceptar", command=confirmar).pack(pady=10)
    ventana.resultado = None
    ventana.grab_set()
    root.wait_window(ventana)
    return ventana.resultado


def pedir_crf():
    crf_input = simpledialog.askstring(
        "CRF (Calidad)",
        "Ingresa el valor CRF (0-51).\n0 = sin pérdida, 23 = predeterminado, 20 = alta calidad.\nDefault: 20"
    )
    try:
        if crf_input is None or crf_input.strip() == "":
            return 20
        crf = int(crf_input)
        if 0 <= crf <= 51:
            return crf
        else:
            messagebox.showwarning("Valor inválido", "El CRF debe estar entre 0 y 51. Se usará 20 por defecto.")
            return 20
    except ValueError:
        messagebox.showwarning("Valor inválido", "El CRF debe ser un número entero. Se usará 20 por defecto.")
        return 20


def convertir_video():
    input_path = seleccionar_archivo()
    if not input_path:
        return

    cScale = seleccionar_resolucion()
    if not cScale:
        return

    crf = pedir_crf()

    default_name = os.path.splitext(os.path.basename(input_path))[0] + "-convertido.mp4"
    output_path = filedialog.asksaveasfilename(
        title="Guardar video convertido como...",
        defaultextension=".mp4",
        initialfile=default_name,
        filetypes=[("Video MP4", "*.mp4")]
    )

    if not output_path:
        return

    command = f'"{FFMPEG_PATH}" -i "{input_path}" -vf scale={cScale} -vcodec libx264 -crf {crf} "{output_path}"'
    if run_ffmpeg_command(command):
        messagebox.showinfo("Éxito", f"Video convertido exitosamente:\n{output_path}")
        abrir_carpeta_de_archivo(output_path)


def cortar_video():
    input_path = seleccionar_archivo()
    if not input_path:
        return

    start_time = simpledialog.askstring("Inicio del corte", "Ingresa el tiempo de inicio (hh:mm:ss):")
    end_time = simpledialog.askstring("Fin del corte", "Ingresa el tiempo de finalización (hh:mm:ss):")
    if not start_time or not end_time:
        return

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1]
    default_name = base_name + "-recorte" + ext

    output_path = filedialog.asksaveasfilename(
        title="Guardar recorte como...",
        defaultextension=ext,
        initialfile=default_name,
        filetypes=[("Videos", "*.mp4 *.mov"), ("Todos los archivos", "*.*")]
    )

    if not output_path:
        return

    command = f'"{FFMPEG_PATH}" -ss {start_time} -to {end_time} -i "{input_path}" -c copy "{output_path}"'
    if run_ffmpeg_command(command):
        messagebox.showinfo("Éxito", f"Video cortado exitosamente:\n{output_path}")
        abrir_carpeta_de_archivo(output_path)

root = tk.Tk()
root.title("FFMPEG SIX's MENU")
icon_path = obtener_ruta_recurso("favicon-black.ico")
root.iconbitmap(icon_path)


tk.Label(root, text="============================", font=("Arial", 12)).pack()
tk.Label(root, text="    FFMPEG SIX's MENU", font=("Arial", 14, "bold")).pack()
tk.Label(root, text="============================", font=("Arial", 12)).pack(pady=(0, 10))

tk.Button(root, text="1. Convertir Video", width=30, command=convertir_video).pack(pady=5)
tk.Button(root, text="2. Cortar Video", width=30, command=cortar_video).pack(pady=5)
tk.Button(root, text="3. Salir", width=30, command=root.quit).pack(pady=20)

root.mainloop()
