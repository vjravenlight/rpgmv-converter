#!/usr/bin/env python3
"""
RPGMV Converter
Encripta y desencripta imágenes y audio de RPG Maker MV/MZ
by Karl Ravenlight
"""

# ============================================================================
# IMPORTS // Librerias necesarias para el funcionamiento
# ============================================================================

import os
import sys
import threading
import queue
import webbrowser
from pathlib import Path
from typing import Optional, Callable
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import io
import time

# ============================================================================
# CONSTANTES // Valores fijos usados en toda la aplicacion
# ============================================================================

VERSION = "1.2.0"
RPGMV_HEADER = b'RPGMV\x00\x00\x00\x00\x03\x01\x00\x00\x00\x00\x00'

# ============================================================================
# SISTEMA DE IDIOMAS // Traducciones ES/EN para toda la interfaz
# ============================================================================

LANGUAGES = {
    'es': {
        'name': 'Español',
        'flag': '🇪🇸',
        # UI General
        'title': 'RPGMV Converter',
        'ready': 'Listo',
        'completed': 'Completado',
        'files': 'archivos',
        'file': 'archivo',
        # Tabs
        'tab_png': '  PNG  ',
        'tab_ogg': '  OGG  ',
        'tab_about': '  ACERCA DE  ',
        # File Panel
        'images_png': 'IMAGENES (PNG)',
        'audio_ogg': 'AUDIO (OGG)',
        'preview': 'PREVIEW',
        'options': 'OPCIONES',
        'preserve_structure': 'Preservar estructura',
        'select_files': 'Archivos',
        'select_folder': 'Carpeta',
        'clear': 'Limpiar',
        'slideshow': 'Slideshow',
        'decrypt': 'DESENCRIPTAR',
        'encrypt': 'ENCRIPTAR',
        'drop_zone': 'Arrastra archivos o haz clic para seleccionar',
        'select_image': 'Selecciona una imagen\n\nDoble-click para slideshow',
        'audio_no_preview': '🎵 Audio\nSin preview disponible\n\nSelecciona archivos y usa\nDESENCRIPTAR para exportar',
        'no_files': 'No hay archivos para procesar',
        'no_slideshow_files': 'No hay archivos cargados',
        'key_loaded': 'Clave cargada desde JSON',
        'key_detected': 'Clave detectada automaticamente',
        'key_not_found': "No se encontro 'encryptionKey' en el archivo",
        'using_key': 'Usando clave',
        'folder': 'Carpeta',
        'added_files': 'Agregados {0} archivos',
        'completed_stats': 'Completado: {0} OK, {1} errores',
        'select_output': 'Seleccionar carpeta de salida',
        'select_json': 'Seleccionar System.json',
        'error_json': 'Error al leer JSON',
        # Slideshow
        'slideshow_title': 'Slideshow - RPGMV Converter',
        'slideshow_files': 'ARCHIVOS',
        'slideshow_prev': '< PREV',
        'slideshow_next': 'NEXT >',
        'slideshow_close': 'CERRAR',
        'slideshow_help1': 'Click izq: siguiente | Click der: anterior',
        'slideshow_help2': 'Flechas / Espacio: navegar | ESC: cerrar',
        'slideshow_no_images': 'No hay imagenes para mostrar',
        'slideshow_error': 'Error al cargar imagen',
        # About
        'about_made_for': '[ HECHO ESPECIFICAMENTE PARA ]',
        'about_game_desc': 'Un juego de RPG Maker MV',
        'about_coded_by': 'CODED BY',
        'about_protection': 'PROTECTION',
        'about_status': 'STATUS',
        'about_release': 'RELEASE',
        'about_working': '100% Working',
        'about_links': '>> LINKS',
        'about_compat_title': '[!] COMPATIBILIDAD:',
        'about_compat1': '    Este programa funciona con CUALQUIER',
        'about_compat2': '    juego de RPG Maker MV/MZ que use',
        'about_compat3': '    encriptacion RPGMV estandar.',
        'about_quote': '"Breaking barriers between creators and their assets"',
        'about_greets': '═══════════[ GREETS TO ALL RPGMAKER DEVS ]═══════════',
        # Status bar
        'status_by': 'by Karl Ravenlight',
    },
    'en': {
        'name': 'English',
        'flag': '🇺🇸',
        # UI General
        'title': 'RPGMV Converter',
        'ready': 'Ready',
        'completed': 'Completed',
        'files': 'files',
        'file': 'file',
        # Tabs
        'tab_png': '  PNG  ',
        'tab_ogg': '  OGG  ',
        'tab_about': '  ABOUT  ',
        # File Panel
        'images_png': 'IMAGES (PNG)',
        'audio_ogg': 'AUDIO (OGG)',
        'preview': 'PREVIEW',
        'options': 'OPTIONS',
        'preserve_structure': 'Preserve structure',
        'select_files': 'Files',
        'select_folder': 'Folder',
        'clear': 'Clear',
        'slideshow': 'Slideshow',
        'decrypt': 'DECRYPT',
        'encrypt': 'ENCRYPT',
        'drop_zone': 'Drag files or click to select',
        'select_image': 'Select an image\n\nDouble-click for slideshow',
        'audio_no_preview': '🎵 Audio\nNo preview available\n\nSelect files and use\nDECRYPT to export',
        'no_files': 'No files to process',
        'no_slideshow_files': 'No files loaded',
        'key_loaded': 'Key loaded from JSON',
        'key_detected': 'Key detected automatically',
        'key_not_found': "'encryptionKey' not found in file",
        'using_key': 'Using key',
        'folder': 'Folder',
        'added_files': 'Added {0} files',
        'completed_stats': 'Completed: {0} OK, {1} errors',
        'select_output': 'Select output folder',
        'select_json': 'Select System.json',
        'error_json': 'Error reading JSON',
        # Slideshow
        'slideshow_title': 'Slideshow - RPGMV Converter',
        'slideshow_files': 'FILES',
        'slideshow_prev': '< PREV',
        'slideshow_next': 'NEXT >',
        'slideshow_close': 'CLOSE',
        'slideshow_help1': 'Left click: next | Right click: previous',
        'slideshow_help2': 'Arrows / Space: navigate | ESC: close',
        'slideshow_no_images': 'No images to display',
        'slideshow_error': 'Error loading image',
        # About
        'about_made_for': '[ MADE SPECIFICALLY FOR ]',
        'about_game_desc': 'An RPG Maker MV game',
        'about_coded_by': 'CODED BY',
        'about_protection': 'PROTECTION',
        'about_status': 'STATUS',
        'about_release': 'RELEASE',
        'about_working': '100% Working',
        'about_links': '>> LINKS',
        'about_compat_title': '[!] COMPATIBILITY:',
        'about_compat1': '    This program works with ANY',
        'about_compat2': '    RPG Maker MV/MZ game using',
        'about_compat3': '    standard RPGMV encryption.',
        'about_quote': '"Breaking barriers between creators and their assets"',
        'about_greets': '═══════════[ GREETS TO ALL RPGMAKER DEVS ]═══════════',
        # Status bar
        'status_by': 'by Karl Ravenlight',
    }
}

