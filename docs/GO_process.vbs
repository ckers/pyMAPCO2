Option Explicit

Sub Standards_and_fco2()

ActiveSheet.Name = "Data"

Const MaxStdSetInterval = 4# / 24#  '   Max time between standard sets

Dim dsh As Worksheet
Dim dr As Long, thisStdSet As Long, nextStdSet As Long
Dim co2Col As Integer, typeCol As Integer
Dim stdCO2Col As Integer, stdFlags(0 To 3) As Integer
Dim i1 As Long, i2 As Long, i3 As Long, ct As Long, r As Long, i4 As Long, i5 As Long, rAve As Long
Dim m As Double, b As Double, stdConcs(0 To 3) As Double, preStds(0 To 3) As Double, postStds(0 To 3) As Double
Dim currStds(0 To 3) As Double, currCO2 As Double
Dim moreRows As Boolean, stillLooking As Boolean, thisSetGood As Boolean, nextSetGood As Boolean, LookingForStandards As Boolean
Dim s1 As String, exStd As String
Dim xco2swCol As Integer, xco2airCol As Integer, stdCol As Integer

Dim eqtCol As Integer, sstCol As Integer, sssCol As Integer, eqpressCol As Integer, atmpressCol As Integer, cellpressCol As Integer, druckpressCol As Integer
Dim fco2airCol As Integer, fco2swCol As Integer, xco2warmCol As Integer, pco2swCol As Integer, pco2airCol As Integer, commentsCol As Integer

Dim ph2oair As Double, ph2osw As Double, b11air As Double, b11sw As Double
Dim d12air As Double, d12sw As Double
Dim fco2wet As Double, pco2wet As Double
Dim xco2swVal As Double

Dim startDate As Date, endDate As Date
    
Dim dateCol As Integer, timeCol As Integer, ydCol As Integer, flagCol As Integer
Dim newdateCol As Integer
Dim dataRow As Integer, monthLength As Integer
Dim dayValue As Integer, monValue As String
Dim sstVal As Double, sssVal As Double, sstOffset As Double
Dim sstFlag As Integer, sssFlag As Integer, qcFlag As Integer, licorFlag As Integer
Dim sstPrompt As String, sssPrompt As String, sDisplay As String, flagPrompt1 As String, fDisplay As String, flagPrompt2 As String, druckPrompt As String, licorPrompt As String
Dim std1Conc As Double, std2Conc As Double, std3Conc As Double, std4Conc As Double, t1 As Double, t2 As Double, T As Double
Dim eqpressAve As Double, eqpressVal As Double, atmpressAve As Double

Sheets("Data").Select


Set dsh = ActiveWorkbook.Worksheets("Data")
       
    Set dsh = Worksheets("Data"): dr = 2
    co2Col = -1: typeCol = -1: stdCO2Col = -1: stdCol = -1
    dateCol = -1: timeCol = -1
    eqtCol = -1: sstCol = -1: sssCol = -1:  eqpressCol = -1: atmpressCol = -1: cellpressCol = -1: flagCol = -1: druckpressCol = -1

    '   Find columns
    ct = 1

    While ct <= dsh.UsedRange.Columns.Count
    Select Case Trim(UCase(Cells(1, ct).Value))
        Case Is = "TYPE"
            typeCol = ct
        Case Is = "CO2 UM/M", "LICOR CO2"
            co2Col = ct
        Case Is = "STD", "STD VAL"
            stdCol = ct
        Case Is = "EQU TEMP"
            eqtCol = ct
        Case Is = "SST", "T IN"
            sstCol = ct
        Case Is = "SALINITY", "SBE SALINITY"
            sssCol = ct
        Case Is = "EQU PRESS"
            eqpressCol = ct
        Case Is = "ATM PRESS"
            atmpressCol = ct
        Case Is = "CELL PRESS", "LICOR PRESS"
            cellpressCol = ct
        Case Is = "DRY DRUCK"
            druckpressCol = ct
        Case Is = "DATE", "PC DATE"
            dateCol = ct
        Case Is = "TIME", "PC TIME"
            timeCol = ct
        Case Is = "FLAG"
            flagCol = ct
        End Select
        ct = ct + 1
    Wend
    
    '   If columns are not found, exit macro
    If typeCol < 0 Then
        MsgBox ("Type column not found - aborting macro.")
        Exit Sub
    End If
    If co2Col < 0 Then
        MsgBox ("CO2 um/m column not found - aborting macro.")
        Exit Sub
    End If
    If stdCol < 0 Then
        MsgBox ("STD column not found - aborting macro.")
        Exit Sub
    End If
    If eqtCol < 0 Then
        MsgBox ("EQ T column not found - aborting macro.")
        Exit Sub
    End If
    If eqpressCol < 0 Then
        MsgBox ("EQ Press column not found - aborting macro.")
        Exit Sub
    End If

    If cellpressCol < 0 Then
        MsgBox ("Cell Press column not found - aborting macro.")
        Exit Sub
    End If
    If dateCol < 0 Then
        MsgBox ("Date column not found - aborting macro.")
        Exit Sub
    End If
    If timeCol < 0 Then
        MsgBox ("Time column not found - aborting macro.")
        Exit Sub
    End If
    
