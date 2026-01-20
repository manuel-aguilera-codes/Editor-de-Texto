'''Crea una interfaz gráfica de usuario (GUI) para simular nuestro propio editor de texto. Este ejemplo 
también utiliza componentes estándar de GUI, incluyendo etiquetas, botones y campos de entrada.
Puedes añadir la capacidad de abrir y guardar archivos, al igual que un editor de texto real.'''

import tkinter as tk
from tkinter import filedialog, messagebox

class BlockEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BlockEditor - Sin título")
        self.geometry("1000x700")
        self.minsize(600, 400)
        self.configure(bg="#2c3e50")

        # Variables importantes
        self.archivo_actual = None      # ruta del archivo abierto (o None)
        self.modificado = False         # ¿hay cambios sin guardar?

        # Barra de estado en la parte inferior
        self.label_status = tk.Label(self, text=" Listo", anchor="w", bg="#2c3e50", fg="#bdc3c7", font=("Segoe UI", 9))
        self.label_status.pack(side="bottom", fill="x")

        # Área de texto grande con scroll
        self.texto = tk.Text(self, wrap="word", undo=True, font=("Consolas", 12))
        self.texto.pack(expand=True, fill="both", padx=10, pady=10)

        # Scrollbar vertical
        scrollbar = tk.Scrollbar(self.texto)
        scrollbar.pack(side="right", fill="y")
        self.texto.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.texto.yview)

        # Detectar cuando el usuario escribe
        self.texto.bind("<Key>", self.texto_modificado)

        # Crear el menú
        self.crear_menu()
        
        # Detectar cuando el usuario pulsa la X de la ventana
        self.protocol("WM_DELETE_WINDOW", self.salir)

    def crear_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        # Menú Archivo
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo              Ctrl+N", command=self.nuevo_archivo)
        menu_archivo.add_command(label="Abrir...           Ctrl+O", command=self.abrir_archivo)
        menu_archivo.add_command(label="Guardar            Ctrl+S", command=self.guardar_archivo)
        menu_archivo.add_command(label="Guardar como...         ", command=self.guardar_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salir)

        # Atajos de teclado (funcionan en Windows, Linux y Mac)
        self.bind("<Control-n>", lambda e: self.nuevo_archivo())
        self.bind("<Control-o>", lambda e: self.abrir_archivo())
        self.bind("<Control-s>", lambda e: self.guardar_archivo())

    def texto_modificado(self, event=None):
        """Se llama cada vez que el usuario escribe o borra"""
        self.modificado = True
        self.actualizar_titulo()

    def actualizar_titulo(self):
        titulo = "BlockEditor"
        if self.archivo_actual:
            titulo += f" - {self.archivo_actual}"
        if self.modificado:
            titulo += " *"
        self.title(titulo)

    def nuevo_archivo(self):
        # 1. ¿Hay cambios sin guardar?
        if self.modificado:
            # Preguntamos al usuario qué quiere hacer
            respuesta = messagebox.askyesnocancel(
                "BlockEditor - Nuevo archivo",
                "¿Deseas guardar los cambios antes de crear un nuevo archivo?"
            )
            
            if respuesta is True:      # Sí → quiere guardar
                self.guardar_archivo()        # ← este método aún no existe, pero lo haremos después
                # Si el usuario cancela el guardado, no seguimos
                if self.modificado:           # ← sigue True = canceló el guardado
                    return
                    
            elif respuesta is False:   # No → descarta los cambios
                pass                       # simplemente seguimos
            else:                      # Cancelar (None)
                return                     # no hacemos nada y salimos
        
        # 2. Si llegamos aquí → podemos crear el archivo nuevo
        self.texto.delete("1.0", tk.END)    # borra todo el texto
        self.archivo_actual = None          # ya no hay archivo abierto
        self.modificado = False             # no hay cambios sin guardar
        self.actualizar_titulo()            # quita el * y pone "Sin título"

    
    def abrir_archivo(self):
        # 1. ¿Hay cambios sin guardar? preguntamos igual que en nuevo
        if self.modificado:
            respuesta = messagebox.askyesnocancel(
                "BlockEditor - Abrir archivo",
                "¿Deseas guardar los cambios antes de abrir otro archivo?"
            )
            if respuesta is True:           # Sí, guardar
                self.guardar_archivo()
                if self.modificado:         # canceló el guardado, no seguimos
                    return
            elif respuesta is None:         # Cancelar
                return
            # Si dijo "No", simplemente seguimos (descarta cambios)

        # 2. Abrir el diálogo para elegir archivo
        ruta = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos Python", "*.py"),
                ("Todos los archivos", "*.*")
            ]
        )

        # 3. Si el usuario canceló el diálogo no hacemos nada
        if not ruta:
            return

        try:
            # 4. Leer el archivo (usamos utf-8 para que funcione con acentos, ñ, etc.)
            with open(ruta, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()

            # 5. Cargar el contenido en el área de texto
            self.texto.delete("1.0", tk.END)      # borrar lo que había
            self.texto.insert("1.0", contenido)   # insertar el nuevo texto

            # 6. Actualizar estado de la aplicación
            self.archivo_actual = ruta
            self.modificado = False
            self.actualizar_titulo()

        except Exception as e:
            # 7. Si hay cualquier error (permiso, archivo dañado, etc.)
            messagebox.showerror("Error al abrir", f"No se pudo abrir el archivo:\n{e}")


    def guardar_archivo(self):
        # Caso 1: Ya tiene nombre → guardar directamente
        if self.archivo_actual:
            try:
                contenido = self.texto.get("1.0", tk.END + "-1c")  # todo menos el \n final
                with open(self.archivo_actual, "w", encoding="utf-8") as archivo:
                    archivo.write(contenido)
                
                self.modificado = False
                self.actualizar_titulo()
            
                # Mensaje de guardado correcto
                self.mostrar_mensaje_temporal("Guardado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")
            return

        # Caso 2: Es un archivo nuevo (sin nombre) → delegamos a "Guardar como"
        self.guardar_como()

    def guardar_como(self):
        # Siempre pregunta nombre y ubicación
        ruta = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".txt",
            filetypes=[
                ("Archivo de texto", "*.txt"),
                ("Archivo Python", "*.py"),
                ("Todos los archivos", "*.*")
            ]
        )

        # Si el usuario cancela → no hacemos nada
        if not ruta:
            return

        try:
            contenido = self.texto.get("1.0", tk.END + "-1c")  # quita el salto de línea final
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            
            # ¡Éxito! Actualizamos todo
            self.archivo_actual = ruta
            self.modificado = False
            self.actualizar_titulo()
            self.mostrar_mensaje_temporal("Guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo crear el archivo:\n{e}")

    def mostrar_mensaje_temporal(self, texto, color="#2ecc71", tiempo=3000):
        """Muestra un mensaje en la barra de estado y lo borra después"""
        self.label_status.config(text=texto, fg=color)
        # Cancelamos cualquier mensaje anterior por si acaso
        if hasattr(self, "mensaje_id"):
            self.after_cancel(self.mensaje_id)
        # Programamos el regreso a "Listo"
        self.mensaje_id = self.after(tiempo, lambda: self.label_status.config(text=" Listo", fg="#bdc3c7"))

    def salir(self):
        # Si hay cambios sin guardar → preguntamos
        if self.modificado:
            respuesta = messagebox.askyesnocancel(
                "BlockEditor - Salir",
                "¿Deseas guardar los cambios antes de cerrar?"
            )
            
            if respuesta is True:      # Sí → guardar
                self.guardar_archivo()
                # Si después de intentar guardar sigue modificado = canceló el guardado
                if self.modificado:
                    return             # no cerramos
            elif respuesta is None:    # Cancelar
                return                 # no cerramos
            # Si dijo "No" → simplemente seguimos y cerramos

        # Si llegamos aquí → podemos cerrar sin miedo
        self.destroy()   # cierra la ventana y termina el programa

if __name__ == "__main__":
    app = BlockEditor()
    app.mainloop()