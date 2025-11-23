import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import os
import sys
import ctypes
from pathlib import Path
import shutil
from datetime import datetime
import random
import string
import winreg
import subprocess
import pythoncom
from win32com.client import Dispatch
import winshell
import zipfile
import requests
import io
from threading import Thread
import keyboard

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        script = sys.argv[0]
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
        
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        sys.exit()
    except Exception as e:
        print(f"Ошибка перезапуска: {e}")
        return False

def generate_random_title():
    length = random.randint(5, 10)
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class NyaUnlock:
    def __init__(self):
        self.in_recovery = self.check_recovery_environment()
        
        if not self.in_recovery:
            self.hide_console()
        
        if not self.in_recovery and not is_admin():
            print("Требуются права администратора... Перезапуск...")
            if not run_as_admin():
                messagebox.showwarning(
                    "Предупреждение", 
                    "Не удалось запустить с правами администратора."
                )
        
        self.root = tk.Tk()
        self.root.title("Nya.Unlock")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        self.root.attributes('-topmost', True)
        
        if not self.in_recovery:
            self.center_window()
        
        self.setup_dragging()
        
        self.is_admin = is_admin() or self.in_recovery
        self.current_frame = None
        self.process_update_job = None
        
        self.always_on_top = True
        self.critical_processes = set()
        
        self.bin_path = os.path.join(os.path.dirname(__file__), "bin")
        os.makedirs(self.bin_path, exist_ok=True)
        
        self.update_window_title()
        
        self.setup_global_keyboard()
        
        self.setup_main_menu()
        
    def check_recovery_environment(self):
        try:
            recovery_indicators = [
                os.path.exists(r"X:\Sources"),
                os.path.exists(r"X:\Windows\System32\Recovery"),
                "RECOVERY" in os.environ.get("PATH", ""),
                "WINPE" in os.environ.get("SYSTEMROOT", "")
            ]
            return any(recovery_indicators)
        except:
            return False
        
    def hide_console(self):
        try:
            if sys.platform == 'win32':
                kernel32 = ctypes.WinDLL('kernel32')
                user32 = ctypes.WinDLL('user32')
                hwnd = kernel32.GetConsoleWindow()
                if hwnd:
                    user32.ShowWindow(hwnd, 0)
        except:
            pass
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_dragging(self):
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        
    def start_move(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()
        self.drag_data["dragging"] = True
        
    def on_move(self, event):
        if self.drag_data["dragging"]:
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.root.geometry(f"+{x}+{y}")
            
    def stop_move(self, event):
        self.drag_data["dragging"] = False
        
    def setup_global_keyboard(self):
        try:
            keyboard.add_hotkey('up', self.navigate_up)
            keyboard.add_hotkey('down', self.navigate_down)
            keyboard.add_hotkey('enter', self.activate_selected)
            keyboard.add_hotkey('ctrl+alt+n', self.focus_window)
        except Exception as e:
            print(f"Ошибка настройки клавиатуры: {e}")
            
    def navigate_up(self):
        try:
            if hasattr(self, 'current_frame') and self.current_frame:
                all_widgets = self.get_all_widgets(self.current_frame)
                focusable_widgets = [w for w in all_widgets if self.is_focusable(w)]
                
                if focusable_widgets:
                    current_focus = self.root.focus_get()
                    if current_focus in focusable_widgets:
                        index = focusable_widgets.index(current_focus)
                        new_index = (index - 1) % len(focusable_widgets)
                    else:
                        new_index = 0
                    
                    focusable_widgets[new_index].focus_set()
                    self.highlight_widget(focusable_widgets[new_index])
        except Exception as e:
            print(f"Ошибка навигации вверх: {e}")
            
    def navigate_down(self):
        try:
            if hasattr(self, 'current_frame') and self.current_frame:
                all_widgets = self.get_all_widgets(self.current_frame)
                focusable_widgets = [w for w in all_widgets if self.is_focusable(w)]
                
                if focusable_widgets:
                    current_focus = self.root.focus_get()
                    if current_focus in focusable_widgets:
                        index = focusable_widgets.index(current_focus)
                        new_index = (index + 1) % len(focusable_widgets)
                    else:
                        new_index = 0
                    
                    focusable_widgets[new_index].focus_set()
                    self.highlight_widget(focusable_widgets[new_index])
        except Exception as e:
            print(f"Ошибка навигации вниз: {e}")
            
    def get_all_widgets(self, parent):
        widgets = []
        for child in parent.winfo_children():
            widgets.append(child)
            if hasattr(child, 'winfo_children'):
                widgets.extend(self.get_all_widgets(child))
        return widgets
    
    def is_focusable(self, widget):
        return isinstance(widget, (tk.Button, ttk.Button, tk.Entry, ttk.Entry, tk.Listbox))
    
    def highlight_widget(self, widget):
        try:
            self.reset_highlights()
            
            if isinstance(widget, (tk.Button, ttk.Button)):
                original_bg = widget.cget('background')
                widget.config(background='#a0a0ff')
                widget.original_bg = original_bg
        except:
            pass
    
    def reset_highlights(self):
        try:
            if hasattr(self, 'current_frame') and self.current_frame:
                all_widgets = self.get_all_widgets(self.current_frame)
                for widget in all_widgets:
                    if hasattr(widget, 'original_bg'):
                        try:
                            widget.config(background=widget.original_bg)
                        except:
                            pass
        except:
            pass
            
    def activate_selected(self):
        try:
            widget = self.root.focus_get()
            if isinstance(widget, (tk.Button, ttk.Button)):
                widget.invoke()
        except Exception as e:
            print(f"Ошибка активации: {e}")
            
    def focus_window(self):
        try:
            self.root.focus_force()
            self.root.lift()
        except:
            pass
        
    def update_window_title(self):
        if self.root:
            try:
                random_title = generate_random_title()
                self.root.title(random_title)
                self.root.after(4000, self.update_window_title)
            except:
                pass
    
    def setup_bottom_panel(self, parent):
        bottom_panel = tk.Frame(parent, bg='#e0e0e0', height=25)
        bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_panel.pack_propagate(False)
        
        mode_text = "Recovery Mode" if self.in_recovery else "Admin Mode" if self.is_admin else "User Mode"
        version_label = tk.Label(bottom_panel, text=f"Nya.Unlock v1.0 | {mode_text}", 
                               bg='#e0e0e0', fg='black', font=('Arial', 8))
        version_label.pack(side=tk.LEFT, padx=5)
        
        unlock_status = tk.Label(bottom_panel, text="System Unlocked", 
                               bg='#e0e0e0', fg='green', font=('Arial', 8))
        unlock_status.pack(side=tk.RIGHT, padx=5)
        
        return bottom_panel
        
    def setup_main_menu(self):
        self.clear_frame()
        self.root.geometry("400x400")
        
        title_bar = tk.Frame(self.current_frame, bg='#e0e0e0', height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        title_label = tk.Label(title_bar, text="Nya.Unlock - MultiTool", 
                             bg='#e0e0e0', fg='black', font=('Arial', 10, 'bold'))
        title_label.pack(expand=True, pady=5)
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.on_move)
        title_label.bind('<ButtonRelease-1>', self.stop_move)
        
        minimize_btn = tk.Label(title_bar, text="_", bg='#e0e0e0', fg='black', 
                           font=('Arial', 16, 'bold'), cursor='hand2')
        minimize_btn.pack(side=tk.RIGHT, padx=5)
        minimize_btn.bind('<Button-1>', lambda e: self.root.iconify())
        minimize_btn.bind('<Enter>', lambda e: minimize_btn.config(bg='#d0d0d0'))
        minimize_btn.bind('<Leave>', lambda e: minimize_btn.config(bg='#e0e0e0'))
        
        close_btn = tk.Label(title_bar, text="×", bg='#e0e0e0', fg='black', 
                           font=('Arial', 16, 'bold'), cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind('<Button-1>', lambda e: self.safe_exit())
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#ff4444', fg='white'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='#e0e0e0', fg='black'))
        
        button_frame = tk.Frame(self.current_frame, bg='white')
        button_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        buttons = [
            ("Диспетчер задач", self.show_task_manager),
            ("Разблокировка", self.show_unlock_tools),
            ("Автозагрузка", self.show_startup_manager),
            ("MBR Recovery", self.show_mbr_recovery),
            ("Утилиты", self.show_utilities),
            ("Консоль", self.show_console)
        ]
        
        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command,
                          bg='#f0f0f0', fg='black', font=('Arial', 9),
                          relief='solid', bd=1, height=2)
            btn.pack(fill=tk.X, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#e0e0e0'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#f0f0f0'))
        
        self.setup_bottom_panel(self.current_frame)

    def show_unlock_tools(self):
        self.clear_frame()
        self.root.geometry("600x500")
        
        self.setup_title_bar("Разблокировка системы")
        
        content_frame = tk.Frame(self.current_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        unlock_buttons = [
            ("Восстановить шрифты", self.restore_fonts),
            ("Восстановить курсор", self.restore_cursor),
            ("Убрать SwapMouseButton", self.fix_swap_mouse),
            ("Разблокировать диспетчер задач", self.unlock_task_manager),
            ("Разблокировать диски", self.unlock_drives)
        ]
        
        for text, command in unlock_buttons:
            btn = tk.Button(content_frame, text=text, command=command,
                          bg='#f0f0f0', fg='black', font=('Arial', 10),
                          relief='solid', bd=1, height=2)
            btn.pack(fill=tk.X, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#e0e0e0'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#f0f0f0'))
        
        log_frame = tk.Frame(content_frame, bg='white')
        log_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        tk.Label(log_frame, text="Лог операций:", bg='white', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.unlock_log = tk.Text(log_frame, wrap=tk.WORD, width=60, height=10,
                                 bg='#f8f8f8', fg='black', font=('Arial', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.unlock_log.yview)
        self.unlock_log.configure(yscrollcommand=scrollbar.set)
        
        self.unlock_log.insert('1.0', "Готов к работе...\n")
        self.unlock_log.config(state=tk.DISABLED)
        
        self.unlock_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.setup_bottom_panel(self.current_frame)

    def log_unlock(self, message):
        self.unlock_log.config(state=tk.NORMAL)
        self.unlock_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.unlock_log.see(tk.END)
        self.unlock_log.config(state=tk.DISABLED)

    def restore_fonts(self):
        if not messagebox.askyesno("Восстановление шрифтов", 
                                 "Это восстановит стандартные шрифты Windows.\n"
                                 "Продолжить?"):
            return
        
        try:
            self.log_unlock("Начало восстановления шрифтов...")
            
            subprocess.run(['net', 'stop', 'FontCache'], capture_output=True)
            
            font_dirs = [
                os.path.join(os.environ['WINDIR'], 'Fonts'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts')
            ]
            
            restored_count = 0
            
            for font_dir in font_dirs:
                if os.path.exists(font_dir):
                    backup_dir = os.path.join(os.environ['TEMP'], 'FontBackup')
                    os.makedirs(backup_dir, exist_ok=True)
                    
                    standard_fonts = {
                        'arial.ttf', 'arialbd.ttf', 'arialbi.ttf', 'ariali.ttf',
                        'times.ttf', 'timesbd.ttf', 'timesbi.ttf', 'timesi.ttf',
                        'cour.ttf', 'courbd.ttf', 'courbi.ttf', 'couri.ttf',
                        'verdana.ttf', 'verdanab.ttf', 'verdanai.ttf', 'verdanaz.ttf',
                        'tahoma.ttf', 'tahomabd.ttf',
                        'segoeui.ttf', 'segoeuib.ttf', 'segoeuii.ttf', 'segoeuiz.ttf',
                        'seguisb.ttf', 'segui.ttf',
                        'calibri.ttf', 'calibrib.ttf', 'calibrii.ttf', 'calibriz.ttf',
                        'consola.ttf', 'consolab.ttf', 'consolai.ttf', 'consolaz.ttf',
                        'comic.ttf', 'comicbd.ttf',
                        'impact.ttf', 'georgia.ttf', 'georgiab.ttf', 'georgiai.ttf', 'georgiaz.ttf'
                    }
                    
                    for font_file in os.listdir(font_dir):
                        if font_file.lower().endswith(('.ttf', '.ttc', '.otf')):
                            if font_file.lower() not in standard_fonts:
                                src_path = os.path.join(font_dir, font_file)
                                dst_path = os.path.join(backup_dir, font_file)
                                try:
                                    shutil.move(src_path, dst_path)
                                    restored_count += 1
                                    self.log_unlock(f"Перемещен шрифт: {font_file}")
                                except Exception as e:
                                    self.log_unlock(f"Ошибка перемещения {font_file}: {e}")
            
            subprocess.run(['net', 'start', 'FontCache'], capture_output=True)
            
            subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], capture_output=True)
            subprocess.Popen(['explorer.exe'])
            
            self.log_unlock(f"Восстановление шрифтов завершено! Перемещено: {restored_count} шрифтов")
            messagebox.showinfo("Успех", 
                              f"Восстановление шрифтов завершено!\n"
                              f"Перемещено нестандартных шрифтов: {restored_count}\n"
                              f"Резервная копия создана в: {backup_dir}")
                              
        except Exception as e:
            self.log_unlock(f"Ошибка восстановления шрифтов: {e}")
            messagebox.showerror("Ошибка", f"Не удалось восстановить шрифты: {e}")

    def restore_cursor(self):
        try:
            self.log_unlock("Восстановление курсора...")
            
            cursor_schemes = [
                (r"Control Panel\Cursors", "Arrow", "%SystemRoot%\\cursors\\arrow_i.cur"),
                (r"Control Panel\Cursors", "Help", "%SystemRoot%\\cursors\\help_i.cur"),
                (r"Control Panel\Cursors", "AppStarting", "%SystemRoot%\\cursors\\wait_i.cur"),
                (r"Control Panel\Cursors", "Wait", "%SystemRoot%\\cursors\\busy_i.cur"),
                (r"Control Panel\Cursors", "Crosshair", "%SystemRoot%\\cursors\\cross_i.cur"),
                (r"Control Panel\Cursors", "IBeam", "%SystemRoot%\\cursors\\beam_i.cur"),
                (r"Control Panel\Cursors", "NWPen", "%SystemRoot%\\cursors\\pen_i.cur"),
                (r"Control Panel\Cursors", "No", "%SystemRoot%\\cursors\\no_i.cur"),
                (r"Control Panel\Cursors", "SizeNS", "%SystemRoot%\\cursors\\sizeNS_i.cur"),
                (r"Control Panel\Cursors", "SizeWE", "%SystemRoot%\\cursors\\sizeWE_i.cur"),
                (r"Control Panel\Cursors", "SizeNWSE", "%SystemRoot%\\cursors\\sizeNWSE_i.cur"),
                (r"Control Panel\Cursors", "SizeNESW", "%SystemRoot%\\cursors\\sizeNESW_i.cur"),
                (r"Control Panel\Cursors", "SizeAll", "%SystemRoot%\\cursors\\move_i.cur"),
                (r"Control Panel\Cursors", "UpArrow", "%SystemRoot%\\cursors\\up_i.cur"),
                (r"Control Panel\Cursors", "Hand", "%SystemRoot%\\cursors\\hand_i.cur")
            ]
            
            for key_path, value_name, default_value in cursor_schemes:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_EXPAND_SZ, default_value)
                except:
                    pass
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors", 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "Scheme Source", 0, winreg.REG_DWORD, 2)
            except:
                pass
            
            ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0)
            
            self.log_unlock("Курсор восстановлен до стандартных настроек")
            messagebox.showinfo("Успех", "Стандартный курсор восстановлен!")
            
        except Exception as e:
            self.log_unlock(f"Ошибка восстановления курсора: {e}")
            messagebox.showerror("Ошибка", f"Не удалось восстановить курсор: {e}")

    def fix_swap_mouse(self):
        try:
            self.log_unlock("Исправление SwapMouseButton...")
            
            result = ctypes.windll.user32.SwapMouseButton(0)
            
            if result:
                self.log_unlock("Кнопки мыши восстановлены (левая - основная)")
                messagebox.showinfo("Успех", "Кнопки мыши восстановлены!\nЛевая кнопка - основная")
            else:
                self.log_unlock("Кнопки мыши уже в нормальном состоянии")
                messagebox.showinfo("Информация", "Кнопки мыши уже в нормальном состоянии")
                
        except Exception as e:
            self.log_unlock(f"Ошибка исправления мыши: {e}")
            messagebox.showerror("Ошибка", f"Не удалось исправить кнопки мыши: {e}")

    def unlock_task_manager(self):
        try:
            self.log_unlock("Разблокировка диспетчера задач...")
            
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools")
            ]
            
            unlocked = False
            for hkey, subkey, value_name in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        try:
                            winreg.DeleteValue(key, value_name)
                            self.log_unlock(f"Удалено значение: {value_name} из {subkey}")
                            unlocked = True
                        except FileNotFoundError:
                            pass
                except FileNotFoundError:
                    pass
            
            if unlocked:
                self.log_unlock("Диспетчер задач разблокирован")
                messagebox.showinfo("Успех", "Диспетчер задач разблокирован!")
            else:
                self.log_unlock("Диспетчер задач не был заблокирован")
                messagebox.showinfo("Информация", "Диспетчер задач не был заблокирован")
                
        except Exception as e:
            self.log_unlock(f"Ошибка разблокировки диспетчера задач: {e}")
            messagebox.showerror("Ошибка", f"Не удалось разблокировать диспетчер задач: {e}")

    def unlock_drives(self):
        try:
            self.log_unlock("Разблокировка дисков...")
            
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDrives"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDrives"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoViewOnDrive"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoViewOnDrive")
            ]
            
            unlocked = False
            for hkey, subkey, value_name in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        try:
                            winreg.DeleteValue(key, value_name)
                            self.log_unlock(f"Удалено значение: {value_name} из {subkey}")
                            unlocked = True
                        except FileNotFoundError:
                            pass
                except FileNotFoundError:
                    pass
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE) as key:
                    try:
                        winreg.DeleteValue(key, "NoDriveTypeAutoRun")
                    except FileNotFoundError:
                        pass
            except FileNotFoundError:
                pass
            
            if unlocked:
                self.log_unlock("Диски разблокированы")
                messagebox.showinfo("Успех", "Диски разблокированы!\nМожет потребоваться перезагрузка Explorer")
                
                if messagebox.askyesno("Перезагрузка Explorer", "Перезапустить Explorer для применения изменений?"):
                    subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], capture_output=True)
                    subprocess.Popen(['explorer.exe'])
                    self.log_unlock("Explorer перезапущен")
            else:
                self.log_unlock("Диски не были заблокированы")
                messagebox.showinfo("Информация", "Диски не были заблокированы")
                
        except Exception as e:
            self.log_unlock(f"Ошибка разблокировки дисков: {e}")
            messagebox.showerror("Ошибка", f"Не удалось разблокировать диски: {e}")

    def show_console(self):
        self.clear_frame()
        self.root.geometry("800x600")
        
        self.setup_title_bar("Встроенная консоль")
        
        content_frame = tk.Frame(self.current_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        tools_frame = tk.Frame(content_frame, bg='white')
        tools_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(tools_frame, text="Очистить", command=self.clear_console).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Выполнить команду", command=self.execute_command).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Перезапуск CMD", command=self.restart_cmd).pack(side=tk.LEFT, padx=2)
        
        console_frame = tk.Frame(content_frame, bg='black')
        console_frame.pack(expand=True, fill=tk.BOTH)
        
        self.console_text = tk.Text(console_frame, wrap=tk.WORD, bg='black', fg='white', 
                                   font=('Consolas', 10), insertbackground='white')
        
        scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        input_frame = tk.Frame(content_frame, bg='white')
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Команда:", bg='white').pack(side=tk.LEFT, padx=5)
        self.cmd_entry = tk.Entry(input_frame, width=50, font=('Consolas', 10))
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cmd_entry.bind('<Return>', lambda e: self.execute_command())
        
        tk.Button(input_frame, text="Выполнить", command=self.execute_command).pack(side=tk.RIGHT, padx=5)
        
        self.start_cmd_process()
        
        self.setup_bottom_panel(self.current_frame)

    def start_cmd_process(self):
        try:
            self.cmd_process = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.read_cmd_output()
            
        except Exception as e:
            self.console_text.insert(tk.END, f"Ошибка запуска CMD: {e}\n")

    def read_cmd_output(self):
        def read_thread():
            while hasattr(self, 'cmd_process') and self.cmd_process and self.cmd_process.poll() is None:
                try:
                    output = self.cmd_process.stdout.readline()
                    if output:
                        try:
                            decoded_output = output.decode('cp866')
                        except:
                            try:
                                decoded_output = output.decode('utf-8')
                            except:
                                decoded_output = output.decode('cp1251', errors='replace')
                        
                        self.console_text.after(0, self.append_output, decoded_output)
                except Exception as e:
                    break
        
        thread = Thread(target=read_thread, daemon=True)
        thread.start()

    def append_output(self, text):
        self.console_text.insert(tk.END, text)
        self.console_text.see(tk.END)

    def execute_command(self):
        command = self.cmd_entry.get().strip()
        if not command:
            return
        
        self.console_text.insert(tk.END, f"> {command}\n")
        self.cmd_entry.delete(0, tk.END)
        
        try:
            if hasattr(self, 'cmd_process') and self.cmd_process and self.cmd_process.poll() is None:
                command_bytes = (command + '\r\n').encode('cp866')
                self.cmd_process.stdin.write(command_bytes)
                self.cmd_process.stdin.flush()
        except Exception as e:
            self.console_text.insert(tk.END, f"Ошибка выполнения команды: {e}\n")

    def clear_console(self):
        self.console_text.delete(1.0, tk.END)

    def restart_cmd(self):
        try:
            if hasattr(self, 'cmd_process'):
                self.cmd_process.terminate()
            self.clear_console()
            self.start_cmd_process()
            self.console_text.insert(tk.END, "CMD перезапущен\n")
        except Exception as e:
            self.console_text.insert(tk.END, f"Ошибка перезапуска: {e}\n")

    def show_utilities(self):
        self.clear_frame()
        self.root.geometry("400x200")
        
        self.setup_title_bar("Утилиты")
        
        content_frame = tk.Frame(self.current_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        explorer_frame = tk.Frame(content_frame, bg='#f0f0f0', relief='solid', bd=1)
        explorer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(explorer_frame, text="Explorer++", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor=tk.W, padx=10, pady=10)
        tk.Label(explorer_frame, text="Улучшенный файловый менеджер для Windows", bg='#f0f0f0').pack(anchor=tk.W, padx=10)
        
        btn_frame = tk.Frame(explorer_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, padx=10, pady=15)
        
        tk.Button(btn_frame, text="Запустить Explorer++", 
                 command=self.run_explorer_plusplus,
                 bg='#e0e0e0', fg='black', font=('Arial', 10), height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Скачать и установить", 
                 command=self.download_explorer_plusplus,
                 bg='#d0e0ff', fg='black', font=('Arial', 10), height=2).pack(side=tk.LEFT, padx=5)
        
        self.setup_bottom_panel(self.current_frame)

    def download_explorer_plusplus(self):
        try:
            url = "https://github.com/derceg/explorerplusplus/releases/download/version-1.4.0/explorerpp_x64.zip"
            download_path = os.path.join(self.bin_path, "explorerpp_x64.zip")
            extract_path = os.path.join(self.bin_path, "explorerpp")
            
            os.makedirs(extract_path, exist_ok=True)
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            progress = tk.Toplevel(self.root)
            progress.title("Скачивание Explorer++")
            progress.geometry("300x100")
            progress.transient(self.root)
            progress.grab_set()
            
            tk.Label(progress, text="Скачивание Explorer++...").pack(pady=10)
            progress_bar = ttk.Progressbar(progress, length=250, mode='determinate')
            progress_bar.pack(pady=10)
            
            def download_thread():
                downloaded = 0
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                progress_bar['value'] = percent
                                progress.update()
                
                progress_bar['value'] = 100
                tk.Label(progress, text="Распаковка...").pack()
                
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                os.remove(download_path)
                
                progress.destroy()
                messagebox.showinfo("Успех", "Explorer++ успешно скачан и установлен!")
            
            thread = Thread(target=download_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скачать Explorer++: {e}")

    def run_explorer_plusplus(self):
        try:
            explorer_path = os.path.join(self.bin_path, "explorerpp", "Explorer++.exe")
            
            if os.path.exists(explorer_path):
                subprocess.Popen([explorer_path])
            else:
                if messagebox.askyesno("Explorer++ не найден", 
                                      "Explorer++ не установлен. Скачать и установить?"):
                    self.download_explorer_plusplus()
                else:
                    messagebox.showinfo("Информация", "Explorer++ можно скачать вручную с:\nhttps://github.com/derceg/explorerplusplus/releases")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить Explorer++: {e}")

    def show_task_manager(self):
        self.clear_frame()
        self.root.geometry("900x600")
        
        self.setup_title_bar("Диспетчер задач")
        
        if not self.is_admin and not self.in_recovery:
            tk.Label(self.current_frame, text="Требуются права администратора", 
                    font=('Arial', 12), fg='gray', bg='white').pack(expand=True)
            self.setup_bottom_panel(self.current_frame)
            return
        
        content_frame = tk.Frame(self.current_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        notebook = ttk.Notebook(content_frame)
        notebook.pack(expand=True, fill=tk.BOTH)
        
        processes_frame = ttk.Frame(notebook)
        self.setup_processes_tab(processes_frame)
        notebook.add(processes_frame, text="Процессы")
        
        services_frame = ttk.Frame(notebook)
        self.setup_services_tab(services_frame)
        notebook.add(services_frame, text="Службы")
        
        self.setup_bottom_panel(self.current_frame)

    def setup_processes_tab(self, parent):
        tools_frame = tk.Frame(parent, bg='white')
        tools_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(tools_frame, text="Обновить", command=self.update_processes).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Завершить", command=self.kill_process).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Заморозить", command=self.freeze_process).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Разморозить", command=self.unfreeze_process).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Добавить в критические", command=self.add_critical_process).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Убрать из критических", command=self.remove_critical_process).pack(side=tk.LEFT, padx=2)
        
        tree_frame = tk.Frame(parent, bg='white')
        tree_frame.pack(expand=True, fill=tk.BOTH)
        
        columns = ('pid', 'name', 'cpu', 'memory', 'status', 'critical')
        self.process_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        self.process_tree.heading('pid', text='PID')
        self.process_tree.heading('name', text='Имя процесса')
        self.process_tree.heading('cpu', text='CPU %')
        self.process_tree.heading('memory', text='Память (MB)')
        self.process_tree.heading('status', text='Статус')
        self.process_tree.heading('critical', text='Критичность')
        
        self.process_tree.column('pid', width=80)
        self.process_tree.column('name', width=200)
        self.process_tree.column('cpu', width=80)
        self.process_tree.column('memory', width=100)
        self.process_tree.column('status', width=100)
        self.process_tree.column('critical', width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_processes()

    def update_processes(self):
        try:
            if hasattr(self, 'process_tree') and self.process_tree.winfo_exists():
                for item in self.process_tree.get_children():
                    self.process_tree.delete(item)
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                    try:
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                        pid = proc.info['pid']
                        name = proc.info['name']
                        
                        is_critical = "Да" if pid in self.critical_processes else "Нет"
                        
                        values = (
                            pid,
                            name,
                            f"{proc.info['cpu_percent']:.1f}" if proc.info['cpu_percent'] else "0.0",
                            f"{memory_mb:.1f}",
                            proc.info['status'] or "running",
                            is_critical
                        )
                        self.process_tree.insert('', 'end', values=values)
                        
                        if pid in self.critical_processes:
                            self.process_tree.item(self.process_tree.get_children()[-1], tags=('critical',))
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        continue
                
                self.process_tree.tag_configure('critical', background='#ffcccc')
                
        except Exception as e:
            print(f"Error updating processes: {e}")

    def kill_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите процесс для завершения")
            return
        
        item = selected[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        
        if pid in self.critical_processes:
            if not messagebox.askyesno("Внимание", "Это критический процесс! Завершение может привести к нестабильности системы. Продолжить?"):
                return
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if messagebox.askyesno("Подтверждение", f"Завершить процесс {process_name} (PID: {pid})?"):
                process.terminate()
                messagebox.showinfo("Успех", f"Процесс {process_name} завершен")
                self.update_processes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось завершить процесс: {e}")

    def freeze_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите процесс для заморозки")
            return
        
        item = selected[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        
        if pid in self.critical_processes:
            messagebox.showwarning("Предупреждение", "Невозможно заморозить критический процесс")
            return
        
        try:
            process = psutil.Process(pid)
            process.suspend()
            messagebox.showinfo("Успех", f"Процесс {process.name()} заморожен")
            self.update_processes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось заморозить процесс: {e}")

    def unfreeze_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите процесс для разморозки")
            return
        
        item = selected[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        
        try:
            process = psutil.Process(pid)
            process.resume()
            messagebox.showinfo("Успех", f"Процесс {process.name()} разморожен")
            self.update_processes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось разморозить процесс: {e}")

    def add_critical_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите процесс для добавления в критические")
            return
        
        item = selected[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        name = self.process_tree.item(item, 'values')[1]
        
        self.critical_processes.add(pid)
        messagebox.showinfo("Успех", f"Процесс {name} (PID: {pid}) добавлен в критические")
        self.update_processes()

    def remove_critical_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите процесс для удаления из критических")
            return
        
        item = selected[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        name = self.process_tree.item(item, 'values')[1]
        
        if pid in self.critical_processes:
            self.critical_processes.remove(pid)
            messagebox.showinfo("Успех", f"Процесс {name} (PID: {pid}) убран из критических")
            self.update_processes()
        else:
            messagebox.showwarning("Предупреждение", "Этот процесс не является критическим")

    def setup_services_tab(self, parent):
        tools_frame = tk.Frame(parent, bg='white')
        tools_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(tools_frame, text="Обновить", command=self.update_services).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Запустить", command=self.start_service).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Остановить", command=self.stop_service).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Удалить", command=self.delete_service).pack(side=tk.LEFT, padx=2)
        
        tree_frame = tk.Frame(parent, bg='white')
        tree_frame.pack(expand=True, fill=tk.BOTH)
        
        columns = ('name', 'display_name', 'status', 'startup')
        self.services_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        self.services_tree.heading('name', text='Имя службы')
        self.services_tree.heading('display_name', text='Отображаемое имя')
        self.services_tree.heading('status', text='Статус')
        self.services_tree.heading('startup', text='Тип запуска')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_services()

    def update_services(self):
        try:
            if hasattr(self, 'services_tree') and self.services_tree.winfo_exists():
                for item in self.services_tree.get_children():
                    self.services_tree.delete(item)
                
                for service in psutil.win_service_iter():
                    try:
                        service_info = service.as_dict()
                        values = (
                            service_info['name'],
                            service_info['display_name'],
                            service_info['status'],
                            service_info['start_type']
                        )
                        self.services_tree.insert('', 'end', values=values)
                    except Exception:
                        continue
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить список служб: {e}")

    def start_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите службу для запуска")
            return
        
        item = selected[0]
        service_name = self.services_tree.item(item, 'values')[0]
        
        try:
            subprocess.run(['sc', 'start', service_name], check=True, capture_output=True)
            messagebox.showinfo("Успех", f"Служба {service_name} запущена")
            self.update_services()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить службу: {e}")

    def stop_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите службу для остановки")
            return
        
        item = selected[0]
        service_name = self.services_tree.item(item, 'values')[0]
        
        try:
            subprocess.run(['sc', 'stop', service_name], check=True, capture_output=True)
            messagebox.showinfo("Успех", f"Служба {service_name} остановлена")
            self.update_services()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить службу: {e}")

    def delete_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите службу для удаления")
            return
        
        item = selected[0]
        service_name = self.services_tree.item(item, 'values')[0]
        
        if messagebox.askyesno("Подтверждение", 
                              f"ВНИМАНИЕ: Удаление службы {service_name} может привести к нестабильной работе системы!\nПродолжить?"):
            try:
                subprocess.run(['sc', 'delete', service_name], check=True, capture_output=True)
                messagebox.showinfo("Успех", f"Служба {service_name} удалена")
                self.update_services()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить службу: {e}")

    def show_startup_manager(self):
        self.clear_frame()
        self.root.geometry("800x600")
        
        self.setup_title_bar("Управление автозагрузкой")
        
        if not self.is_admin and not self.in_recovery:
            tk.Label(self.current_frame, text="Требуются права администратора", 
                    font=('Arial', 12), fg='gray', bg='white').pack(expand=True)
            self.setup_bottom_panel(self.current_frame)
            return
        
        content_frame = tk.Frame(self.current_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        buttons_frame = tk.Frame(content_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=10)
        
        startup_buttons = [
            ("Реестр", self.show_registry_startup),
            ("Папка автозагрузки", self.show_startup_folder),
            ("Планировщик задач", self.show_task_scheduler)
        ]
        
        for text, command in startup_buttons:
            btn = tk.Button(buttons_frame, text=text, command=command,
                          bg='#f0f0f0', fg='black', font=('Arial', 9),
                          relief='solid', bd=1, width=20)
            btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#e0e0e0'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#f0f0f0'))
        
        self.startup_content = tk.Frame(content_frame, bg='white')
        self.startup_content.pack(expand=True, fill=tk.BOTH)
        
        self.show_registry_startup()
        
        self.setup_bottom_panel(self.current_frame)

    def add_startup_entry(self):
        file_path = filedialog.askopenfilename(
            title="Выберите программу для автозагрузки",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                name_without_ext = os.path.splitext(file_name)[0]
                
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                  0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name_without_ext, 0, winreg.REG_SZ, file_path)
                
                messagebox.showinfo("Успех", f"Программа добавлена в автозагрузку: {file_name}")
                self.show_registry_startup()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить в автозагрузку: {e}")

    def remove_startup_entry(self, hkey, subkey, entry_name):
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, entry_name)
            messagebox.showinfo("Успех", f"Запись удалена: {entry_name}")
            self.show_registry_startup()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись: {e}")

    def create_startup_shortcut(self):
        file_path = filedialog.askopenfilename(
            title="Выберите программу для автозагрузки",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                startup_folder = os.path.join(os.environ['APPDATA'], 
                                             r'Microsoft\Windows\Start Menu\Programs\Startup')
                
                file_name = os.path.basename(file_path)
                shortcut_name = os.path.splitext(file_name)[0] + ".lnk"
                shortcut_path = os.path.join(startup_folder, shortcut_name)
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = file_path
                shortcut.WorkingDirectory = os.path.dirname(file_path)
                shortcut.save()
                
                messagebox.showinfo("Успех", f"Ярлык создан в автозагрузке: {shortcut_name}")
                self.show_startup_folder()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать ярлык: {e}")

    def remove_startup_shortcut(self, shortcut_name):
        try:
            startup_folder = os.path.join(os.environ['APPDATA'], 
                                         r'Microsoft\Windows\Start Menu\Programs\Startup')
            shortcut_path = os.path.join(startup_folder, shortcut_name)
            
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                messagebox.showinfo("Успех", f"Ярлык удален: {shortcut_name}")
                self.show_startup_folder()
            else:
                messagebox.showwarning("Предупреждение", "Ярлык не найден")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить ярлык: {e}")

    def show_registry_startup(self):
        self.clear_startup_content()
        
        notebook = ttk.Notebook(self.startup_content)
        notebook.pack(expand=True, fill=tk.BOTH)
        
        registry_locations = [
            ("HKCU Run", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ("HKLM Run", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        
        for tab_name, hkey, subkey in registry_locations:
            frame = ttk.Frame(notebook)
            self.setup_registry_tab(frame, hkey, subkey, tab_name)
            notebook.add(frame, text=tab_name)

    def setup_registry_tab(self, parent, hkey, subkey, tab_name):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=5)
        
        if hkey == winreg.HKEY_CURRENT_USER:
            tk.Button(button_frame, text="Добавить программу", 
                     command=self.add_startup_entry,
                     bg='#e0e0e0', fg='black', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(expand=True, fill=tk.BOTH)
        
        columns = ('name', 'path', 'enabled')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        tree.heading('name', text='Имя программы')
        tree.heading('path', text='Путь/Команда')
        tree.heading('enabled', text='Статус')
        
        tree.column('name', width=200)
        tree.column('path', width=400)
        tree.column('enabled', width=100)
        
        entries = self.get_registry_startup_entries(hkey, subkey)
        for name, path in entries:
            tree.insert('', 'end', values=(name, path, "Включено"))
        
        if not entries:
            tree.insert('', 'end', values=("Нет записей автозагрузки", "", ""))
        
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="Удалить из автозагрузки", 
                               command=lambda: self.remove_startup_entry(hkey, subkey, 
                                                                       tree.item(tree.selection()[0], 'values')[0]))
        
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                context_menu.post(event.x_root, event.y_root)
        
        tree.bind("<Button-3>", show_context_menu)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_registry_startup_entries(self, hkey, subkey):
        entries = []
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                i = 0
                while True:
                    try:
                        name, value, type = winreg.EnumValue(key, i)
                        entries.append((name, value))
                        i += 1
                    except WindowsError:
                        break
        except FileNotFoundError:
            pass
        except Exception as e:
            entries.append(("Ошибка чтения", str(e)))
        
        return entries

    def show_startup_folder(self):
        self.clear_startup_content()
        
        content_frame = tk.Frame(self.startup_content, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="Добавить ярлык", 
                 command=self.create_startup_shortcut,
                 bg='#e0e0e0', fg='black', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        startup_folders = [
            ("Текущий пользователь", os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')),
            ("Все пользователи", os.path.join(os.environ['PROGRAMDATA'], r'Microsoft\Windows\Start Menu\Programs\StartUp'))
        ]
        
        for folder_name, folder_path in startup_folders:
            group_frame = tk.LabelFrame(content_frame, text=f"{folder_name} - {folder_path}", 
                                      bg='white', font=('Arial', 10, 'bold'))
            group_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
            
            list_frame = tk.Frame(group_frame, bg='white')
            list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            listbox = tk.Listbox(list_frame, bg='#f8f8f8', font=('Arial', 9))
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)
            
            try:
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, file)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            listbox.insert(tk.END, f"{file} ({file_size} bytes)")
                else:
                    listbox.insert(tk.END, "Папка не существует")
            except Exception as e:
                listbox.insert(tk.END, f"Ошибка доступа: {e}")
            
            context_menu = tk.Menu(listbox, tearoff=0)
            context_menu.add_command(label="Удалить", 
                                   command=lambda lb=listbox, fp=folder_path: 
                                   self.remove_startup_shortcut(lb.get(lb.curselection()).split(' ')[0]))
            
            def show_context_menu(event, lb=listbox):
                try:
                    lb.selection_clear(0, tk.END)
                    lb.selection_set(lb.nearest(event.y))
                    context_menu.post(event.x_root, event.y_root)
                except:
                    pass
            
            listbox.bind("<Button-3>", show_context_menu)
            
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_task_scheduler(self):
        self.clear_startup_content()
        
        content_frame = tk.Frame(self.startup_content, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        tk.Label(content_frame, text="Автозагрузка через Планировщик задач", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
        
        tasks = self.get_startup_tasks()
        
        if tasks:
            tree_frame = tk.Frame(content_frame, bg='white')
            tree_frame.pack(expand=True, fill=tk.BOTH)
            
            columns = ('name', 'status', 'description')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
            
            tree.heading('name', text='Имя задачи')
            tree.heading('status', text='Статус')
            tree.heading('description', text='Описание')
            
            for task in tasks:
                tree.insert('', 'end', values=task)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            tk.Label(content_frame, text="Не удалось получить задачи планировщика", 
                    font=('Arial', 10), fg='red', bg='white').pack(expand=True)

    def get_startup_tasks(self):
        try:
            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'CSV'], 
                capture_output=True, 
                text=True, 
                encoding='cp866'
            )
            
            tasks = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    for line in lines[1:6]:
                        fields = line.split('","')
                        if len(fields) >= 3:
                            task_name = fields[0].replace('"', '')
                            status = fields[1]
                            schedule = fields[2] if len(fields) > 2 else ""
                            tasks.append((task_name, status, schedule))
            
            return tasks
            
        except Exception as e:
            return [("Ошибка", str(e), "Не удалось получить задачи")]

    def show_mbr_recovery(self):
        self.clear_frame()
        self.root.geometry("500x400")
        
        self.setup_title_bar("MBR Recovery")
        
        if not self.is_admin and not self.in_recovery:
            tk.Label(self.current_frame, text="Требуются права администратора", 
                    font=('Arial', 12), fg='gray', bg='white').pack(expand=True)
            self.setup_bottom_panel(self.current_frame)
            return
        
        content_frame = tk.Frame(self.current_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        info_frame = tk.Frame(content_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text="MBR (Master Boot Record) - первый сектор жесткого диска,\nсодержащий код для загрузки операционной системы.", 
                bg='white', font=('Arial', 9), justify=tk.LEFT).pack()
        
        disk_frame = tk.Frame(content_frame, bg='white')
        disk_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(disk_frame, text="Физический диск:", bg='white').pack(side=tk.LEFT)
        
        disks = self.get_physical_disks()
        disk_var = tk.StringVar(value=disks[0] if disks else "")
        disk_combo = ttk.Combobox(disk_frame, textvariable=disk_var, values=disks, state="readonly", width=20)
        disk_combo.pack(side=tk.LEFT, padx=10)
        
        buttons_frame = tk.Frame(content_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(buttons_frame, text="Создать бэкап MBR", 
                 command=lambda: self.create_mbr_backup(disk_var.get()),
                 bg='#f0f0f0', fg='black', font=('Arial', 10),
                 relief='solid', bd=1, height=2).pack(fill=tk.X, pady=5)
        
        tk.Button(buttons_frame, text="Восстановить MBR из бэкапа", 
                 command=lambda: self.restore_mbr_from_file(disk_var.get()),
                 bg='#f0f0f0', fg='black', font=('Arial', 10),
                 relief='solid', bd=1, height=2).pack(fill=tk.X, pady=5)
        
        tk.Button(buttons_frame, text="Восстановить стандартный MBR", 
                 command=lambda: self.restore_standard_mbr(disk_var.get()),
                 bg='#ffcccc', fg='black', font=('Arial', 10),
                 relief='solid', bd=1, height=2).pack(fill=tk.X, pady=5)
        
        log_frame = tk.Frame(content_frame, bg='white')
        log_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        tk.Label(log_frame, text="Лог операций:", bg='white', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.mbr_log = tk.Text(log_frame, wrap=tk.WORD, width=60, height=8,
                              bg='#f8f8f8', fg='black', font=('Arial', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.mbr_log.yview)
        self.mbr_log.configure(yscrollcommand=scrollbar.set)
        
        self.mbr_log.insert('1.0', "Готов к работе...\n")
        self.mbr_log.config(state=tk.DISABLED)
        
        self.mbr_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.setup_bottom_panel(self.current_frame)

    def get_physical_disks(self):
        try:
            disks = []
            for drive in range(5):
                disk_path = f"\\\\.\\PhysicalDrive{drive}"
                try:
                    with open(disk_path, 'rb') as f:
                        pass
                    disks.append(disk_path)
                except:
                    continue
            return disks if disks else ["\\\\.\\PhysicalDrive0"]
        except:
            return ["\\\\.\\PhysicalDrive0"]

    def create_mbr_backup(self, disk):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".bin",
                filetypes=[("MBR Backup files", "*.bin"), ("All files", "*.*")],
                title="Сохранить бэкап MBR",
                initialfile=f"mbr_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
            )
            if file_path:
                with open(disk, 'rb') as disk_file:
                    mbr_data = disk_file.read(512)
                
                with open(file_path, 'wb') as f:
                    f.write(mbr_data)
                
                self.log_mbr(f"Бэкап MBR создан: {file_path}")
                messagebox.showinfo("Успех", f"Бэкап MBR создан:\n{file_path}")
        except Exception as e:
            self.log_mbr(f"Ошибка создания бэкапа: {e}")
            messagebox.showerror("Ошибка", f"Ошибка создания бэкапа: {e}")

    def restore_mbr_from_file(self, disk):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("MBR Backup files", "*.bin"), ("All files", "*.*")],
                title="Выберите файл бэкапа MBR"
            )
            if file_path:
                if messagebox.askyesno("Подтверждение", 
                                      "ВНИМАНИЕ: Восстановление MBR может быть опасным!\nЭто может привести к потере данных и сделать систему незагружаемой!\nПродолжить?"):
                    with open(file_path, 'rb') as f:
                        mbr_data = f.read()
                    
                    with open(disk, 'r+b') as disk_file:
                        disk_file.write(mbr_data)
                    
                    self.log_mbr(f"MBR восстановлен из: {file_path}")
                    messagebox.showinfo("Успех", "MBR успешно восстановлен!\nМожет потребоваться перезагрузка системы.")
        except Exception as e:
            self.log_mbr(f"Ошибка восстановления: {e}")
            messagebox.showerror("Ошибка", f"Ошибка восстановления: {e}")

    def restore_standard_mbr(self, disk):
        if messagebox.askyesno("ВНИМАНИЕ", 
                              "Это восстановит стандартный MBR Windows.\n"
                              "Это может сделать систему незагружаемой если у вас:\n"
                              "- Linux или другая ОС\n"
                              "- Нестандартный загрузчик\n"
                              "- Несколько ОС\n\n"
                              "Продолжить?"):
            try:
                result = subprocess.run(
                    ['bootrec', '/fixmbr'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    self.log_mbr("Стандартный MBR восстановлен")
                    messagebox.showinfo("Успех", "Стандартный MBR успешно восстановлен!")
                else:
                    self.log_mbr(f"Ошибка восстановления MBR: {result.stderr}")
                    messagebox.showerror("Ошибка", f"Не удалось восстановить MBR: {result.stderr}")
                    
            except Exception as e:
                self.log_mbr(f"Ошибка восстановления стандартного MBR: {e}")
                messagebox.showerror("Ошибка", f"Не удалось восстановить стандартный MBR: {e}")

    def log_mbr(self, message):
        self.mbr_log.config(state=tk.NORMAL)
        self.mbr_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.mbr_log.see(tk.END)
        self.mbr_log.config(state=tk.DISABLED)

    def setup_title_bar(self, title):
        title_bar = tk.Frame(self.current_frame, bg='#e0e0e0', height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        back_btn = tk.Button(title_bar, text="← Назад", command=self.setup_main_menu,
                           bg='#e0e0e0', fg='black', font=('Arial', 9),
                           relief='flat', bd=0)
        back_btn.pack(side=tk.LEFT, padx=5, pady=3)
        back_btn.bind('<Enter>', lambda e: back_btn.config(bg='#d0d0d0'))
        back_btn.bind('<Leave>', lambda e: back_btn.config(bg='#e0e0e0'))
        
        title_label = tk.Label(title_bar, text=title, 
                             bg='#e0e0e0', fg='black', font=('Arial', 10, 'bold'))
        title_label.pack(expand=True, pady=3)
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.on_move)
        title_label.bind('<ButtonRelease-1>', self.stop_move)
        
        minimize_btn = tk.Label(title_bar, text="_", bg='#e0e0e0', fg='black', 
                           font=('Arial', 16, 'bold'), cursor='hand2')
        minimize_btn.pack(side=tk.RIGHT, padx=5)
        minimize_btn.bind('<Button-1>', lambda e: self.root.iconify())
        minimize_btn.bind('<Enter>', lambda e: minimize_btn.config(bg='#d0d0d0'))
        minimize_btn.bind('<Leave>', lambda e: minimize_btn.config(bg='#e0e0e0'))
        
        close_btn = tk.Label(title_bar, text="×", bg='#e0e0e0', fg='black', 
                           font=('Arial', 16, 'bold'), cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind('<Button-1>', lambda e: self.safe_exit())
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#ff4444', fg='white'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='#e0e0e0', fg='black'))

    def safe_exit(self):
        try:
            keyboard.unhook_all()
        except:
            pass
            
        if self.process_update_job:
            self.root.after_cancel(self.process_update_job)
        if hasattr(self, 'cmd_process'):
            try:
                self.cmd_process.terminate()
            except:
                pass
        self.root.quit()
        self.root.destroy()

    def clear_frame(self):
        if self.process_update_job:
            self.root.after_cancel(self.process_update_job)
            self.process_update_job = None
        
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(expand=True, fill=tk.BOTH)

    def clear_startup_content(self):
        for widget in self.startup_content.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
            
        app = NyaUnlock()
        app.root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter...")