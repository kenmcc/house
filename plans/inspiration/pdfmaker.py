from os.path import *
import sys
import os
import subprocess as ps

excluded=["attic"]

def dir_contents(path, filesOrFolders="Files"):
    contents = os.listdir(path)
    files,folders = [],[]
    for p in os.listdir(path):
        if p not in excluded:
            if isdir(p): folders.append(p)
            else: files.append(p)
    
    if filesOrFolders=="Files":
        return files
    elif filesOrFolders=="Folders":
        return sorted(folders, key=lambda s: s.lower())
    else:
        print "FILESORFOLDERS", filesOrFolders
        return []
    
header="""
\\documentclass[a4paper, titlepage, 12pt]{article}
\\usepackage{hyperref}
\\usepackage{xcolor}
\\hypersetup{
    colorlinks,
    linkcolor={red!50!black},
    citecolor={blue!50!black},
    urlcolor={blue!80!black}
}
\\usepackage{graphicx}
\\usepackage[a4paper, top=1cm, bottom=2cm, left=1cm, right=1cm]{geometry}
\\usepackage{pdfpages}
\\usepackage{xcolor,colortbl}
%%\\pdfimageresolution=72
\\begin{document}
~\\\\[5cm]
\\begin{center}
    \\textcolor{black}{
        \\bf{
            \\fontsize{5cm}{1cm}\\selectfont 
            INSPIRATIONS FOR BUILD \\\\
            }
    }
\end{center}
\\newpage
\\tableofcontents
"""

footer="""
\\end{document}
"""

def recurse(path, f, depth=0):        
    path = path.replace("./", "")
    #print "-------{0}---------------".format(path)
    files = []
    folders = []
    contents = os.listdir(path)
    for p in contents:
      if p.lower() not in excluded:
        if isdir(path+"/"+p):
            folders.append(path+"/"+p)
        else: 
            files.append(p)
            
    if "requirements.tex" in files:
         files.remove("requirements.tex")
    
    firstPrinted = False
    for fa in sorted(files):
        if path != ".":
            if not fa.endswith(".aux"):
                
                imgName = path+"/"+fa.replace("./","")
                caption = fa.replace("_", "\_")
                if len(caption) > 45:
                    begin = caption[:20]
                    end = caption[-23:]
                    caption=begin+".."+end
                    
                if not firstPrinted:
                    f.write("\\"+"sub"*(depth)+"section{Inspiration Images}")
                    firstPrinted = True
                f.write("\\begin{figure}[!h]\\centering\\includegraphics[width=0.8\\textwidth]{"+imgName+"}\\caption{"+caption+"}\\end{figure} \n")
    for fa in sorted(folders, key=lambda s: s.lower()):
        sections = fa.split("/")
        f.write("\\clearpage \n")
        f.write("\\"+"sub"*depth+"section{"+ sections[-1:][0].upper().replace("ZZZ","")+"}\n")
        f.write("\\InputIfFileExists{"+fa+"/requirements}{}{} \n")
        
        recurse(fa, f, depth + 1)
            
    return
            


with open("inspirations.tex", "w") as f:
    f.write(header)
    '''
    folders = dir_contents(".", "Folders")
    for fld in folders:
        f.write("\\section{"+fld.upper()+"} \n")
        files = dir_contents(fld, "Files")
        for fl in files:
            f.write("\\includegraphics[width=14cm]{"+fld+"/"+fl+"} \\\\")
    '''
    recurse(".", f)
    f.write(footer)
    
    
ps.check_call(["pdflatex", "inspirations.tex"])
ps.check_call(["pdflatex", "inspirations.tex"])
ps.check_call(["pdflatex", "inspirations.tex"])

