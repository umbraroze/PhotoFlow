;;; ==================================================================
;;; AutoHotkey script for backing up photos from a memory card.
;;; Load it up and hit Ctrl+Shift+P.
;;; ==================================================================

;; I still need to wrap my brain around how to create GUIs, so this
;; will be done later.
;^!+p::
;{
;	Gui,New,,"Choose the camera"
;	Gui,Add,DropDownList,gCamera,Other|Nikon_D3200|Galaxy_Trend
;	Gui,Show
;	GuiControlGet,Camera,,gCamera
;	MsgBox, Camera: %Camera%
;	Return
;}

^+p::
{
	;; Figure out what we need back up and to where.
	SourceCard:="D:\CameraImportTest"
	;Camera:="Nikon_D3200"
	Camera:="Test_Camera"
	FormatTime,OutputTimeStamp,,yyyyMMdd
	OutputFile:=% "D:\" . Camera . "_" . OutputTimeStamp . ".7z"
	MsgBox, Photos will be backed up to %OutputFile%

	;; Go to 7-Zip and navigate to the source folder
	WinActivate, 7-Zip
	Click,46,115
	Send,%SourceCard%{Enter}
	;; And all we now need to do is to add this shit to the
	;; bloody package. THIS IS YET TO BE DONE.

	;; We're done.
	Return
}