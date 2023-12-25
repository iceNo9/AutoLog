'On error resume Next

'使用gb2312打开此文件

Dim is_debug
Dim cmd, log_index, is_write_info
Dim path_script_ini, path_flag, path_log, path_save
Dim path_storage, path_storage_DC, path_storage_EC, path_storage_OTHERS

Const ForReading = 1, ForWriting =2 , ForAppending = 8
Const TristateUseDefault = -2

is_debug = False
Call main

sub debug(rv_str)
	if(is_debug) Then
		MsgBox(rv_str)
	end if
end sub

function main()
	InitPara
	RunCmd
end function

sub InitPara()
	'初始化入参
	set argus=wscript.arguments
	cmd = argus(0)
	log_index = argus(1)
	is_write_info = argus(2)

	'依赖路径初始化
	path_script_ini = createobject("Scripting.FileSystemObject").GetFolder(".").Path & "\config.ini"
	path_flag = createobject("Scripting.FileSystemObject").GetFolder(".").Path & "\..\Scripts\"
	path_log = GetINIStringVirtual("LogPath", "val", "", path_script_ini)
	path_save = GetINIStringVirtual("SavePath", "val", "", path_script_ini)
end sub

sub RunCmd()
	select case cmd
		case 0'重置
			Call ResetFlag
		case 1'收集日志
			Call SaveLog(0)
		case 2'截断日志
			Call CutLog
		case 4'收集日志&添加info文本
			Call SaveLog(1)
		case 5'删除日志	
			Call DeleteLog
		case 6'管理日志(按日期收纳)
			Call ManageLog
		case 7'打开日志保存路径
			Call OpenSavePath
		case else
			
	end select
end sub

function ResetFlag()
	Call SetFlag(1)
end function

function SaveLog(rv_mode)
	' rv_mode:0(正常收集), :1(创建info一次)
	Call SetFlag(0)
	Call InifStorage
	Call LogFileHandle(0)
	if is_write_info = 1 Or rv_mode = 1 Then
		CreateInfo
	end if
end function

function CutLog()
	Call SetFlag(0)
end function

function DeleteLog()
	Call SetFlag(0)
	Call LogFileHandle(1)
end function