' Check for SST, Salinity, and Atmospheric Pressure

    commentsCol = dsh.UsedRange.Columns.Count + 1
    Cells(1, commentsCol) = "User Input"
    Columns(commentsCol).Select
    Selection.ColumnWidth = 10
    
    licorPrompt = 0
    Do While licorPrompt = 0
    sDisplay = "Which Licor was used for data acquisition?" & Chr(13) _
        & "1 - Licor 7000 (GO System)" & Chr(13) _
        & "2 - Licor 6262 (Neill System - PMEL1 or PMEL2)" & Chr(13) _
        & "3 - Don't know - exit macro"
        licorPrompt = InputBox(sDisplay)
        Select Case licorPrompt
            Case Is = 1
                licorFlag = 1
            Case Is = 2
                licorFlag = 2
            Case Is = 3
                Exit Sub
            Case Else
                licorPrompt = 0
        End Select
    Loop
    
    If sstCol < 0 Then
        sDisplay = "SST not found, choose one of the following:" & Chr(13) _
        & "C - enter a constant for SST" & Chr(13) _
        & "O - enter an offset to be subtracted from eqT" & Chr(13) _
        & "S - stop and add SST column to file"
        sstPrompt = InputBox(sDisplay)
        Select Case sstPrompt
        Case Is = "C", "c"
            sstVal = Val(InputBox("Enter value for SST: "))
            Cells(2, commentsCol) = "SST:"
            Cells(3, commentsCol) = "Constant: " & sstVal
'            Cells(4, commentsCol) = sstVal
        Case Is = "O", "o"
            sstOffset = Val(InputBox("Enter offset for SST: "))
            Cells(2, commentsCol) = "SST:"
            Cells(3, commentsCol) = "Offset: " & sstOffset
 '           Cells(4, commentsCol) = sstOffset
        Case Else
            Exit Sub
        End Select
    Else
        sstFlag = 1
        Cells(2, commentsCol) = "SST:"
        Cells(3, commentsCol) = "Found"
    End If
    If sssCol < 0 Then
        sDisplay = "Salinity not found, choose one of the following:" & Chr(13) _
        & "C - enter a constant for Salinity" & Chr(13) _
        & "S - stop and add Salinty column to file"
        sssPrompt = InputBox(sDisplay)
        Select Case sssPrompt
        Case Is = "C", "c"
            sssVal = Val(InputBox("Enter value for Salinity: "))
            Cells(5, commentsCol) = "Salinity:"
            Cells(6, commentsCol) = "Constant: " & sssVal
'            Cells(7, commentsCol) = sssVal
        Case Else
            Exit Sub
        End Select
    Else
        sssFlag = 1
        Cells(5, commentsCol) = "Salinity:"
        Cells(6, commentsCol) = "Found"
    End If
        
    If druckpressCol > 0 Then
        If Not IsEmpty(Cells(2, druckpressCol)) Then
            druckPrompt = InputBox("Use Druck pressure instead of Licor pressure? (Y or N)")
                If druckPrompt = "Y" Or druckPrompt = "y" Then
                    cellpressCol = druckpressCol
                    Cells(8, commentsCol) = "Pressure:"
                    Cells(9, commentsCol) = "Druck"
                Else
                    Cells(8, commentsCol) = "Pressure:"
                    Cells(9, commentsCol) = "Licor"
                End If
        End If
    End If
    
            
    If atmpressCol < 0 Then
        MsgBox ("Atm pressure not found, using Cell pressure (or Druck if specified) to calculate fCO2a")
        atmpressCol = cellpressCol
    End If

