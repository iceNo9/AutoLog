Dim workPath

workPath = Createobject("Scripting.FileSystemObject").GetFile(crt.ScriptFullName).ParentFolder.Path

Set fso = CreateObject("Scripting.FilesyStemObject")
	Str = fso.OpenTextFile(workPath & "/crtScriptLib.vbs", 1).ReadAll
	ExecuteGlobal Str
Set fso = Nothing

Sub Main()

    Dim szPrompt, szResult
    Dim objTab
		
	'�����ؼ���
    szPrompt = "Engine Log Start"

    Set objTab = crt.GetScriptTab
    objTab.Screen.Synchronous = True
    objTab.Screen.IgnoreEscape = True
    
	'Ҫ���͵�����
    szCommand = "cmddsp"
	
	'crt.Sleep GetRandMath(1,10)
 
	While GetFlag(workPath) = "1"
		If crt.screen.WaitForString(szPrompt, 10, false, true) = true Then
			objTab.Screen.Send szCommand & vbCrLf
		End If			
	Wend
    
	crt.Session.Disconnect()
End Sub
