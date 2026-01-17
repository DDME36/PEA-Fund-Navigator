Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get current directory
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strBat = strPath & "\setup_auto_run.bat"

' Run as administrator
objShell.ShellExecute "cmd.exe", "/c """ & strBat & """", "", "runas", 1