' Add manual offset column and flag column
    If flagCol < 0 Then
        flagCol = dsh.UsedRange.Columns.Count + 1
        Cells(1, flagCol) = "Flag"
    End If
    
 ' add decimal date

    newdateCol = dsh.UsedRange.Columns.Count + 1
    Cells(1, newdateCol) = "New Date"
    ydCol = dsh.UsedRange.Columns.Count + 1
    Cells(1, ydCol).Value = "YD"
    
    dataRow = 2
    While dataRow <= dsh.UsedRange.Rows.Count
        If Left(Cells(dataRow, 1), 3) <> "EQU" And Left(Cells(dataRow, 1), 3) <> "ATM" And Left(Cells(dataRow, 1), 3) <> "STD" And Left(Cells(dataRow, 1), 3) <> "FIL" Then
            Columns(ydCol).Select
            Selection.Delete Shift:=xlToLeft
            Columns(newdateCol).Select
            Selection.Delete Shift:=xlToLeft
            Columns(flagCol).Select
            Selection.Delete Shift:=xlToLeft
            Columns(commentsCol).Select
            Selection.Delete Shift:=xlToLeft
            Cells(dataRow, 1).Select
            MsgBox ("Rows can only contain measurements for EQU,ATM,or Standards - Run macro again after fixing file")
            Exit Sub
        End If
    

        monthLength = (InStrRev(dsh.Cells(dataRow, dateCol), "/") - InStr(dsh.Cells(dataRow, dateCol), "/"))

        If monthLength < 3 Then
            monValue = "0" & Mid(dsh.Cells(dataRow, dateCol).Value, InStr(dsh.Cells(dataRow, dateCol).Value, "/") + 1, monthLength - 1)
        Else
            monValue = Mid(dsh.Cells(dataRow, dateCol).Value, InStr(dsh.Cells(dataRow, dateCol).Value, "/") + 1, monthLength - 1)
        End If
        If InStr(dsh.Cells(dataRow, dateCol), "/") < 3 Then
            dayValue = "0" & Left(dsh.Cells(dataRow, dateCol), InStr(dsh.Cells(dataRow, dateCol), "/") - 1)
        Else
            dayValue = Left(dsh.Cells(dataRow, dateCol), InStr(dsh.Cells(dataRow, dateCol), "/") - 1)
        End If
        dsh.Cells(dataRow, newdateCol) = monValue & "/" & dayValue & "/" & "12"
        startDate = "12/31/" & Year(dsh.Cells(dataRow, newdateCol)) - 1
        endDate = monValue & "/" & dayValue & "/" & Year(dsh.Cells(dataRow, newdateCol))
        dsh.Cells(dataRow, ydCol) = DateDiff("y", startDate, endDate) + ((Hour(dsh.Cells(dataRow, timeCol)) / 24) + (Minute(dsh.Cells(dataRow, timeCol)) / 1440) + (Second(dsh.Cells(dataRow, timeCol)) / 86400))
        dataRow = dataRow + 1
    Wend
    dsh.Cells(1, newdateCol) = "Date_mm/dd/yyyy"


' calculate standards

i4 = 2
LookingForStandards = True
While LookingForStandards
    If Left(dsh.Cells(i4, typeCol).Value, 4) = "STD1" Then
        If Left(dsh.Cells(i4 + 1, typeCol).Value, 4) = "STD2" And Left(dsh.Cells(i4 + 2, typeCol).Value, 4) = "STD3" And _
                    Left(dsh.Cells(i4 + 3, typeCol).Value, 4) = "STD4" Then

            std1Conc = dsh.Cells(i4, stdCol)
            std2Conc = dsh.Cells(i4 + 1, stdCol)
            std3Conc = dsh.Cells(i4 + 2, stdCol)
            std4Conc = dsh.Cells(i4 + 3, stdCol)
            dr = i4: r = i4
            LookingForStandards = False
        End If
     End If
    i4 = i4 + 1
