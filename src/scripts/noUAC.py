import subprocess
import ctypes
import sys

def is_admin():

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def disable_UAC():
    if not is_admin():
        print("Требуются права администратора. Перезапуск...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    command1 = r'reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /f'
    command2 = r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 0 /f'

    try:
        print("Удаление текущего значения EnableLUA...")
        subprocess.run(command1, check=True, shell=True)
        print("Добавление нового значения EnableLUA = 0...")
        subprocess.run(command2, check=True, shell=True)
        print("UAC успешно отключён (потребуется перезагрузка).")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e}")

