Set filesystem = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
projectRoot = filesystem.GetParentFolderName(WScript.ScriptFullName)
pythonWindowed = projectRoot & "\.venv\Scripts\pythonw.exe"

If Not filesystem.FileExists(pythonWindowed) Then
    MsgBox "Application environment is missing. Run install_dependencies.bat first.", vbCritical, "Topological Sort Application"
    WScript.Quit 1
End If

shell.CurrentDirectory = projectRoot
shell.Run """" & pythonWindowed & """ """ & projectRoot & "\run_app.pyw" & """", 0, False