Wend

 
    flagPrompt1 = UCase(InputBox("Do you want to exclude a standard? (Y or N)"))
    If flagPrompt1 <> "Y" And flagPrompt1 <> "N" Then
        flagPrompt1 = InputBox("Do you want to exclude a standard? (Y or N) - any other key assumes NO")
    End If
    If flagPrompt1 = "Y" Or flagPrompt1 = "y" Then
        fDisplay = "Which Standard do you want to exclude (1,2,3 or 4)" & Chr(13) _
        & "1 - " & std1Conc & Chr(13) _
        & "2 - " & std2Conc & Chr(13) _
        & "3 - " & std3Conc & Chr(13) _
        & "4 - " & std4Conc & Chr(13) _
        & "any other value assumes all Standards should be used"
        flagPrompt2 = InputBox(fDisplay)
        Select Case flagPrompt2
        Case Is = "1"
            exStd = "STD1"
        Case Is = "2"
            exStd = "STD2"
        Case Is = "3"
            exStd = "STD3"
        Case Is = "4"
            exStd = "STD4"
        End Select
        
        i5 = 2
        While i5 <= dsh.UsedRange.Rows.Count
            If Left(Cells(i5, typeCol), 4) = exStd Then
                Cells(i5, flagCol) = "Excluded"
            End If
            i5 = i5 + 1
        Wend
    End If
    

    

    stdCO2Col = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, stdCO2Col).WrapText = True
    dsh.Cells(1, stdCO2Col).Value = "Std CO2 - dry"
    
    xco2swCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, xco2swCol).WrapText = True
    dsh.Cells(1, xco2swCol).Value = "XCO2sw - dry@eqT"
    
