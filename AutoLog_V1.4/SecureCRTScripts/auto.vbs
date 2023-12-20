Dim workPath

workPath = Createobject("Scripting.FileSystemObject").GetFile(crt.ScriptFullName).ParentFolder.Path

Set fso = CreateObject("Scripting.FilesyStemObject")
	Str = fso.OpenTextFile(workPath & "/crtScriptLib.vbs", 1).ReadAll
	ExecuteGlobal Str
Set fso = Nothing


'crt.Sleep GetRandMath(11,30)

Sub Main()

	szPrompt = "*****"
	
	While GetFlag(workPath) = "1"
		If crt.screen.WaitForString(szPrompt, 10, false, true) = true Then
			
		End If			
	Wend
    	
	'¶Ï¿ªÁ¬½Ó
	crt.Session.Disconnect()
End Sub

