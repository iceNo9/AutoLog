Dim workPath

workPath = Createobject("Scripting.FileSystemObject").GetFile(crt.ScriptFullName).ParentFolder.Path

Set fso = CreateObject("Scripting.FilesyStemObject")
	Str = fso.OpenTextFile(workPath & "/crtScriptLib.vbs", 1).ReadAll
	ExecuteGlobal Str
Set fso = Nothing

Sub Main()

    Dim szPrompt, szResult
    Dim objTab

	'触发关键词
    szPrompt = "nvram.db successed"

    Set objTab = crt.GetScriptTab
    objTab.Screen.Synchronous = True    
    objTab.Screen.IgnoreEscape = True
    
	'要发送的命令
	szCommand = "root"
	
	'crt.Sleep GetRandMath(1,10)
        
	While GetFlag(workPath)	= "1"		
		If crt.screen.WaitForString(szPrompt, 10, false, true) = true Then
			objTab.Screen.Send szCommand & vbCrLf
		End If				
	Wend
	
	crt.Session.Disconnect()
End Sub