'    xco2swdilCol = dsh.UsedRange.Columns.Count + 1
'    dsh.Cells(1, xco2swdilCol).WrapText = True
'    dsh.Cells(1, xco2swdilCol).Value = "XCO2sw - dry@eqT - corrected for dilution"
        
    xco2warmCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, xco2warmCol).WrapText = True
    dsh.Cells(1, xco2warmCol).Value = "xCO2sw - dry@SST"
    
    xco2airCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, xco2airCol).WrapText = True
    dsh.Cells(1, xco2airCol).Value = "XCO2air - dry"
    

    moreRows = True
    While moreRows
        thisSetGood = False: nextSetGood = False
        If Left(dsh.Cells(dr, typeCol).Value, 4) = "STD1" Then
            If Left(dsh.Cells(dr + 1, typeCol).Value, 4) = "STD2" And Left(dsh.Cells(dr + 2, typeCol).Value, 4) = "STD3" And _
                        Left(dsh.Cells(dr + 3, typeCol).Value, 4) = "STD4" Then
                ct = 0
                For i1 = 0 To 3
                    If IsEmpty(dsh.Cells(dr + i1, flagCol).Value) Then
                        preStds(i1) = dsh.Cells(dr + i1, co2Col).Value
                        ct = ct + 1
                    Else
                        preStds(i1) = -999#
                    End If
                Next
                '   make sure that there at least 2 good standard values
                If ct > 1 Then
                    thisStdSet = dr: thisSetGood = True
                    '   look for next set of stds
                    stillLooking = True: i2 = 4
                    While stillLooking
                        If Left(dsh.Cells(dr + i2, typeCol).Value, 4) = "STD1" Then
                            If dsh.Cells(dr + i2 + 1, typeCol).Value = "STD2" And _
                                    Left(dsh.Cells(dr + i2 + 2, typeCol).Value, 4) = "STD3" And _
                                    Left(dsh.Cells(dr + i2 + 3, typeCol).Value, 4) = "STD4" Then
                                '   Found second set - check for good stds
                                ct = 0
                                For i1 = 0 To 3
                                    If IsEmpty(dsh.Cells(dr + i2 + i1, flagCol).Value) Then
                                        postStds(i1) = dsh.Cells(dr + i2 + i1, co2Col).Value
                                        ct = ct + 1
                                    Else
                                        postStds(i1) = -999#
                                    End If
                                Next
                                If ct > 1 Then  '   2 good sets of stds exist
                                    nextStdSet = dr + i2: nextSetGood = True
                                    stillLooking = False
                                    t1 = dsh.Cells(dr + i2, ydCol).Value - dsh.Cells(dr, ydCol).Value
                                    t2 = dsh.Cells(dr + i2 + 3, ydCol).Value - dsh.Cells(dr + 3, ydCol).Value
                                    '   check if 2 stds are good in each set for interpolation
                                    ct = 0
                                    For i1 = 0 To 3
                                        If preStds(i1) > 0 And postStds(i1) > 0 Then
                                            stdFlags(i1) = 1
                                            ct = ct + 1
                                        Else
                                            stdFlags(i1) = 0
                                        End If
                                    Next
                                    If t1 < MaxStdSetInterval And t2 < MaxStdSetInterval And ct > 1 Then
                                        '   Store good standards in array of concentrations
                                        i3 = 0
                                        For i1 = 0 To 3
                                            If stdFlags(i1) > 0 Then
                                                If i1 = 0 Then
                                                    stdConcs(i3) = std1Conc: i3 = i3 + 1
                                                ElseIf i1 = 1 Then
                                                    stdConcs(i3) = std2Conc: i3 = i3 + 1
                                                ElseIf i1 = 2 Then
                                                    stdConcs(i3) = std3Conc: i3 = i3 + 1
                                                Else
                                                    stdConcs(i3) = std4Conc: i3 = i3 + 1
                                                End If
                                            End If
                                        Next
                                        i2 = 0: ct = 0
                                        While thisStdSet + ct < nextStdSet  '   recompute each sample
                                            If (Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "EQU" Or _
                                            Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "ATM" Or _
                                            Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "STD") And _
                                            IsEmpty(dsh.Cells(thisStdSet + ct, flagCol).Value) Then
                                                T = dsh.Cells(thisStdSet + ct, ydCol).Value
                                                currCO2 = dsh.Cells(thisStdSet + ct, co2Col).Value
                                                i3 = 0
                                                For i1 = 0 To 3
                                                    t1 = dsh.Cells(thisStdSet + i1, ydCol).Value
                                                    t2 = dsh.Cells(nextStdSet + i1, ydCol).Value
                                                    If stdFlags(i1) > 0 Then
                                                        currStds(i3) = preStds(i1) + ((postStds(i1) - preStds(i1)) _
                                                                    * (T - t1)) / (t2 - t1)
                                                        i3 = i3 + 1
                                                    End If
                                                Next
                                                '   compute slope & intercept of best fit line
                                                Call LeastSquaresLine(currStds(), stdConcs(), i3, m, b)
                                                Select Case Left(dsh.Cells(thisStdSet + ct, typeCol), 3)
                                                Case Is = "ATM"
                                                dsh.Cells(thisStdSet + ct, xco2airCol).Value = m * currCO2 + b
                                                Case Is = "EQU"
                                                dsh.Cells(thisStdSet + ct, xco2swCol).Value = m * currCO2 + b
                                                Case Else
                                                dsh.Cells(thisStdSet + ct, stdCO2Col).Value = m * currCO2 + b
                                                End Select
   
                                            End If
                                            ct = ct + 1
                                        Wend    '   while thisstdset + ct < nextstdset
                                    Else    '   time interval between stds is too long
                                        '   recompute xco2 with preceding set of standards
                                        i2 = 0: ct = 0
                                        While thisStdSet + ct < nextStdSet  '   recompute each sample
                                            If (Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "EQU" Or _
                                            Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "ATM" Or _
                                            Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "STD") And _
                                            IsEmpty(dsh.Cells(thisStdSet + ct, flagCol).Value) Then
                                                currCO2 = dsh.Cells(thisStdSet + ct, co2Col).Value
                                                i3 = 0
                                                For i1 = 0 To 3
                                                    If preStds(i1) > 0 Then
                                                        If i1 = 0 Then
                                                            currStds(i3) = preStds(i1)
                                                            stdConcs(i3) = std1Conc
                                                            i3 = i3 + 1
                                                        ElseIf i1 = 1 Then
                                                            currStds(i3) = preStds(i1)
                                                            stdConcs(i3) = std2Conc
                                                            i3 = i3 + 1
                                                        ElseIf i1 = 2 Then
                                                            currStds(i3) = preStds(i1)
                                                            stdConcs(i3) = std3Conc
                                                            i3 = i3 + 1
                                                        Else
                                                            currStds(i3) = preStds(i1)
                                                            stdConcs(i3) = std4Conc
                                                            i3 = i3 + 1
                                                        End If
                                                    End If
                                                Next
                                                '   compute slope & intercept of best fit line
                                                Call LeastSquaresLine(currStds(), stdConcs(), i3, m, b)
                                                Select Case Left(dsh.Cells(thisStdSet + ct, typeCol), 3)
                                                Case Is = "ATM"
                                                dsh.Cells(thisStdSet + ct, xco2airCol).Value = m * currCO2 + b
                                                Case Is = "EQU"
                                                dsh.Cells(thisStdSet + ct, xco2swCol).Value = m * currCO2 + b
                                                Case Else
                                                dsh.Cells(thisStdSet + ct, stdCO2Col).Value = m * currCO2 + b
                                                End Select
                                                ' dsh.Cells(thisStdSet + ct, stdCO2Col).Value = m * currCO2 + b
                                            End If
                                            ct = ct + 1
                                        Wend    '   while thisstdset + ct < nextstdset
                                    End If  '   t1 < maxInterval and t2 < maxInterval
                                    dr = nextStdSet
                                Else    '   keep looking for next good std set
                                    i2 = i2 + 1
                                End If  '   ct > 1
                            Else    '   No Std2, 3, & 4
                                i2 = i2 + 1
                            End If  '   Std set is complete
                        Else    '   Second std1 not found, keep looking
                            i2 = i2 + 1
                        End If  '   type = Std1
                        '   Check for end of data
                        If TypeName(dsh.Cells(dr + i2, ydCol).Value) = "Empty" Then
                            '   recompute xco2 with one set of standards
                            stillLooking = False
                            moreRows = False
                        End If
                    Wend    '   while stilllooking
                    If thisSetGood And Not nextSetGood Then
                        ct = 0: i3 = 0
                        '   Store good standards in conc array
                        For i1 = 0 To 3
                            If preStds(i1) > 0 Then
                                If i1 = 0 Then
                                    stdConcs(i3) = std1Conc
                                    currStds(i3) = preStds(i1)
                                ElseIf i1 = 1 Then
                                    stdConcs(i3) = std2Conc
                                    currStds(i3) = preStds(i1)
                                ElseIf i1 = 2 Then
                                    stdConcs(i3) = std3Conc
                                    currStds(i3) = preStds(i1)
                                Else
                                    stdConcs(i3) = std4Conc
                                    currStds(i3) = preStds(i1)
                                End If
                                stdFlags(i1) = 1
                                i3 = i3 + 1
                            Else
                                stdFlags(i1) = 0
                            End If
                        Next
                        While ct < i2
                            If (Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "EQU" Or _
                                            Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "ATM" Or _
                                            Left(dsh.Cells(thisStdSet + ct, typeCol), 3) = "STD") And _
                                            IsEmpty(dsh.Cells(thisStdSet + ct, flagCol).Value) Then
                                currCO2 = dsh.Cells(thisStdSet + ct, co2Col).Value
                                Call LeastSquaresLine(currStds(), stdConcs(), i3, m, b)
                                Select Case Left(dsh.Cells(thisStdSet + ct, typeCol), 3)
                                Case Is = "ATM"
                                dsh.Cells(thisStdSet + ct, xco2airCol).Value = m * currCO2 + b
                                Case Is = "EQU"
                                dsh.Cells(thisStdSet + ct, xco2swCol).Value = m * currCO2 + b
                                Case Else
                                dsh.Cells(thisStdSet + ct, stdCO2Col).Value = m * currCO2 + b
                                End Select
                                'dsh.Cells(thisStdSet + ct, stdCO2Col).Value = m * currCO2 + b
                            End If
                            ct = ct + 1
                        Wend
                        dr = thisStdSet + i2
                    End If
                Else    '   one or fewer good standards
                    dr = dr + 1
                End If  '   ct > 1
            Else    '   not a complete set of standards - keep looking
                dr = dr + 1
            End If  '   Complete set of standards found
        Else    '   Std 1 not found - keep looking
            dr = dr + 1
        End If  '   typecol = STD1
        '   Check for end of data
        If TypeName(dsh.Cells(dr, ydCol).Value) = "Empty" Then
            moreRows = False
        End If
    Wend    '   while moreRows
    

    
    
