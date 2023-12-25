@echo off

rem 设置为utf-8
::chcp 65001 

set workPath=%~dp0

cd %workPath%

set /p index=请输入起始序号：
set infoFlag=0

:head
call "./subfun.vbs" 0 0 0
cls

echo 当前序号为：%index%
if %infoFlag% equ 0 ( echo info:CLOSE )else ( echo info:OPEN )
echo=
echo 输入以下数字
echo 1:收集日志
echo 2:截断日志
echo 3:切换info开关
echo 4:收集并记录info(仅一次)
echo 5:删除当前日志
echo 6:按日期收纳日志
echo 7:打开日志存放路径
set /p key=请输入：

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
echo 输入错误，请重新输入
goto head