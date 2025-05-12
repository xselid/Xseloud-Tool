import os
import sys
import ctypes
import winreg
import subprocess
import shutil
import psutil
import platform
import win32api
import win32con
import win32security
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return True

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def disable_uac():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True, "UAC успешно отключён. Перезагрузите компьютер."
    except Exception as e:
        return False, f"Ошибка: {e}"

def unlock_policies():
    try:
        # Разблокировка редактора групповых политик
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Policies\Microsoft\MMC\{8FC0B734-A0E1-11D1-A7D3-0000F87571E3}",
                0,
                winreg.KEY_SET_VALUE
            )
        except FileNotFoundError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Policies\Microsoft\MMC\{8FC0B734-A0E1-11D1-A7D3-0000F87571E3}"
            )
        winreg.SetValueEx(key, "Restrict_Run", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        # Разблокировка панели управления
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                0,
                winreg.KEY_SET_VALUE
            )
        except FileNotFoundError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            )
        winreg.SetValueEx(key, "NoControlPanel", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        # Разблокировка диспетчера задач
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                0,
                winreg.KEY_SET_VALUE
            )
        except FileNotFoundError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            )
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        # Разблокировка командной строки
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Policies\Microsoft\Windows\System",
                0,
                winreg.KEY_SET_VALUE
            )
        except FileNotFoundError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Policies\Microsoft\Windows\System"
            )
        winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        # Разблокировка редактора реестра
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                0,
                winreg.KEY_SET_VALUE
            )
        except FileNotFoundError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            )
        winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        # Разблокировка контекстного меню
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                0,
                winreg.KEY_SET_VALUE
            )
        except FileNotFoundError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            )
        winreg.SetValueEx(key, "NoViewContextMenu", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        return True, "Ограничения в реестре успешно сняты!"
    except Exception as e:
        return False, f"Ошибка при разблокировке: {e}"

def enable_windows_features():
    try:
        # Включение всех функций Windows
        subprocess.run("dism /online /enable-feature /all", shell=True)
        
        # Включение .NET Framework
        subprocess.run("dism /online /enable-feature /featurename:NetFx3 /all", shell=True)
        
        return True, "Функции Windows успешно включены!"
    except Exception as e:
        return False, f"Ошибка при включении функций: {e}"

def clear_temp_files():
    try:
        temp_dirs = [
            os.environ.get('TEMP'),
            os.path.join(os.environ.get('WINDIR'), 'Temp'),
            os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp'),
            os.path.join(os.environ.get('WINDIR'), 'Prefetch'),
            os.path.join(os.environ.get('WINDIR'), 'SoftwareDistribution', 'Download')
        ]
        
        total_files = 0
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    total_files += len(files)
        
        deleted_files = 0
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            os.unlink(os.path.join(root, file))
                            deleted_files += 1
                        except:
                            pass
        
        return True, f"Удалено {deleted_files} из {total_files} временных файлов!"
    except Exception as e:
        return False, f"Ошибка при очистке: {e}"

def optimize_system():
    try:
        # Отключение ненужных служб
        services = [
            "DiagTrack", "dmwappushservice", "MapsBroker", "WSearch", "SysMain",
            "WMPNetworkSvc", "WbioSrvc", "WwanSvc", "XblAuthManager", "XblGameSave"
        ]
        for service in services:
            try:
                win32serviceutil.StopService(service)
                win32serviceutil.ChangeServiceConfig(
                    service,
                    win32service.SERVICE_NO_CHANGE,
                    win32service.SERVICE_DISABLED
                )
            except:
                pass
        
        # Очистка кэша DNS
        subprocess.run("ipconfig /flushdns", shell=True)
        
        # Оптимизация файла подкачки
        subprocess.run("wmic computersystem set AutomaticManagedPagefile=False", shell=True)
        subprocess.run("wmic pagefileset where name='C:\\pagefile.sys' set InitialSize=4096,MaximumSize=8192", shell=True)
        
        # Очистка журнала событий
        subprocess.run("wevtutil el | Foreach-Object {wevtutil cl \"$_\"}", shell=True)
        
        return True, "Система оптимизирована!"
    except Exception as e:
        return False, f"Ошибка при оптимизации: {e}"

def show_system_info():
    try:
        info = []
        info.append(f"Операционная система: {platform.system()} {platform.release()}")
        info.append(f"Процессор: {platform.processor()}")
        info.append(f"Оперативная память: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
        info.append(f"Свободно места на диске C: {round(shutil.disk_usage('C:').free / (1024**3), 2)} GB")
        info.append(f"Загрузка CPU: {psutil.cpu_percent()}%")
        info.append(f"Загрузка памяти: {psutil.virtual_memory().percent}%")
        info.append(f"Имя компьютера: {socket.gethostname()}")
        info.append(f"IP адрес: {socket.gethostbyname(socket.gethostname())}")
        return True, info
    except Exception as e:
        return False, [f"Ошибка при получении информации: {e}"]

def repair_system():
    try:
        # Проверка системных файлов
        subprocess.run("sfc /scannow", shell=True)
        
        # Проверка диска
        subprocess.run("chkdsk C: /f", shell=True)
        
        # Восстановление компонентов Windows
        subprocess.run("dism /online /cleanup-image /restorehealth", shell=True)
        
        # Очистка и восстановление хранилища компонентов
        subprocess.run("DISM /Online /Cleanup-Image /StartComponentCleanup", shell=True)
        subprocess.run("DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase", shell=True)
        
        return True, "Система успешно проверена и восстановлена!"
    except Exception as e:
        return False, f"Ошибка при восстановлении: {e}"

def disable_windows_defender():
    try:
        # Отключение Windows Defender
        subprocess.run("powershell Set-MpPreference -DisableRealtimeMonitoring $true", shell=True)
        subprocess.run("powershell Set-MpPreference -DisableIOAVProtection $true", shell=True)
        
        # Отключение через реестр
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Policies\Microsoft\Windows Defender",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        
        return True, "Windows Defender успешно отключен!"
    except Exception as e:
        return False, f"Ошибка при отключении Windows Defender: {e}"

def optimize_network():
    try:
        # Оптимизация сетевых настроек
        subprocess.run("netsh int tcp set global autotuninglevel=normal", shell=True)
        subprocess.run("netsh int tcp set global chimney=enabled", shell=True)
        subprocess.run("netsh int tcp set global dca=enabled", shell=True)
        subprocess.run("netsh int tcp set global netdma=enabled", shell=True)
        subprocess.run("netsh int tcp set global ecncapability=enabled", shell=True)
        
        # Очистка DNS кэша
        subprocess.run("ipconfig /flushdns", shell=True)
        subprocess.run("ipconfig /registerdns", shell=True)
        subprocess.run("ipconfig /release", shell=True)
        subprocess.run("ipconfig /renew", shell=True)
        
        return True, "Сеть успешно оптимизирована!"
    except Exception as e:
        return False, f"Ошибка при оптимизации сети: {e}"

def disable_telemetry():
    try:
        # Отключение телеметрии
        subprocess.run("sc stop DiagTrack", shell=True)
        subprocess.run("sc stop dmwappushservice", shell=True)
        
        # Отключение через реестр
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        
        return True, "Телеметрия успешно отключена!"
    except Exception as e:
        return False, f"Ошибка при отключении телеметрии: {e}"

def optimize_gaming():
    try:
        # Оптимизация для игр
        subprocess.run("bcdedit /set useplatformclock false", shell=True)
        subprocess.run("bcdedit /set disabledynamictick yes", shell=True)
        subprocess.run("bcdedit /set tscsyncpolicy Enhanced", shell=True)
        
        # Отключение ненужных служб для игр
        gaming_services = [
            "SysMain", "DiagTrack", "WSearch", "WbioSrvc",
            "WwanSvc", "XblAuthManager", "XblGameSave"
        ]
        for service in gaming_services:
            try:
                win32serviceutil.StopService(service)
                win32serviceutil.ChangeServiceConfig(
                    service,
                    win32service.SERVICE_NO_CHANGE,
                    win32service.SERVICE_DISABLED
                )
            except:
                pass
        
        return True, "Система оптимизирована для игр!"
    except Exception as e:
        return False, f"Ошибка при оптимизации для игр: {e}" 