' Calculate fCO2

'   Find unused columns and use them for storing new values.

    fco2swCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, fco2swCol).WrapText = True
    dsh.Cells(1, fco2swCol).Value = "fCO2sw @SST"
    
    fco2airCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, fco2airCol).WrapText = True
    dsh.Cells(1, fco2airCol).Value = "fCO2air"
 
    pco2swCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, pco2swCol).WrapText = True
    dsh.Cells(1, pco2swCol).Value = "pCO2sw @SST"
    
    pco2airCol = dsh.UsedRange.Columns.Count + 1
    dsh.Cells(1, pco2airCol).WrapText = True
    dsh.Cells(1, pco2airCol).Value = "pCO2air"
    
    eqpressAve = 0
    atmpressAve = 0
    
    rAve = 2
    While rAve <= dsh.UsedRange.Rows.Count
        eqpressAve = eqpressAve + Cells(rAve, eqpressCol)
        atmpressAve = atmpressAve + Cells(rAve, atmpressCol)
        rAve = rAve + 1
    Wend
    eqpressAve = eqpressAve / (rAve - 2)
    atmpressAve = atmpressAve / (rAve - 2)

    
    If atmpressAve < 100 Then
        MsgBox ("Atm pressure not found, using Cell pressure")
        atmpressCol = cellpressCol
    End If
        
