@echo off

rem ����Ϊutf-8
::chcp 65001 

set workPath=%~dp0

cd %workPath%

set /p index=��������ʼ��ţ�
set infoFlag=0

:head
call "./subfun.vbs" 0 0 0
cls

echo ��ǰ���Ϊ��%index%
if %infoFlag% equ 0 ( echo info:CLOSE )else ( echo info:OPEN )
echo=
echo ������������
echo 1:�ռ���־
echo 2:�ض���־
echo 3:�л�info����
echo 4:�ռ�����¼info(��һ��)
echo 5:ɾ����ǰ��־
echo 6:������������־
echo 7:����־���·��
set /p key=�����룺

if %key% equ 1 ( goto ok ) ^
else if %key% equ 2 ( goto ok ) ^
else if %key% equ 3 ( goto info ) ^
else if %key% equ 4 ( goto ok ) ^
else if %key% equ 5 ( goto ok ) ^
else if %key% equ 6 ( goto ok ) ^
else if %key% equ 7 ( goto ok ) ^
else ( goto ng )

:ok
cls

call "./subfun.vbs" %key% %index% %infoFlag%
::timeout /T 1 /NOBREAK
::rd /s /q %dcPath%
::rd /s /q %ecPath%
::rd /s /q %scPath%
::rd /s /q %st103Path%

if %key% equ 1 ( set /a index=index+1 )  ^
else if %key% equ 4 ( set /a index=index+1 )
goto head


:info
cls
if %infoFlag% equ 0 ( set infoFlag=1 ) ^
else ( set infoFlag=0 )
goto head

:ng
cls
echo �����������������
goto head