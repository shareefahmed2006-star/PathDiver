import os
import shutil
import zipfile

def create_package():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    staging = os.path.join(base_dir, 'package_staging')
    if os.path.exists(staging):
        shutil.rmtree(staging)
    os.makedirs(staging, exist_ok=True)

    # 1. Copy PathDiver.exe
    exe_src = os.path.join(base_dir, 'dist', 'PathDiver.exe')
    if not os.path.exists(exe_src):
        raise FileNotFoundError(f"Missing {exe_src}")
    shutil.copy2(exe_src, os.path.join(staging, 'PathDiver.exe'))

    # 2. Copy PathDiver_Offline.html
    shutil.copy2(os.path.join(base_dir, 'PathDiver_Offline.html'), os.path.join(staging, 'PathDiver_Offline.html'))

    # 3. Copy README.md
    shutil.copy2(os.path.join(base_dir, 'README.md'), os.path.join(staging, 'README.md'))

    # 4. Create Click_To_Start_PathDiver.bat
    bat_content = (
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File\"\r\n"
        "start \"\" \"%~dp0PathDiver.exe\"\r\n"
        "exit\r\n"
    )
    with open(os.path.join(staging, 'Click_To_Start_PathDiver.bat'), 'w', encoding='utf-8') as f:
        f.write(bat_content)

    # 5. Create How_To_Run.txt
    instructions = (
        "==================================================\r\n"
        "PathDiver Desktop Application\r\n"
        "Intelligent File Traversal & Storage Manager\r\n"
        "==================================================\r\n\r\n"
        "TO RUN ON WINDOWS:\r\n"
        "Double-click 'Click_To_Start_PathDiver.bat' (or run 'PathDiver.exe' directly).\r\n\r\n"
        "BONUS (CROSS-PLATFORM / ZERO-SETUP):\r\n"
        "Double-click 'PathDiver_Offline.html' to open and run PathDiver in any web browser without needing any software installed!\r\n\r\n"
        "FEATURES INCLUDED:\r\n"
        "1. Find & Peek (In-content search inside PDF, DOCX, Notebooks, Code + <15ms smart peek)\r\n"
        "2. 2-Phase Heuristic Duplicate Detector (Exact copies + edited version drafts)\r\n"
        "3. 1-Click Folder Organizer (With 100% reversible undo)\r\n"
        "4. Developer & Cache Junk Sweeper (Reclaim space to Recycle Bin in <2s)\r\n"
        "5. Developer View (Explicit DFS LIFO Stack Visualizer & Hierarchy Tree)\r\n\r\n"
        "Zero configuration, zero telemetry, 100% privacy-first.\r\n"
        "==================================================\r\n"
    )
    with open(os.path.join(staging, 'How_To_Run.txt'), 'w', encoding='utf-8') as f:
        f.write(instructions)

    # 6. Build the ZIP
    main_zip = os.path.join(base_dir, 'PathDiver_Ready_To_Send.zip')
    with zipfile.ZipFile(main_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(staging):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, staging)
                z.write(full, rel)

    print(f"Created main ZIP: {main_zip} ({os.path.getsize(main_zip)} bytes)")

    # 7. Copy to Desktop and Downloads for easy sending
    user_home = os.path.expanduser('~')
    destinations = [
        r'C:\Users\Shareef\Downloads\PathDiver_Ready_To_Send.zip',
        os.path.join(user_home, 'Desktop', 'PathDiver_Ready_To_Send.zip'),
        os.path.join(user_home, 'OneDrive', 'Desktop', 'PathDiver_Ready_To_Send.zip'),
        r'C:\Users\Shareef\Downloads\Desktop\PathDiver_Ready_To_Send.zip'
    ]

    for dest in destinations:
        dest_dir = os.path.dirname(dest)
        if os.path.exists(dest_dir):
            try:
                shutil.copy2(main_zip, dest)
                print(f"Copied package to: {dest}")
            except Exception as e:
                print(f"Could not copy to {dest}: {e}")

    # Copy the fresh PathDiver.exe directly to desktop as well
    for dt in [os.path.join(user_home, 'Desktop'), os.path.join(user_home, 'OneDrive', 'Desktop')]:
        if os.path.exists(dt):
            try:
                shutil.copy2(exe_src, os.path.join(dt, 'PathDiver.exe'))
                print(f"Updated Desktop PathDiver.exe at: {dt}")
            except Exception as e:
                print(f"Could not copy PathDiver.exe to {dt}: {e}")

    # Clean staging
    shutil.rmtree(staging, ignore_errors=True)

if __name__ == '__main__':
    create_package()