'    r = 2
 
    While r <= dsh.UsedRange.Rows.Count

        If sssFlag Then sssVal = Cells(r, sssCol).Value
        If sstFlag Then sstVal = Cells(r, sstCol).Value
        
        If sstPrompt = "O" Or sstPrompt = "o" Then
            sstVal = Cells(r, eqtCol).Value - sstOffset
        End If
        
        If eqpressAve < 100 Then
            eqpressVal = Cells(r, eqpressCol) + Cells(r, cellpressCol)
        Else
            eqpressVal = Cells(r, eqpressCol)
        End If

        If Left(Cells(r, typeCol), 3) = "EQU" Then
            ' calculate fco2 sw and delta fco2
         
            '   P(H2O) atm Teq (correction for vapor pressure in Sea Water)
            ph2osw = Exp(24.4543 - (67.4509 * (100 / (Cells(r, eqtCol) + 273.15))) - (4.8489 * Log((Cells(r, eqtCol) + 273.15) / 100)) - (0.000544 * sssVal))

            '   B11 cm3/mol Teq (1st correction for non-ideality of gas - SW)
            b11sw = -1636.75 + (12.0408 * (Cells(r, eqtCol) + 273.15)) - (0.0327957 * (Cells(r, eqtCol) + 273.15) ^ 2) + (0.0000316528 * (Cells(r, eqtCol) + 273.15) ^ 3)
            
            '   d12 cm3/mol Teq (2nd correction for non-ideality of gas - SW)
            
            d12sw = 57.7 - (0.118 * (Cells(r, eqtCol) + 273.15))
            
            ' xCO2 with dilution correction for Licor 7000, if needed
            
            If licorFlag = 1 Then
                xco2swVal = Cells(r, xco2swCol) / (1 - ph2osw / 1000)
            Else
                xco2swVal = Cells(r, xco2swCol)
            End If

            ' pCO2 wet @ eqt
            
            pco2wet = xco2swVal * ((eqpressVal * 0.000986923) - ph2osw)
            
            ' fCO2 wet @ eqt
            
            fco2wet = pco2wet * Exp((eqpressVal * 0.000986923) * (b11sw + (2 * d12sw)) / (82.057 * (Cells(r, eqtCol) + 273.15)))
            
            If Cells(r, eqtCol) > 10 And Cells(r, cellpressCol) > 900 Then
                
            '   f(CO2) sw (with warming correction) (fco2 wet @ sst)
            
            Cells(r, fco2swCol) = fco2wet * Exp(0.0423 * (sstVal - Cells(r, eqtCol)))
            
            ' xco2 dry, corrected for warming - for comparison to buoy CO2 (xco2 dry @ sst)
            
            Cells(r, xco2warmCol) = xco2swVal * Exp(0.0423 * (sstVal - Cells(r, eqtCol)))
        
             ' pco2 wet @sst
             
             Cells(r, pco2swCol) = xco2swVal * ((eqpressVal * 0.000986923) - ph2osw) * Exp(0.0423 * (sstVal - Cells(r, eqtCol)))
            Else
                If Cells(r, eqtCol) <= 10 Then
                    If Cells(r, cellpressCol) < 900 Then
                        Cells(r, flagCol) = "EqT, pressure"
                    Else
                        Cells(r, flagCol) = "EqT"
                    End If
                Else
                Cells(r, flagCol) = "Pressure"
                End If
            
  '              Cells(r, flagCol) = "EqT"
            End If
            
        End If
        
        If Left(Cells(r, typeCol), 3) = "ATM" Then
            'calculate fCO2 air

            '   P(H2O) atm Tss (correction for vapor pressure in Air)
            ph2oair = Exp(24.4543 - (67.4509 * (100 / (sstVal + 273.15))) - (4.8489 * Log((sstVal + 273.15) / 100)) - (0.000544 * sssVal))

            '   B11 cm3/mol Tss (1st correction for non-ideality of gas - Air)
            b11air = -1636.75 + (12.0408 * (sstVal + 273.15)) - (0.0327957 * (sstVal + 273.15) ^ 2) + (0.0000316528 * (sstVal + 273.15) ^ 3)
            
            
            '   d12 cm3/mol Tss (2nd correction for non-ideality of gas - Air)
            d12air = 57.7 - (0.118 * (sstVal + 273.15))

            If Cells(r, atmpressCol) > 900 Then
            '   f(CO2) air
            Cells(r, fco2airCol) = Cells(r, xco2airCol) * ((Cells(r, atmpressCol) * 0.000986923) - ph2oair) * Exp((Cells(r, atmpressCol) * 0.000986923) * (b11air + (2 * d12air)) / (82.057 * (sstVal + 273.15)))
        
            ' pCO2 air
            
            Cells(r, pco2airCol) = Cells(r, xco2airCol) * ((Cells(r, atmpressCol) * 0.000986923) - ph2oair)
            Else
                Cells(r, flagCol) = "Pressure"
            End If
        End If
        
        r = r + 1
    Wend