function ManageLog()
	Dim objFSO, objFolder, item, is_executed
	Dim str_year, str_month, str_day
	Dim folder_name
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	Set objFolder = objFSO.getfolder(path_save)
	For Each item In objFolder.subfolders
		If InStr(item.name, "NO") Then
			str_year = Mid(item.name, 1, 4)
			str_month = Mid(item.name, 5, 2)
			str_day =  Mid(item.name, 7, 2)			
			folder_name = str_year & "年" & str_month & "月" & str_day & "日"
			
			If Not objFso.FolderExists(path_save & folder_name) Then
				MyCreateFolder(path_save & folder_name)
			End If

			Call XCopy(objFSO, item.path, path_save & folder_name & "\" & item.name, True)
			objFso.DeleteFolder item
		End If
	Next
	set objFolder = Nothing
	set objFSO = Nothing
end function

function OpenSavePath()
	Set objShell = CreateObject("Wscript.Shell")
	strPath = "explorer.exe /e," & path_save
	objShell.Run strPath
end function

'设置文件标志
Function SetFlag(var)
	Dim objFSO, objFile, txtFile, path
	Set objFSO = CreateObject("scripting.filesystemobject")
	path = path_flag & "config.txt"
	
	If (objFSO.FileExists(path)) = 0 Then
		'Create the file if there is no the text file
		objFSO.CreateTextFile(path)
		Set objFile = objFSO.GetFile(path)
		'Open the txt file
		Set txtFile = objFile.OpenAsTextStream(ForWriting, TristateUseDefault)
		txtFile.Write var
		txtFile.Close
	Else 
		'open the text file directly if the file is existed
		Set txtFile = objFSO.OpenTextFile(path, ForWriting, False)
		txtFile.Write var
		txtFile.Close
	End If 
	wscript.sleep(100)
End Function

'读取文件标志
Function GetFlag()
	Dim objFSO, objFile, txtFile, path
	Set objFSO = CreateObject("scripting.filesystemobject")
	path = path_flag & "config.txt"
	
	Set objFile = objFSO.GetFile(path)
	'Open the txt file
	Set txtFile = objFile.OpenAsTextStream(ForReading, TristateUseDefault)
	GetFlag = txtFile.Read(1)	
	
	Set txtFile = Nothing
	Set objFile = Nothing
	Set objFSO = Nothing
End Function


'获取格式化的Now()
Function GetFormatNow
	Dim dd, mm, yy, hh, nn, ss
	Dim datevalue, timevalue, dtsnow, dtsvalue

	'Store DateTimeStamp once.
	dtsnow = Now()

	'Individual date components
	dd = Right("00" & Day(dtsnow), 2)
	mm = Right("00" & Month(dtsnow), 2)
	yy = Year(dtsnow)
	hh = Right("00" & Hour(dtsnow), 2)
	nn = Right("00" & Minute(dtsnow), 2)
	ss = Right("00" & Second(dtsnow), 2)

	'Build the date string in the format yyyy-mm-dd
	datevalue = yy & mm & dd
	'Build the time string in the format hh:mm:ss
	timevalue = hh & nn & ss
	'Concatenate both together to build the timestamp yyyy-mm-dd hh:mm:ss
	dtsvalue = datevalue & "_" & timevalue
	
	GetFormatNow = dtsvalue
End Function

'初始化存储位置
function InifStorage()
	Dim folder_name
	'根据时间+序列号创建序号文件夹及子文件夹DC/EC/OTHERS
	folder_name = GetFormatNow & "NO." & log_index & "\"
	path_storage = path_save & folder_name
	path_storage_DC = path_storage & "DC"
	path_storage_EC = path_storage & "EC"
	path_storage_OTHERS = path_storage & "OTHERS"
	MyCreateFolder(path_storage)
end function

'日志文件处理
function LogFileHandle(rv_mode)
	'mode:0(通常), 1(仅删除)
	Dim objFSO, objFolder, item, is_executed
	is_init = False
	'遍历日志文件夹，将含有相应关键词的文件夹移动到存储位置的相对应的路径下
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	Set objFolder = objFSO.getfolder(path_log)
	For Each item In objFolder.subfolders
		is_executed = False
		If is_executed = False Then
			If InStr(item.name, "DC") Then			
				If rv_mode = 0 Then
					If Not objFso.FolderExists(path_storage_DC) Then
						MyCreateFolder(path_storage_DC)
					End If
					Call XCopy(objFSO, item.path, path_storage_DC & "\" & item.name, True)
					debug(item.path)
					debug(path_storage_DC)
				End If
				objFso.DeleteFolder item
				is_executed = True
			End if
		End If

		If is_executed = False Then
			If InStr(item.name, "EC") Then			
				If rv_mode = 0 Then
					If Not objFso.FolderExists(path_storage_EC) Then
						MyCreateFolder(path_storage_EC)
					End If					
					Call XCopy(objFSO, item.path, path_storage_EC & "\" & item.name, True)
				End If
				objFso.DeleteFolder item
				is_executed = True
			End if
		End If

		If is_executed = False Then
			If InStr(item.name, "OTHER") Then			
				If rv_mode = 0 Then
					If Not objFso.FolderExists(path_storage_OTHERs) Then
						MyCreateFolder(path_storage_OTHERS)
					End If
					Call XCopy(objFSO, item.path, path_storage_OTHERS & "\" & item.name, True)
				End If
				objFso.DeleteFolder item
				is_executed = True
			End if
		End If
	Next
	set objFolder = Nothing
	set objFSO = Nothing
end function

'删除字符串最右边的字符chs
Function MyRTrim(src, chs)                  '删除字符串最右边的字符chs(可多个)
    Dim pos, sLeft
    src = Trim(src)
    pos = InStrRev(src, chs)                '查找最后一个字符chs
    if(pos > 0 and Len(Mid(src, pos+1)) = 0) Then
        sLeft = Left(src, pos - 1)          '去除最后一个chs
        MyRTrim = MyRTrim(sLeft, chs)       '去除尾部的chs
    else
        MyRTrim = src
    end if
End Function

'创建目录，如果父目录不存在，则创建：实现一次性创建所有父级目录
Sub MyCreateFolder(sPath)
    Dim fs
    set fs = CreateObject("Scripting.FileSystemObject")
    if(Len(sPath) > 0 And fs.FolderExists(sPath) = False) Then
        Dim pos, sLeft
        pos = InStrRev(sPath, "\")
        if(pos <> 0) Then
            sLeft = Left(sPath, pos - 1)
            MyCreateFolder sLeft            '先创建父目录
        end if
		if fs.FolderExists(sPath) = False Then
			fs.CreateFolder sPath               '再创建本目录
		end if        
    end if
    set fs = Nothing
End Sub

'********************************************************************
'* Function :     XCopy
'*
'* Purpose:  复制文件和目录树。
'*
'* Input:    fso            FileSystemObject 对象实例
'*           source         指定要复制的文件。
'*           destination    指定新文件的位置和/或名称。
'*           overwrite      是否覆盖已存在文件。 Ture 覆盖， False 跳过
'*
'* Output:   返回复制的文件个数
'*
'********************************************************************
Function XCopy(fso, source, destination, overwrite)
    Dim s, d, f, l, CopyCount    
	
	If fso.FolderExists(source) Then	
	
		Set s = fso.GetFolder(source)
		If Not fso.FolderExists(destination) Then
			fso.CreateFolder destination
		End If
		Set d = fso.GetFolder(destination)

		CopyCount = 0
		For Each f In s.Files
			l = d.Path & "\" & f.Name
			If Not fso.FileExists(l) Or overwrite Then
				If fso.FileExists(l) Then
					fso.DeleteFile l, True
				End If
				f.Copy l, True
				CopyCount = CopyCount + 1
			End If
		Next

		For Each f In s.SubFolders
			CopyCount = CopyCount + XCopy(fso, f.Path, d.Path & "\" & f.Name, overwrite)
		Next

		XCopy = CopyCount
	End If
End Function

'创建info文本
Function CreateInfo
	Dim file_name, file_path
	Dim objFSO, objFile

	file_name = "LogInfo.txt"
	file_path = path_storage & file_name
	
	set objFSO = CreateObject("Scripting.FileSystemObject")
	
	if(objFSO.FileExists(file_path)) Then                     '检测文件是否存在
		MsgBox "已存在info文本"
	end if

	set objFile = objFSO.CreateTextFile(file_path, True, True)    '第二个参数不写的话，默认为True(会覆盖原文件)
	
	'ts.WriteLine "LOG by 胡宏安"
	objFile.Close
	set objFile = Nothing
	set objFSO = Nothing	
End Function

'打开文本文档
Function OpenInfo	
	Dim file_path, ws

	file_path path_storage & "\LogInfo.txt"
	set ws=CreateObject("wscript.shell")
	ws.run mu_sFileName,1,true
	set ws = Nothing
End Function

Function GetClipboardText()   'ie剪切读取板信息，ie设置允许对剪切板进行编程
    Set objIE = CreateObject("InternetExplorer.Application") 
    objIE.Navigate("about:blank") 
    GetClipboardText = objIE.Document.ParentWindow.ClipboardData.GetData("text") 
    objIE.Quit 
	Set objIE = Nothing
End Function

Function GetClipboardText1()   'Microsoft Forms 2.0 Object Library剪切读取板信息,需要office
	Dim Form, TextBox
	Set Form = CreateObject("Forms.Form.1")
	Set TextBox = Form.Controls.Add("Forms.TextBox.1").Object
	TextBox.MultiLine = True
	If TextBox.CanPaste Then
		TextBox.Paste
		GetClipboardText1 = TextBox.Text
	End If
	Set TextBox = Nothing
	Set Form = Nothing
End Function

Function GetClipboardText2()   'word剪切读取板信息，无法读取表格
	Dim Word
	Set Word = CreateObject("Word.Application")
	Word.Documents.Add
	Word.Selection.PasteAndFormat(wdFormatPlainText)
	Word.Selection.WholeStory
	GetClipboardText2 = Word.Selection.Text
	Word.Quit False
	Set Word = Nothing
End Function



'*************************************************ini 库开始*************************************************
Sub WriteINIStringVirtual(Section, KeyName, value, FileName)
	WriteINIString Section, KeyName, value, FileName
End Sub

Function GetINIStringVirtual(Section, KeyName, Default, FileName)
	GetINIStringVirtual = GetINIString(Section, KeyName, Default, FileName)
End Function


' Work with INI files In VBS (ASP/WSH)
' v1.00
' 2003 Antonin Foller, PSTRUH Software, http://www.pstruh.cz
' Function GetINIString(Section, KeyName, Default, FileName)
' Sub WriteINIString(Section, KeyName, value, FileName)

Sub WriteINIString(Section, KeyName, value, FileName)
Dim INIContents, PosSection, PosEndSection

'Get contents of the INI file As a string
INIContents = GetFile(FileName)
 
'Find section
PosSection = InStr(1, INIContents, "[" & Section & "]", vbTextCompare)
If PosSection>0 Then
	'Section exists. Find end of section
	PosEndSection = InStr(PosSection, INIContents, vbCrLf & "[")
	'?Is this last section?
If PosEndSection = 0 Then PosEndSection = Len(INIContents)+1
 
'Separate section contents
Dim OldsContents, NewsContents, Line
Dim sKeyName, Found
OldsContents = Mid(INIContents, PosSection, PosEndSection - PosSection)
OldsContents = split(OldsContents, vbCrLf)
 
'Temp variable To find a Key
sKeyName = LCase(KeyName & "=")
 
'Enumerate section lines
For Each Line In OldsContents
If LCase(Left(Line, Len(sKeyName))) = sKeyName Then
Line = KeyName & "=" & value
Found = True
End If
NewsContents = NewsContents & Line & vbCrLf
Next
 
If isempty(Found) Then
'key Not found - add it at the end of section
NewsContents = NewsContents & KeyName & "=" & value
Else
'remove last vbCrLf - the vbCrLf is at PosEndSection
NewsContents = Left(NewsContents, Len(NewsContents) - 2)
End If
 
'Combine pre-section, new section And post-section data.
INIContents = Left(INIContents, PosSection-1) & _
NewsContents & Mid(INIContents, PosEndSection)
else'if PosSection>0 Then
'Section Not found. Add section data at the end of file contents.
If Right(INIContents, 2) <> vbCrLf And Len(INIContents)>0 Then 
INIContents = INIContents & vbCrLf 
End If
INIContents = INIContents & "[" & Section & "]" & vbCrLf & _
KeyName & "=" & value
end if'if PosSection>0 Then
WriteFile FileName, INIContents
End Sub
 
 Function GetINIString(Section, KeyName, Default, FileName)
Dim INIContents, PosSection, PosEndSection, sContents, value, Found
 
'Get contents of the INI file As a string
INIContents = GetFile(FileName)
 
'Find section
PosSection = InStr(1, INIContents, "[" & Section & "]", vbTextCompare)
If PosSection>0 Then
'Section exists. Find end of section
PosEndSection = InStr(PosSection, INIContents, vbCrLf & "[")
'?Is this last section?
If PosEndSection = 0 Then PosEndSection = Len(INIContents)+1
 
'Separate section contents
sContents = Mid(INIContents, PosSection, PosEndSection - PosSection)
 
If InStr(1, sContents, vbCrLf & KeyName & "=", vbTextCompare)>0 Then
Found = True
'Separate value of a key.
value = SeparateField(sContents, vbCrLf & KeyName & "=", vbCrLf)
End If
End If
If isempty(Found) Then value = Default
GetINIString = value
End Function
 
 ' Separates one field between sStart And sEnd
 Function SeparateField(ByVal sFrom, ByVal sStart, ByVal sEnd)
Dim PosB: PosB = InStr(1, sFrom, sStart, 1)
If PosB > 0 Then
PosB = PosB + Len(sStart)
Dim PosE: PosE = InStr(PosB, sFrom, sEnd, 1)
If PosE = 0 Then PosE = InStr(PosB, sFrom, vbCrLf, 1)
If PosE = 0 Then PosE = Len(sFrom) + 1
SeparateField = Mid(sFrom, PosB, PosE - PosB)
End If
End Function
 
 ' File functions
 Function GetFile(ByVal FileName)
Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")
'Go To windows folder If full path Not specified.
If InStr(FileName, ":") = 0 And Left (FileName,2)<>"/" Then 
FileName = FS.GetSpecialFolder(0) & "" & FileName
End If
On Error Resume Next
 
GetFile = FS.OpenTextFile(FileName).ReadAll
End Function
 
 Function WriteFile(ByVal FileName, ByVal Contents)
 
Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")
'On Error Resume Next
 
'Go To windows folder If full path Not specified.
If InStr(FileName, ":") = 0 And Left (FileName,2)<>"/" Then 
FileName = FS.GetSpecialFolder(0) & "" & FileName
End If
 
Dim OutStream: Set OutStream = FS.OpenTextFile(FileName, 2, True)
OutStream.Write Contents
End Function
'*************************************************ini 库结束*************************************************






