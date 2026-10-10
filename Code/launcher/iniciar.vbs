Option Explicit

Dim shell
Dim fso
Dim root
Dim pythonw
Dim launcher

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))

pythonw = root & "\.venv\Scripts\pythonw.exe"
launcher = root & "\launcher\launcher.pyw"

If Not fso.FileExists(pythonw) Then
    MsgBox "pythonw.exe não encontrado:" & vbCrLf & pythonw, 16, "ESP32 IoT"
    WScript.Quit 1
End If

If Not fso.FileExists(launcher) Then
    MsgBox "launcher.pyw não encontrado:" & vbCrLf & launcher, 16, "ESP32 IoT"
    WScript.Quit 1
End If

shell.CurrentDirectory = root

shell.Run """" & pythonw & """ """ & launcher & """", 0, False

Set fso = Nothing
Set shell = Nothing