End Sub '
Sub LeastSquaresLine(xVals() As Double, yVals() As Double, numPts As Long, slope As Double, yInt As Double)
'
'   Determines the slope and y intercept of the best fit line for the data contained in the
'   arrays xVals and yVals.  Works with any number of points but the number of points must
'   be input to the procedure.
'

Dim sumX As Double, sumY As Double, sumXY As Double, sumXSq As Double
Dim numerator As Double, divisor As Double
Dim i1 As Long, botLim As Long, topLim As Long
    '
    If LBound(xVals) = 0 Then
        botLim = 0
        topLim = numPts - 1
    Else
        botLim = 1
        topLim = numPts
    End If
    sumX = 0#: sumY = 0#: sumXY = 0#: sumXSq = 0#
    For i1 = botLim To topLim
        sumX = sumX + xVals(i1)
        sumY = sumY + yVals(i1)
        sumXY = sumXY + (xVals(i1) * yVals(i1))
        sumXSq = sumXSq + xVals(i1) ^ 2
    Next
    numerator = (numPts * sumXY) - (sumX * sumY)
    divisor = (numPts * sumXSq) - sumX ^ 2
    slope = numerator / divisor
    numerator = (sumXSq * sumY) - (sumXY * sumX)
    yInt = numerator / divisor
End Sub '   LeastSquaresLine


