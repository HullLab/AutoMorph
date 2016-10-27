#!/usr/bin/python
"""
writeLatexFile.py
"""

def writeLatexFile(u3dFile,media9Path,outputFileNameBase,outputFilePath,focusedPath,sfPath,unit):
    """
    """
    import os
    import glob
    import string
    
    volFilePath = os.path.join(sfPath,outputFileNameBase,outputFileNameBase+'_volume_surface_area.csv')
    volFile = open(volFilePath,'r')
    volLines = volFile.readlines()[0].split('\r')
    values = volLines[1].split(',')
    width = values[-3]
    length = values[-2]
    gridSize = values[-5]
    # Build label image path
    labelPath = glob.glob(os.path.join(focusedPath,'final','stripped','labels',outputFileNameBase) + '*')[0]
        
    # Remove periods from image name if present
    if '.' in outputFileNameBase:
    	newFileNameBase = outputFileNameBase.replace('.','_')
    	rgbPathIn = os.path.join(sfPath,outputFileNameBase,outputFileNameBase + '_focused_rgb')
    	rgbPathOut = os.path.join(sfPath,outputFileNameBase,newFileNameBase + '_focused_rgb')
    	imRGBCommand = 'convert ' + rgbPathIn + '.tif ' + rgbPathOut + '.png'
    else:
        rgbPathOut = os.path.join(sfPath,outputFileNameBase,outputFileNameBase + '_focused_rgb')
        imRGBCommand = 'convert ' + rgbPathOut + '.tif ' + rgbPathOut + '.png'
    # Convert image types from .tif to '.png' using an external call to ImageMagick
    labelNoExtPath = os.path.splitext(labelPath)[0]
    pngPath = string.replace(labelNoExtPath,'.','_') + '.png'
    imLabelCommand = ' '.join(['convert', labelPath, pngPath])
    os.system(imLabelCommand)
    #imRGBCommand = 'convert ' + rgbPathIn + '.tif ' + rgbPathOut + '.png'
    os.system(imRGBCommand)
    
    latexFile = open(outputFilePath,'w')
    
    latexText1 = """\documentclass{article}
\usepackage{"""

    latexText2 = """}
\usepackage[colorlinks=true]{hyperref}
\usepackage{siunitx}

\setlength{\\voffset}{-0.75in}
\setlength{\headsep}{5pt}
\setlength{\intextsep}{5pt}
\setlength{\\textfloatsep}{-1pt}
\setlength{\\textheight}{650pt}

\\begin{document}
\pagestyle{empty}

\\begin{figure}[t]
	\centerline{\includegraphics[scale=0.5]{"""

    latexText3 = """}}
\end{figure}

\\begin{center}
	Length: \SI{""" 
	
    latexText4 = """} - Width: \SI{"""
    
    latexText5 = """} - Grid Size: \SI{"""

    latexText6 = """} - Unit: """

    latexText7 = """\end{center}

\centerline{\includemedia[
label="""

    latexText8 = """,
width=1\linewidth,height=1\linewidth,
playbutton=none,
activate=pageopen,
3Dlights=CAD,
3Daac=7,
3Droll=0,
3Dc2c=-4 -2 5,
3Droo=85,
3Dcoo=6 4 0
]{}{"""
    
    latexText9 = """}}

\\begin{figure}[b]
	\centerline{\includegraphics[scale=0.2]{"""
 
    latexText10 = """}}
\end{figure}

\end{document}"""

    latexTextFinal = ''.join([latexText1,os.path.join(media9Path,'media9'),latexText2,string.replace(labelNoExtPath,'.','_'),latexText3,length,latexText4,width,latexText5,gridSize,latexText6,unit,latexText7,u3dFile,latexText8,u3dFile,latexText9,rgbPathOut,latexText10])
    latexFile.write(latexTextFinal)
    latexFile.close()
