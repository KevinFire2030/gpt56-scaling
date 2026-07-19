Option Explicit
Dim app, pres, fso, inFile, outDir
Set fso = CreateObject("Scripting.FileSystemObject")
inFile = fso.GetAbsolutePathName("deck.pptx")
outDir = fso.GetAbsolutePathName("preview")
If Not fso.FolderExists(outDir) Then fso.CreateFolder(outDir)
Set app = CreateObject("PowerPoint.Application")
app.Visible = True
Set pres = app.Presentations.Open(inFile, False, False, False)
pres.Export outDir, "PNG", 1600, 900
pres.Close
app.Quit
WScript.Echo "Rendered to " & outDir