# Idioma actual (por defecto español)
current_language = 'es'

def t(key: str) -> str:
    """Obtiene el texto traducido para la clave dada"""
    return LANGUAGES.get(current_language, LANGUAGES['es']).get(key, key)
RPGMV_HEADER_SIZE = 16

PNG_HEADER = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52
])

PNG_EXTENSIONS_ENC = {'.png_', '.rpgmvp'}
PNG_EXTENSIONS_DEC = {'.png'}
OGG_EXTENSIONS_ENC = {'.ogg_', '.rpgmvo'}
OGG_EXTENSIONS_DEC = {'.ogg'}

EXT_MAP_DECRYPT = {
    '.png_': '.png', '.rpgmvp': '.png',
    '.ogg_': '.ogg', '.rpgmvo': '.ogg',
}

EXT_MAP_ENCRYPT = {'.png': '.png_', '.ogg': '.ogg_'}

FILE_HEADERS = {
    '.png': PNG_HEADER,
    '.ogg': bytes([0x4F, 0x67, 0x67, 0x53, 0x00, 0x02, 0x00, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
}

# ============================================================================
# FUNCIONES DE ENCRIPTACIÓN/DESENCRIPTACIÓN // Logica XOR para archivos RPGMV
# ============================================================================

def is_rpgmv_encrypted(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            return f.read(5) == b'RPGMV'
    except:
        return False

def find_encryption_key(folder_path: str) -> Optional[bytes]:
    """Busca la clave de encriptacion en System.json del juego"""
    import json

    # Buscar System.json en varias ubicaciones posibles
    possible_paths = [
        Path(folder_path) / 'data' / 'System.json',
        Path(folder_path) / 'www' / 'data' / 'System.json',
        Path(folder_path).parent / 'data' / 'System.json',
        Path(folder_path).parent.parent / 'data' / 'System.json',
    ]

    for system_path in possible_paths:
        if system_path.exists():
            try:
                with open(system_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'encryptionKey' in data:
                    key_hex = data['encryptionKey']
                    return bytes.fromhex(key_hex)
            except:
                continue
    return None

def derive_key(encrypted_header: bytes, file_type: str = '.png') -> bytes:
    """Deriva la clave XOR del header encriptado (metodo fallback)"""
    known_header = FILE_HEADERS.get(file_type, PNG_HEADER)
    return bytes([encrypted_header[i] ^ known_header[i] for i in range(min(16, len(encrypted_header)))])

def decrypt_file(input_path: str, output_path: Optional[str] = None,
                 encryption_key: Optional[bytes] = None) -> tuple[bool, str]:
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        if not data.startswith(b'RPGMV'):
            return False, "No es archivo RPGMV"
        ext = Path(input_path).suffix.lower()
        target_ext = EXT_MAP_DECRYPT.get(ext, '.png')

        # Usar clave proporcionada o derivar del header (fallback para PNG)
        if encryption_key is None:
            encrypted_header = data[RPGMV_HEADER_SIZE:RPGMV_HEADER_SIZE + 16]
            key = derive_key(encrypted_header, target_ext)
        else:
            key = encryption_key

        decrypted = bytearray()
        for i in range(16):
            decrypted.append(data[RPGMV_HEADER_SIZE + i] ^ key[i])
        decrypted.extend(data[RPGMV_HEADER_SIZE + 16:])
        if output_path is None:
            output_path = str(Path(input_path).with_suffix(target_ext))
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        return True, output_path
    except Exception as e:
        return False, str(e)

def encrypt_file(input_path: str, output_path: Optional[str] = None,
                 encryption_key: Optional[bytes] = None) -> tuple[bool, str]:
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        ext = Path(input_path).suffix.lower()
        target_ext = EXT_MAP_ENCRYPT.get(ext, '.png_')
        if encryption_key is None:
            encryption_key = bytes([0xd4, 0x1d, 0x8c, 0xd9, 0x8f, 0x00, 0xb2, 0x04,
                                    0xe9, 0x80, 0x09, 0x98, 0xec, 0xf8, 0x42, 0x7e])
        encrypted = bytearray(RPGMV_HEADER)
        for i in range(min(16, len(data))):
            encrypted.append(data[i] ^ encryption_key[i])
        encrypted.extend(data[16:])
        if output_path is None:
            output_path = str(Path(input_path).with_suffix(target_ext))
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        return True, output_path
    except Exception as e:
        return False, str(e)

def get_image_preview(file_path: str, max_size: tuple = (400, 400)) -> Optional[Image.Image]:
    try:
        if is_rpgmv_encrypted(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            encrypted_header = data[RPGMV_HEADER_SIZE:RPGMV_HEADER_SIZE + 16]
            key = derive_key(encrypted_header, '.png')
            decrypted = bytearray()
            for i in range(16):
                decrypted.append(data[RPGMV_HEADER_SIZE + i] ^ key[i])
            decrypted.extend(data[RPGMV_HEADER_SIZE + 16:])
            img = Image.open(io.BytesIO(bytes(decrypted)))
        else:
            img = Image.open(file_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    except:
        return None

def get_full_image(file_path: str) -> Optional[Image.Image]:
    """Obtiene imagen completa sin redimensionar"""
    try:
        if is_rpgmv_encrypted(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            encrypted_header = data[RPGMV_HEADER_SIZE:RPGMV_HEADER_SIZE + 16]
            key = derive_key(encrypted_header, '.png')
            decrypted = bytearray()
            for i in range(16):
                decrypted.append(data[RPGMV_HEADER_SIZE + i] ^ key[i])
            decrypted.extend(data[RPGMV_HEADER_SIZE + 16:])
            return Image.open(io.BytesIO(bytes(decrypted)))
        else:
            return Image.open(file_path)
    except:
        return None

# ============================================================================
# TEMA Y COLORES // Paleta de colores para la interfaz oscura
# ============================================================================

COLORS = {
    'bg_dark': '#0d1117',
    'bg_main': '#161b22',
    'bg_card': '#21262d',
    'bg_input': '#0d1117',
    'accent': '#e94560',
    'accent_hover': '#ff6b6b',
    'accent_green': '#00ff41',
    'accent_cyan': '#00d4ff',
    'accent_pink': '#ff00ff',
    'accent_orange': '#ff9500',
    'text': '#f0f6fc',
    'text_dim': '#8b949e',
    'border': '#30363d',
    'success': '#3fb950',
    'error': '#f85149'
}

# ============================================================================
# SLIDESHOW WINDOW // Ventana fullscreen para ver imagenes con navegacion
# ============================================================================

class SlideshowWindow:
    def __init__(self, parent, files, start_index=0):
        self.parent = parent
        self.files = [f for f in files if Path(f).suffix.lower() in {'.png', '.png_', '.rpgmvp'}]
        self.current_index = min(start_index, len(self.files) - 1) if self.files else 0
        self.image = None
        self.photo = None

        if not self.files:
            messagebox.showwarning("Slideshow", "No hay imagenes para mostrar")
            return

        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Slideshow - RPGMV Converter")
        self.window.geometry("1200x800")
        self.window.configure(bg='#000000')
        self.window.state('zoomed')  # Maximized

        self.create_ui()
        self.bind_keys()
        self.show_image()

    def create_ui(self):
        # Main layout
        main = tk.Frame(self.window, bg='#000000')
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.rowconfigure(0, weight=1)

        # Image area
        self.canvas_frame = tk.Frame(main, bg='#000000')
        self.canvas_frame.grid(row=0, column=0, sticky='nsew')

        self.canvas = tk.Canvas(self.canvas_frame, bg='#000000', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self.on_resize)
        self.canvas.bind('<Button-1>', lambda e: self.next_image())
        self.canvas.bind('<Button-3>', lambda e: self.prev_image())

        # Sidebar
        sidebar = tk.Frame(main, bg=COLORS['bg_card'], width=280)
        sidebar.grid(row=0, column=1, sticky='nsew')
        sidebar.grid_propagate(False)

        # Sidebar header
        header = tk.Frame(sidebar, bg=COLORS['bg_card'])
        header.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(header, text="ARCHIVOS", font=('Consolas', 11, 'bold'),
                bg=COLORS['bg_card'], fg=COLORS['accent']).pack(anchor='w')

        self.counter_label = tk.Label(header, text="",
                                      font=('Consolas', 9),
                                      bg=COLORS['bg_card'], fg=COLORS['text_dim'])
        self.counter_label.pack(anchor='w')

        # File list
        list_frame = tk.Frame(sidebar, bg=COLORS['bg_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(list_frame,
                                       bg=COLORS['bg_input'], fg=COLORS['text'],
                                       font=('Consolas', 9),
                                       selectbackground=COLORS['accent'],
                                       selectforeground='white',
                                       borderwidth=0, highlightthickness=0,
                                       yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        for f in self.files:
            self.file_listbox.insert(tk.END, Path(f).name)

        self.file_listbox.bind('<<ListboxSelect>>', self.on_list_select)

        # Controls
        controls = tk.Frame(sidebar, bg=COLORS['bg_card'])
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        btn_frame = tk.Frame(controls, bg=COLORS['bg_card'])
        btn_frame.pack(fill=tk.X)

        self.prev_btn = tk.Button(btn_frame, text="< PREV", command=self.prev_image,
                                  font=('Consolas', 10, 'bold'),
                                  bg=COLORS['accent'], fg='white',
                                  activebackground=COLORS['accent_hover'],
                                  relief='flat', cursor='hand2', padx=15, pady=8)
        self.prev_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.next_btn = tk.Button(btn_frame, text="NEXT >", command=self.next_image,
                                  font=('Consolas', 10, 'bold'),
                                  bg=COLORS['accent'], fg='white',
                                  activebackground=COLORS['accent_hover'],
                                  relief='flat', cursor='hand2', padx=15, pady=8)
        self.next_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        # Info
        tk.Label(controls, text="Click izq: siguiente | Click der: anterior",
                font=('Consolas', 8), bg=COLORS['bg_card'],
                fg=COLORS['text_dim']).pack(pady=(10, 0))
        tk.Label(controls, text="Flechas / Espacio: navegar | ESC: cerrar",
                font=('Consolas', 8), bg=COLORS['bg_card'],
                fg=COLORS['text_dim']).pack()

        # Close button
        tk.Button(controls, text="CERRAR", command=self.window.destroy,
                 font=('Consolas', 10), bg=COLORS['error'], fg='white',
                 activebackground='#ff0000', relief='flat',
                 cursor='hand2', pady=8).pack(fill=tk.X, pady=(15, 0))

    def bind_keys(self):
        self.window.bind('<Left>', lambda e: self.prev_image())
        self.window.bind('<Right>', lambda e: self.next_image())
        self.window.bind('<Up>', lambda e: self.prev_image())
        self.window.bind('<Down>', lambda e: self.next_image())
        self.window.bind('<space>', lambda e: self.next_image())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.window.bind('<Home>', lambda e: self.go_to(0))
        self.window.bind('<End>', lambda e: self.go_to(len(self.files) - 1))

    def on_resize(self, event):
        self.show_image()

    def on_list_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.show_image()

    def show_image(self):
        if not self.files:
            return

        self.canvas.delete("all")
        file_path = self.files[self.current_index]

        # Update list selection
        self.file_listbox.selection_clear(0, tk.END)
        self.file_listbox.selection_set(self.current_index)
        self.file_listbox.see(self.current_index)

        # Update counter
        self.counter_label.config(text=f"{self.current_index + 1} / {len(self.files)}")

        # Load image
        img = get_full_image(file_path)
        if img is None:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="Error al cargar imagen",
                fill=COLORS['error'], font=('Consolas', 14))
            return

        # Scale to fit canvas
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            return

        img_w, img_h = img.size
        scale = min(canvas_w / img_w, canvas_h / img_h, 1.0)

        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        if new_w > 0 and new_h > 0:
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(canvas_w // 2, canvas_h // 2, image=self.photo)

        # File info
        self.window.title(f"Slideshow - {Path(file_path).name}")

    def next_image(self):
        if self.files:
            self.current_index = (self.current_index + 1) % len(self.files)
            self.show_image()

    def prev_image(self):
        if self.files:
            self.current_index = (self.current_index - 1) % len(self.files)
            self.show_image()

    def go_to(self, index):
        if self.files:
            self.current_index = max(0, min(index, len(self.files) - 1))
            self.show_image()


# ============================================================================
# FILE PANEL // Panel reutilizable para manejar archivos PNG y OGG
# ============================================================================

class FilePanel:
    def __init__(self, parent, app, file_type='png'):
        self.parent = parent
        self.app = app
        self.file_type = file_type
        self.files = []
        self.base_directory = None
        self.current_preview_path = None
        self.preview_image = None
        self.encryption_key = None  # Clave detectada de System.json

        if file_type == 'png':
            self.extensions_enc = PNG_EXTENSIONS_ENC
            self.extensions_dec = PNG_EXTENSIONS_DEC
            self.color = COLORS['accent']
        else:
            self.extensions_enc = OGG_EXTENSIONS_ENC
            self.extensions_dec = OGG_EXTENSIONS_DEC
            self.color = COLORS['accent_orange']

        self.create_ui()

    def create_ui(self):
        # Main layout
        content = tk.Frame(self.parent, bg=COLORS['bg_main'])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        # Left - Files
        left = self.create_files_section(content)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

        # Right - Preview/Options
        right = tk.Frame(content, bg=COLORS['bg_main'])
        right.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.create_preview_section(right)
        self.create_options_section(right)

        # Bottom - Actions
        self.create_actions_section(self.parent)

    def create_files_section(self, parent):
        frame = tk.Frame(parent, bg=COLORS['bg_card'], highlightbackground=COLORS['border'],
                        highlightthickness=1)

        # Header
        header = tk.Frame(frame, bg=COLORS['bg_card'])
        header.pack(fill=tk.X, padx=15, pady=(15, 10))

        title = t('images_png') if self.file_type == 'png' else t('audio_ogg')
        tk.Label(header, text=title, font=('Segoe UI', 11, 'bold'),
                bg=COLORS['bg_card'], fg=self.color).pack(side=tk.LEFT)

        self.file_count_label = tk.Label(header, text=f"0 {t('files')}",
                                         font=('Consolas', 9),
                                         bg=COLORS['bg_card'], fg=COLORS['text_dim'])
        self.file_count_label.pack(side=tk.RIGHT)

        # Drop zone
        drop_zone = tk.Frame(frame, bg=COLORS['bg_input'], height=70,
                            highlightbackground=COLORS['border'], highlightthickness=1)
        drop_zone.pack(fill=tk.X, padx=15, pady=(0, 10))
        drop_zone.pack_propagate(False)

        self.drop_label = tk.Label(drop_zone, text=t('drop_zone'),
                                   font=('Segoe UI', 10),
                                   bg=COLORS['bg_input'], fg=COLORS['text_dim'],
                                   cursor='hand2')
        self.drop_label.pack(expand=True)
        self.drop_label.bind('<Button-1>', lambda e: self.select_files())
        drop_zone.bind('<Button-1>', lambda e: self.select_files())

        # File list
        list_frame = tk.Frame(frame, bg=COLORS['bg_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(list_frame,
                                       bg=COLORS['bg_input'], fg=COLORS['text'],
                                       font=('Consolas', 9),
                                       selectbackground=self.color,
                                       selectforeground='white',
                                       borderwidth=0, highlightthickness=0,
                                       yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        scrollbar.config(command=self.file_listbox.yview)

        # Buttons
        btn_frame = tk.Frame(frame, bg=COLORS['bg_card'])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.create_btn(btn_frame, t('select_files'), self.select_files).pack(side=tk.LEFT, padx=(0, 5))
        self.create_btn(btn_frame, t('select_folder'), self.select_folder).pack(side=tk.LEFT, padx=(0, 5))
        self.create_btn(btn_frame, t('clear'), self.clear_files, danger=True).pack(side=tk.RIGHT)

        # Slideshow button (only for PNG)
        if self.file_type == 'png':
            self.create_btn(btn_frame, t('slideshow'), self.open_slideshow,
                           color=COLORS['accent_cyan']).pack(side=tk.RIGHT, padx=(0, 5))

        return frame

    def create_preview_section(self, parent):
        frame = tk.Frame(parent, bg=COLORS['bg_card'], highlightbackground=COLORS['border'],
                        highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Header
        header = tk.Frame(frame, bg=COLORS['bg_card'])
        header.pack(fill=tk.X, padx=15, pady=(15, 10))

        tk.Label(header, text=t('preview'), font=('Segoe UI', 11, 'bold'),
                bg=COLORS['bg_card'], fg=COLORS['text']).pack(side=tk.LEFT)

        # Slideshow button in preview header (only for PNG)
        if self.file_type == 'png':
            self.slideshow_btn = tk.Button(header, text=f"⛶ {t('slideshow').upper()}", command=self.open_slideshow,
                                           font=('Segoe UI', 9, 'bold'),
                                           bg=COLORS['accent_cyan'], fg='white',
                                           activebackground=COLORS['accent'],
                                           relief='flat', cursor='hand2', padx=12, pady=3)
            self.slideshow_btn.pack(side=tk.RIGHT, padx=(10, 0))

        self.file_info_label = tk.Label(header, text="",
                                        font=('Consolas', 9),
                                        bg=COLORS['bg_card'], fg=COLORS['text_dim'])
        self.file_info_label.pack(side=tk.RIGHT)

        # Canvas
        canvas_frame = tk.Frame(frame, bg=COLORS['bg_input'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.preview_canvas = tk.Canvas(canvas_frame, bg=COLORS['bg_input'], highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.bind('<Configure>', self.on_canvas_resize)

        if self.file_type == 'png':
            placeholder = t('select_image')
            # Make canvas clickable for slideshow
            self.preview_canvas.bind('<Double-Button-1>', lambda e: self.open_slideshow())
        else:
            placeholder = t('audio_no_preview')

        self.preview_canvas.create_text(200, 150, text=placeholder,
                                        fill=COLORS['text_dim'], font=('Segoe UI', 11),
                                        justify='center', tags='placeholder')

    def create_options_section(self, parent):
        frame = tk.Frame(parent, bg=COLORS['bg_card'], highlightbackground=COLORS['border'],
                        highlightthickness=1)
        frame.pack(fill=tk.X)

        # Header con titulo
        header = tk.Frame(frame, bg=COLORS['bg_card'])
        header.pack(fill=tk.X, padx=10, pady=(10, 8))

        tk.Label(header, text=t('options'), font=('Segoe UI', 10, 'bold'),
                bg=COLORS['bg_card'], fg=COLORS['text']).pack(side=tk.LEFT)

        # Preserve structure checkbox en el header
        self.preserve_var = tk.BooleanVar(value=True)
        tk.Checkbutton(header, text=t('preserve_structure'),
                      variable=self.preserve_var,
                      font=('Segoe UI', 8), bg=COLORS['bg_card'], fg=COLORS['text_dim'],
                      selectcolor=COLORS['bg_input'], activebackground=COLORS['bg_card'],
                      activeforeground=COLORS['text']).pack(side=tk.RIGHT)

        # Encryption Key - en una sola linea compacta
        key_frame = tk.Frame(frame, bg=COLORS['bg_card'])
        key_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(key_frame, text="Key:", font=('Consolas', 9),
                bg=COLORS['bg_card'], fg=COLORS['text_dim'], width=4).pack(side=tk.LEFT)

        self.key_var = tk.StringVar()
        self.key_entry = tk.Entry(key_frame, textvariable=self.key_var,
                                  font=('Consolas', 8), bg=COLORS['bg_input'],
                                  fg=COLORS['accent_cyan'], insertbackground=COLORS['text'],
                                  relief='flat', highlightthickness=1,
                                  highlightbackground=COLORS['border'],
                                  highlightcolor=self.color)
        self.key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.key_status_label = tk.Label(key_frame, text="--",
                                         font=('Consolas', 8), width=6,
                                         bg=COLORS['bg_card'], fg=COLORS['text_dim'])
        self.key_status_label.pack(side=tk.LEFT, padx=(0, 5))

        self.create_btn(key_frame, "JSON", self.load_key_from_json,
                       color=COLORS['accent_cyan']).pack(side=tk.RIGHT)

        # Output folder - en una sola linea
        out_frame = tk.Frame(frame, bg=COLORS['bg_card'])
        out_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(out_frame, text="Out:", font=('Consolas', 9),
                bg=COLORS['bg_card'], fg=COLORS['text_dim'], width=4).pack(side=tk.LEFT)

        self.output_var = tk.StringVar()
        self.output_entry = tk.Entry(out_frame, textvariable=self.output_var,
                                     font=('Consolas', 8), bg=COLORS['bg_input'],
                                     fg=COLORS['text'], insertbackground=COLORS['text'],
                                     relief='flat', highlightthickness=1,
                                     highlightbackground=COLORS['border'],
                                     highlightcolor=self.color)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.create_btn(out_frame, "...", self.select_output_folder, width=3).pack(side=tk.RIGHT)

    def create_actions_section(self, parent):
        frame = tk.Frame(parent, bg=COLORS['bg_main'])
        frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Progress
        progress_frame = tk.Frame(frame, bg=COLORS['bg_main'])
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style_name = f'Custom{self.file_type}.Horizontal.TProgressbar'
        style.configure(style_name,
                       background=self.color,
                       troughcolor=COLORS['bg_card'])

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, style=style_name)
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.progress_label = tk.Label(progress_frame, text=t('ready'), width=15,
                                       font=('Consolas', 9), bg=COLORS['bg_main'],
                                       fg=COLORS['text_dim'])
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Buttons + Log
        bottom = tk.Frame(frame, bg=COLORS['bg_main'])
        bottom.pack(fill=tk.X)

        btn_frame = tk.Frame(bottom, bg=COLORS['bg_main'])
        btn_frame.pack(side=tk.LEFT)

        self.decrypt_btn = tk.Button(btn_frame, text=t('decrypt'), command=self.start_decrypt,
                                     font=('Segoe UI', 11, 'bold'), bg=self.color, fg='white',
                                     activebackground=COLORS['accent_hover'],
                                     relief='flat', cursor='hand2', padx=25, pady=10)
        self.decrypt_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.encrypt_btn = tk.Button(btn_frame, text=t('encrypt'), command=self.start_encrypt,
                                     font=('Segoe UI', 11, 'bold'), bg=self.color, fg='white',
                                     activebackground=COLORS['accent_hover'],
                                     relief='flat', cursor='hand2', padx=25, pady=10)
        self.encrypt_btn.pack(side=tk.LEFT)

        # Log
        self.log_text = tk.Text(bottom, height=3, font=('Consolas', 9),
                               bg=COLORS['bg_card'], fg=COLORS['text_dim'],
                               relief='flat', highlightthickness=1,
                               highlightbackground=COLORS['border'])
        self.log_text.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(15, 0))
        self.log_text.config(state=tk.DISABLED)

    # Helpers
    def create_btn(self, parent, text, command, danger=False, color=None, width=None):
        if color:
            bg = color
            fg = 'white'
        elif danger:
            bg = COLORS['error']
            fg = 'white'
        else:
            bg = COLORS['bg_input']
            fg = COLORS['text']
        btn = tk.Button(parent, text=text, command=command,
                       font=('Segoe UI', 9), bg=bg, fg=fg,
                       activebackground=COLORS['border'], activeforeground=COLORS['text'],
                       relief='flat', cursor='hand2', padx=12, pady=5, width=width)
        return btn

    def log(self, message: str, level: str = 'info'):
        self.log_text.config(state=tk.NORMAL)
        prefix = {'info': '>', 'success': '+', 'error': '!'}.get(level, '>')
        self.log_text.insert(tk.END, f"[{prefix}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_key_display(self, key: Optional[bytes], source: str = ""):
        """Actualiza el campo de clave y el estado"""
        if key:
            self.key_var.set(key.hex())
            self.encryption_key = key
            self.key_status_label.config(text="OK", fg=COLORS['success'])
        else:
            self.key_var.set("")
            self.encryption_key = None
            self.key_status_label.config(text="--", fg=COLORS['text_dim'])

    def load_key_from_json(self):
        """Carga la clave desde un archivo System.json seleccionado manualmente"""
        import json
        file_path = filedialog.askopenfilename(
            title="Seleccionar System.json",
            filetypes=[("System JSON", "System.json"), ("JSON files", "*.json"), ("Todos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'encryptionKey' in data:
                    key_hex = data['encryptionKey']
                    key = bytes.fromhex(key_hex)
                    self.update_key_display(key, "System.json")
                    self.log(f"Clave cargada desde JSON", 'success')
                else:
                    messagebox.showwarning("Aviso", "No se encontro 'encryptionKey' en el archivo")
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer JSON: {e}")

    def get_current_key(self) -> Optional[bytes]:
        """Obtiene la clave actual (del campo o detectada)"""
        key_hex = self.key_var.get().strip()
        if key_hex:
            try:
                return bytes.fromhex(key_hex)
            except:
                pass
        return self.encryption_key

    # File operations
    def select_files(self):
        if self.file_type == 'png':
            filetypes = [("Imagenes RPGMV", "*.png_ *.rpgmvp *.png"), ("Todos", "*.*")]
        else:
            filetypes = [("Audio RPGMV", "*.ogg_ *.rpgmvo *.ogg"), ("Todos", "*.*")]

        files = filedialog.askopenfilenames(title="Seleccionar archivos", filetypes=filetypes)
        if files:
            self.add_files(files)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            self.add_folder(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_var.set(folder)

    def add_files(self, files):
        for file in files:
            ext = Path(file).suffix.lower()
            valid_exts = self.extensions_enc | self.extensions_dec
            if ext in valid_exts and file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(tk.END, Path(file).name)
        self.update_count()

    def add_folder(self, folder):
        folder_path = Path(folder)
        self.base_directory = str(folder_path)

        # Buscar clave de encriptacion en System.json
        key = find_encryption_key(folder)
        if key:
            self.update_key_display(key, "Auto")
            self.log(f"Clave detectada automaticamente", 'success')
        else:
            # No limpiar si ya hay una clave cargada manualmente
            if not self.key_var.get():
                self.update_key_display(None, "")

        extensions = list(self.extensions_enc) + list(self.extensions_dec)
        count = 0
        for ext in extensions:
            for file in folder_path.rglob(f"*{ext}"):
                if str(file) not in self.files:
                    self.files.append(str(file))
                    count += 1
                    try:
                        self.file_listbox.insert(tk.END, str(file.relative_to(folder_path)))
                    except:
                        self.file_listbox.insert(tk.END, file.name)
        self.update_count()
        self.log(f"{t('folder')}: {folder}")
        self.log(t('added_files').format(count))

    def clear_files(self):
        self.files.clear()
        self.base_directory = None
        self.file_listbox.delete(0, tk.END)
        self.update_count()
        self.preview_canvas.delete("all")
        self.file_info_label.config(text="")

    def update_count(self):
        count = len(self.files)
        word = t('file') if count == 1 else t('files')
        self.file_count_label.config(text=f"{count} {word}")

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        file_path = self.files[selection[0]]
        try:
            size = os.path.getsize(file_path)
            encrypted = "Enc" if is_rpgmv_encrypted(file_path) else "Dec"
            self.file_info_label.config(text=f"{Path(file_path).name} | {size:,}b | {encrypted}")
        except:
            pass
        self.update_preview(file_path)

    def on_canvas_resize(self, event):
        if self.current_preview_path:
            self.update_preview(self.current_preview_path)

    def update_preview(self, file_path: str):
        self.current_preview_path = file_path
        self.preview_canvas.delete("all")

        if self.file_type != 'png':
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                text="Archivo de audio\n(sin preview)",
                fill=COLORS['text_dim'], font=('Segoe UI', 11), justify='center')
            return

        def load():
            canvas_w = max(self.preview_canvas.winfo_width() - 20, 100)
            canvas_h = max(self.preview_canvas.winfo_height() - 20, 100)
            img = get_image_preview(file_path, (canvas_w, canvas_h))
            if img:
                self.app.task_queue.put(('preview', self, img))

        threading.Thread(target=load, daemon=True).start()

    def show_preview(self, img):
        self.preview_image = ImageTk.PhotoImage(img)
        self.preview_canvas.create_image(
            self.preview_canvas.winfo_width() // 2,
            self.preview_canvas.winfo_height() // 2,
            image=self.preview_image)

    def open_slideshow(self):
        if not self.files:
            messagebox.showwarning("Slideshow", t('no_slideshow_files'))
            return
        selection = self.file_listbox.curselection()
        start = selection[0] if selection else 0
        SlideshowWindow(self.app.root, self.files, start)

    # Processing
    def start_decrypt(self):
        if not self.files:
            messagebox.showwarning("Warning", t('no_files'))
            return
        # Usar clave del campo o detectada
        key = self.get_current_key()
        if key:
            self.log(f"{t('using_key')}: {key.hex()[:16]}...")
        self.start_processing(lambda f, o: decrypt_file(f, o, key), "decrypt")

    def start_encrypt(self):
        if not self.files:
            messagebox.showwarning("Warning", t('no_files'))
            return
        key = self.get_current_key()
        if key:
            self.log(f"{t('using_key')}: {key.hex()[:16]}...")
        self.start_processing(lambda f, o: encrypt_file(f, o, key), "encrypt")

    def start_processing(self, process_func, action):
        self.decrypt_btn.config(state=tk.DISABLED)
        self.encrypt_btn.config(state=tk.DISABLED)

        output_dir = self.output_var.get() or None
        files = self.files.copy()
        base_dir = self.base_directory
        preserve = self.preserve_var.get()

        def process():
            success, failed = 0, 0
            total = len(files)

            for i, file_path in enumerate(files):
                file_p = Path(file_path)
                ext = file_p.suffix.lower()

                if action == "decrypt":
                    new_ext = EXT_MAP_DECRYPT.get(ext, ext)
                else:
                    new_ext = EXT_MAP_ENCRYPT.get(ext, ext)

                if output_dir:
                    if preserve and base_dir:
                        try:
                            rel_path = file_p.relative_to(base_dir)
                            out_path = Path(output_dir) / rel_path
                            out_path = out_path.with_suffix(new_ext)
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                        except ValueError:
                            out_path = Path(output_dir) / file_p.name
                            out_path = out_path.with_suffix(new_ext)
                    else:
                        out_path = Path(output_dir) / file_p.name
                        out_path = out_path.with_suffix(new_ext)
                    out_path = str(out_path)
                else:
                    out_path = None

                ok, result = process_func(file_path, out_path)

                if ok:
                    success += 1
                else:
                    failed += 1
                    self.app.task_queue.put(('log', self, f"{file_p.name}: {result}", 'error'))

                self.app.task_queue.put(('progress', self, ((i + 1) / total) * 100, f"{i+1}/{total}"))

            self.app.task_queue.put(('log', self, t('completed_stats').format(success, failed), 'info'))
            self.app.task_queue.put(('progress', self, 100, t('completed')))
            self.app.task_queue.put(('done', self))

        threading.Thread(target=process, daemon=True).start()


# ============================================================================
# APLICACIÓN PRINCIPAL // Clase principal que crea la ventana y tabs
# ============================================================================

class RPGMVConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(t('title'))
        self.root.geometry("1200x800")
        self.root.minsize(1100, 700)
        self.root.configure(bg=COLORS['bg_dark'])

        self.task_queue = queue.Queue()

        self.setup_styles()
        self.create_ui()
        self.check_queue()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TNotebook', background=COLORS['bg_dark'], borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_dim'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', COLORS['bg_main'])],
                 foreground=[('selected', COLORS['text'])])

    def create_ui(self):
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        self.create_header(main)

        # Notebook
        self.notebook = ttk.Notebook(main, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 0))

        # Tab PNG
        png_tab = tk.Frame(self.notebook, bg=COLORS['bg_main'])
        self.notebook.add(png_tab, text=t('tab_png'))
        self.png_panel = FilePanel(png_tab, self, 'png')

        # Tab OGG
        ogg_tab = tk.Frame(self.notebook, bg=COLORS['bg_main'])
        self.notebook.add(ogg_tab, text=t('tab_ogg'))
        self.ogg_panel = FilePanel(ogg_tab, self, 'ogg')

        # Tab About
        about_tab = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(about_tab, text=t('tab_about'))
        self.create_about_tab(about_tab)

        # Status bar
        self.create_statusbar(main)

    def create_header(self, parent):
        header = tk.Frame(parent, bg=COLORS['bg_dark'])
        header.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Title
        title_frame = tk.Frame(header, bg=COLORS['bg_dark'])
        title_frame.pack(side=tk.LEFT)

        tk.Label(title_frame, text="RPGMV", font=('Consolas', 24, 'bold'),
                bg=COLORS['bg_dark'], fg=COLORS['accent']).pack(side=tk.LEFT)
        tk.Label(title_frame, text="CONVERTER", font=('Consolas', 24, 'bold'),
                bg=COLORS['bg_dark'], fg=COLORS['text']).pack(side=tk.LEFT, padx=(5, 0))

        # Version
        v_frame = tk.Frame(header, bg=COLORS['accent'], padx=6, pady=2)
        v_frame.pack(side=tk.LEFT, padx=(10, 0), pady=(5, 0))
        tk.Label(v_frame, text=f"v{VERSION}", font=('Consolas', 8, 'bold'),
                bg=COLORS['accent'], fg='white').pack()

        # Language selector (right side)
        lang_frame = tk.Frame(header, bg=COLORS['bg_dark'])
        lang_frame.pack(side=tk.RIGHT)

        self.lang_var = tk.StringVar(value=current_language)

        for lang_code in LANGUAGES:
            lang = LANGUAGES[lang_code]
            btn = tk.Button(lang_frame,
                           text=f"{lang['flag']} {lang['name']}",
                           font=('Segoe UI', 9),
                           bg=COLORS['bg_card'] if lang_code != current_language else COLORS['accent'],
                           fg=COLORS['text'],
                           activebackground=COLORS['accent'],
                           relief='flat', cursor='hand2', padx=10, pady=4,
                           command=lambda lc=lang_code: self.change_language(lc))
            btn.pack(side=tk.LEFT, padx=2)
            # Store reference for updating
            if not hasattr(self, 'lang_buttons'):
                self.lang_buttons = {}
            self.lang_buttons[lang_code] = btn

    def change_language(self, lang_code):
        global current_language
        if current_language == lang_code:
            return
        current_language = lang_code

        # Update button states
        for lc, btn in self.lang_buttons.items():
            if lc == lang_code:
                btn.config(bg=COLORS['accent'])
            else:
                btn.config(bg=COLORS['bg_card'])

        # Update all UI elements dynamically
        self.refresh_ui()

    def refresh_ui(self):
        """Actualiza todos los textos de la UI al idioma actual"""
        # Update window title
        self.root.title(t('title'))

        # Update notebook tabs
        self.notebook.tab(0, text=t('tab_png'))
        self.notebook.tab(1, text=t('tab_ogg'))
        self.notebook.tab(2, text=t('tab_about'))

        # Update PNG panel
        self.refresh_panel(self.png_panel)

        # Update OGG panel
        self.refresh_panel(self.ogg_panel)

    def refresh_panel(self, panel):
        """Actualiza los textos de un FilePanel"""
        # Update title
        title = t('images_png') if panel.file_type == 'png' else t('audio_ogg')
        # Find and update the title label (first label in the header)
        for widget in panel.parent.winfo_children():
            self._update_panel_widgets(widget, panel)

        # Update file count
        panel.update_count()

        # Update drop zone
        panel.drop_label.config(text=t('drop_zone'))

        # Update progress label if ready
        if panel.progress_label.cget('text') in ['Listo', 'Ready']:
            panel.progress_label.config(text=t('ready'))

        # Update buttons
        panel.decrypt_btn.config(text=t('decrypt'))
        panel.encrypt_btn.config(text=t('encrypt'))

        # Update slideshow button if exists
        if hasattr(panel, 'slideshow_btn'):
            panel.slideshow_btn.config(text=f"⛶ {t('slideshow').upper()}")

    def _update_panel_widgets(self, widget, panel):
        """Recursivamente busca y actualiza widgets"""
        widget_class = widget.winfo_class()

        if widget_class == 'Label':
            current_text = widget.cget('text')
            # Update specific labels based on current text
            if current_text in ['IMAGENES (PNG)', 'IMAGES (PNG)']:
                widget.config(text=t('images_png'))
            elif current_text in ['AUDIO (OGG)']:
                widget.config(text=t('audio_ogg'))
            elif current_text in ['PREVIEW']:
                widget.config(text=t('preview'))
            elif current_text in ['OPCIONES', 'OPTIONS']:
                widget.config(text=t('options'))

        elif widget_class == 'Checkbutton':
            current_text = widget.cget('text')
            if current_text in ['Preservar estructura', 'Preserve structure']:
                widget.config(text=t('preserve_structure'))

        elif widget_class == 'Button':
            current_text = widget.cget('text')
            if current_text in ['Archivos', 'Files']:
                widget.config(text=t('select_files'))
            elif current_text in ['Carpeta', 'Folder']:
                widget.config(text=t('select_folder'))
            elif current_text in ['Limpiar', 'Clear']:
                widget.config(text=t('clear'))
            elif current_text in ['Slideshow']:
                widget.config(text=t('slideshow'))

        # Recurse into children
        for child in widget.winfo_children():
            self._update_panel_widgets(child, panel)

    def create_statusbar(self, parent):
        bar = tk.Frame(parent, bg=COLORS['bg_card'], height=30)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        tk.Label(bar, text="RPGMV Converter", font=('Consolas', 9),
                bg=COLORS['bg_card'], fg=COLORS['text_dim']).pack(side=tk.LEFT, padx=15)

        tk.Label(bar, text="by Karl Ravenlight", font=('Consolas', 9),
                bg=COLORS['bg_card'], fg=COLORS['accent']).pack(side=tk.RIGHT, padx=15)

    def create_about_tab(self, parent):
        # Scrollable
        canvas = tk.Canvas(parent, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg_dark'])

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Content
        container = tk.Frame(scrollable, bg=COLORS['bg_dark'])
        container.pack(expand=True, fill=tk.X, padx=50, pady=30)

        # ASCII Box
        ascii_frame = tk.Frame(container, bg='#0a0a12', highlightbackground=COLORS['accent_green'],
                              highlightthickness=2)
        ascii_frame.pack(fill=tk.X)

        ascii_art = """
    ██████╗  █████╗ ██╗   ██╗███████╗███╗   ██╗██╗     ██╗ ██████╗ ██╗  ██╗████████╗
    ██╔══██╗██╔══██╗██║   ██║██╔════╝████╗  ██║██║     ██║██╔════╝ ██║  ██║╚══██╔══╝
    ██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║██║     ██║██║  ███╗███████║   ██║
    ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║     ██║██║   ██║██╔══██║   ██║
    ██║  ██║██║  ██║ ╚████╔╝ ███████╗██║ ╚████║███████╗██║╚██████╔╝██║  ██║   ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   """

        tk.Label(ascii_frame, text=ascii_art, font=('Consolas', 8),
                bg='#0a0a12', fg=COLORS['accent_green'], justify='left').pack(padx=20, pady=(20, 10))

        # Separator
        tk.Frame(ascii_frame, bg=COLORS['accent_green'], height=2).pack(fill=tk.X, padx=20)

        # Main info
        info_frame = tk.Frame(ascii_frame, bg='#0a0a12')
        info_frame.pack(fill=tk.X, padx=30, pady=20)

        # For RPG Maker MV/MZ
        special_frame = tk.Frame(info_frame, bg='#0a0a12')
        special_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(special_frame, text="[ UNIVERSAL TOOL FOR ]",
                font=('Consolas', 10), bg='#0a0a12', fg=COLORS['accent_pink']).pack()

        # RPG Maker title with animation effect
        self.rpgmaker_label = tk.Label(special_frame, text="★ RPG MAKER MV/MZ ★",
                                           font=('Consolas', 18, 'bold'),
                                           bg='#0a0a12', fg=COLORS['accent_cyan'])
        self.rpgmaker_label.pack(pady=(5, 0))

        tk.Label(special_frame, text="Asset Encryption/Decryption",
                font=('Consolas', 10), bg='#0a0a12', fg=COLORS['text_dim']).pack()

        # Start animation
        self.animate_title()

        # Separator
        tk.Frame(info_frame, bg=COLORS['border'], height=1).pack(fill=tk.X, pady=10)

        # Credits
        info_lines = [
            ("CODED BY", "Karl Ravenlight", COLORS['accent_cyan']),
            ("PROTECTION", "RPGMV XOR 16-byte Header Encryption", COLORS['text_dim']),
            ("STATUS", "100% Working", COLORS['success']),
            ("RELEASE", "2025", COLORS['text_dim']),
        ]

        for label, value, color in info_lines:
            line = tk.Frame(info_frame, bg='#0a0a12')
            line.pack(fill=tk.X, pady=2)
            tk.Label(line, text=f"[*] {label} ", font=('Consolas', 10),
                    bg='#0a0a12', fg=COLORS['accent_pink']).pack(side=tk.LEFT)
            tk.Label(line, text="." * (20 - len(label)), font=('Consolas', 10),
                    bg='#0a0a12', fg=COLORS['text_dim']).pack(side=tk.LEFT)
            tk.Label(line, text=f" {value}", font=('Consolas', 10),
                    bg='#0a0a12', fg=color).pack(side=tk.LEFT)

        # Separator
        tk.Frame(ascii_frame, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=20, pady=(5, 0))

        # Links
        links_frame = tk.Frame(ascii_frame, bg='#0a0a12')
        links_frame.pack(fill=tk.X, padx=30, pady=15)

        tk.Label(links_frame, text=">> LINKS", font=('Consolas', 10, 'bold'),
                bg='#0a0a12', fg=COLORS['text']).pack(anchor='w', pady=(0, 10))

        links = [
            ("www.ravenlight.net", "https://www.ravenlight.net"),
            ("instagram.com/vjravenlight", "https://www.instagram.com/vjravenlight"),
        ]

        for text, url in links:
            link = tk.Label(links_frame, text=f"    {text}", font=('Consolas', 10),
                           bg='#0a0a12', fg=COLORS['accent_cyan'], cursor='hand2')
            link.pack(anchor='w', pady=2)
            link.bind('<Button-1>', lambda e, u=url: webbrowser.open(u))
            link.bind('<Enter>', lambda e, l=link: l.config(fg=COLORS['accent_pink']))
            link.bind('<Leave>', lambda e, l=link: l.config(fg=COLORS['accent_cyan']))

        # Note
        tk.Frame(ascii_frame, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=20, pady=(5, 0))

        note_frame = tk.Frame(ascii_frame, bg='#0a0a12')
        note_frame.pack(fill=tk.X, padx=30, pady=15)

        tk.Label(note_frame, text="[!] COMPATIBILIDAD:", font=('Consolas', 10, 'bold'),
                bg='#0a0a12', fg=COLORS['accent']).pack(anchor='w')
        tk.Label(note_frame, text="    Este programa funciona con CUALQUIER",
                font=('Consolas', 10), bg='#0a0a12', fg=COLORS['text_dim']).pack(anchor='w')
        tk.Label(note_frame, text="    juego de RPG Maker MV/MZ que use",
                font=('Consolas', 10), bg='#0a0a12', fg=COLORS['text_dim']).pack(anchor='w')
        tk.Label(note_frame, text="    encriptacion RPGMV estandar.",
                font=('Consolas', 10), bg='#0a0a12', fg=COLORS['text_dim']).pack(anchor='w')

        # Quote
        tk.Frame(ascii_frame, bg=COLORS['accent_green'], height=2).pack(fill=tk.X, padx=20, pady=(10, 0))

        tk.Label(ascii_frame, text='"Breaking barriers between creators and their assets"',
                font=('Consolas', 11, 'italic'), bg='#0a0a12',
                fg=COLORS['accent_green']).pack(pady=20)

        # Greets
        greets = tk.Label(container, text="═══════════[ GREETS TO ALL RPGMAKER DEVS ]═══════════",
                         font=('Consolas', 10), bg=COLORS['bg_dark'], fg=COLORS['accent_green'])
        greets.pack(pady=(20, 0))

    def animate_title(self):
        """Animacion del titulo RPG Maker"""
        colors = [COLORS['accent_cyan'], COLORS['accent_pink'], COLORS['accent_green'],
                  COLORS['accent'], COLORS['accent_orange']]

        def cycle():
            if hasattr(self, 'rpgmaker_label') and self.rpgmaker_label.winfo_exists():
                current = getattr(self, '_color_idx', 0)
                self.rpgmaker_label.config(fg=colors[current])
                self._color_idx = (current + 1) % len(colors)
                self.root.after(800, cycle)

        cycle()

    def check_queue(self):
        try:
            while True:
                task = self.task_queue.get_nowait()
                if task[0] == 'preview':
                    panel = task[1]
                    panel.show_preview(task[2])
                elif task[0] == 'progress':
                    panel = task[1]
                    panel.progress_var.set(task[2])
                    panel.progress_label.config(text=task[3])
                elif task[0] == 'log':
                    panel = task[1]
                    panel.log(task[2], task[3])
                elif task[0] == 'done':
                    panel = task[1]
                    panel.decrypt_btn.config(state=tk.NORMAL)
                    panel.encrypt_btn.config(state=tk.NORMAL)
        except queue.Empty:
            pass
        self.root.after(50, self.check_queue)


# ============================================================================
# MAIN // Punto de entrada de la aplicacion
# ============================================================================

def main():
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()

    app = RPGMVConverterApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
