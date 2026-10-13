Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")
strDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

strPythonW = objShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python313\pythonw.exe"

If objFSO.FileExists(strPythonW) Then
    objShell.Run """" & strPythonW & """ """ & strDir & "\main.py""", 0, False
Else
    objShell.Run """" & strDir & "\uruchom.bat""", 1, False
End If
