Option Explicit
Const ForReading = 1, ForWriting =2 , ForAppending = 8
Const TristateUseDefault = -2

Dim objFSO, objFile, txtFile, txtStreamText
Set objFSO = CreateObject("scripting.filesystemobject")

Dim strTxtFilePath


Function SetFlag(path, var)
	strTxtFilePath = path & "/config.txt"
	
	If (objFSO.FileExists(strTxtFilePath)) = 0 Then
		'Create the file if there is no the text file
		objFSO.CreateTextFile(strTxtFilePath)
		Set objFile = objFSO.GetFile(strTxtFilePath)
		'Open the txt file
		Set txtFile = objFile.OpenAsTextStream(ForWriting, TristateUseDefault)
		txtFile.Write var
		txtFile.Close
	Else 
		'open the text file directly if the file is existed
		Set txtFile = objFSO.OpenTextFile(strTxtFilePath, ForWriting, False)
		txtFile.Write var
		txtFile.Close
	End If 
End Function

Function GetFlag(path)
	strTxtFilePath = path & "/config.txt"
	
	Set objFile = objFSO.GetFile(strTxtFilePath)
	'Open the txt file
	Set txtFile = objFile.OpenAsTextStream(ForReading, TristateUseDefault)
	GetFlag = txtFile.Read(1)	
End Function

'Ëæ»úÊý
Function GetRandMath(m,n)
	Randomize
	GetRandMath = Int(((n-m+1) * Rnd) + m)
End Function


