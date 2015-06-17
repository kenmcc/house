import urllib2
import urllib
from cookielib import CookieJar
import re
import ConfigParser
import smtplib
from email.mime.text import MIMEText
import logging
import datetime
import sys
import subprocess as ps
logging.basicConfig(level=logging.DEBUG)

def getNumFiles(url1, url2):
    logging.debug("Getting Number and Info on Files from " + url1  + "\n" + url2)
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    response = opener.open(url1)
    content = response.read()
    logging.debug("Back from open with {0} bytes".format(len(content)))
    
    content = content.replace("&amp;", "&").replace("\r", "").replace("\t","").replace("\n","").replace("&nbsp;", "")
    #print content
    doctab = re.compile(r'\"/(Exe.*)\" sc')
    #print "FOUND", doctab.search(content).groups()[0].split(" ")[0]
    url2 = "http://dms.dlrcoco.ie/"+doctab.search(content).groups()[0].split(" ")[0]
    response = opener.open(url2)
    content = response.read()
    logging.debug("Back from open with {0} bytes".format(len(content)))

    content = content.replace("&amp;", "&").replace("\r", "").replace("\t","").replace("\n","").replace("&nbsp;", "")
    #print content
    
    
    #print content
    numFiles = re.compile(r"var NrOfFiles = (?P<files>[0-9]*);")
    tableRow = re.compile(r"\<tr id.*?/tr\>", re.MULTILINE|re.DOTALL)
    files = None
    docs = []
    s = numFiles.search(content) 
    if s:
        files =  s.groups()[0]
        #print files
        
    ind = tableRow.findall(content)
    if ind:
        tableCol = re.compile(r"\<td(.*?)/td\>",re.MULTILINE|re.DOTALL)
        for i in ind:
            cols = tableCol.findall(i)
            if len(cols) > 9:
                pdf = cols[1]
                hrefFinder = re.compile(r'href="(.*?)"')
                try:
                    link = "http://dms.dlrcoco.ie"+hrefFinder.findall(pdf)[2]
                except:
                    link = "Can't obtain"
                #print pdf.find(r'href=".*"')
                anchorFinder = re.compile(r'\<a\>(.*?)\</a\>')
                typer = anchorFinder.findall(cols[8])[0]
                docs.append((typer, link))
                
    logging.debug("Return Files {0} and changed docs {1}".format(files, docs))
    return files, docs
    
def getStatus(url):
    logging.debug("Getting Status of application")
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    logging.debug("Opening url :" + url)
    response = opener.open(url)
    data = response.read()
    
    logging.debug("Back from open with {0} bytes".format(len(data)))

    info=[]
    data = data.replace("\r", "").replace("\t","").replace("\n","").replace("&nbsp;", "")
    finder = re.compile(r'\<div id="fieldset_data"\>.*?\</div\>', re.MULTILINE|re.DOTALL)
    found =  finder.findall(data)
    for d in found:
        labelfind = re.compile(r'\<label class=".*" for=".*">(.*):\</label\>\<p.*\>(.*)\</p\>')
        items = labelfind.findall(d)
        if len(items):
            #print items[0][0], items[0][1]
            info.append((str(items[0][0]).strip(), str(items[0][1]).strip()))
    logging.debug("Returning {0}".format(info))        
    return info
    

def compareWithExistingData(itemsToCheck, files, docs):
    changes = False
    fileChanges = False
    changedFields = {}
    changedDocs = []
    config = ConfigParser.SafeConfigParser()
    config.read('planningstatus.txt')
    
    if "Updated" not in config.sections():
        config.add_section("Updated")
    config.set("Updated", "Last Updated", datetime.datetime.now().replace(microsecond=0).isoformat())

    
    for section in ["APP DETAILS", "NUM FILES", "DOCS"]:
        if section not in config.sections():
            config.add_section(section)
    
    ######### APP DETAILS ##############
    for i in itemsToCheck:
        try:
            oldVal = config.get('APP DETAILS', i[0])
            if oldVal != i[1]:
                logging.debug("Found different value for {0}".format(i[0]))
                changes = True
                changedFields[i[0]] = "[{0}] => [{1}]".format(oldVal, i[1].strip())
                config.set("APP DETAILS", i[0], i[1].strip())
        except:
            logging.debug("New value for {0}".format(i[0]))
            config.set("APP DETAILS", i[0], i[1].strip())
            changes = True
            changedFields[i[0]] = "[{0}] => [{1}]".format(("unset"), i[1])
            
    ########## NUM FILES ##############
    try:
        oldFiles = config.get("NUM FILES", "FILES")
        if oldFiles != str(files):
            changes = True
            fileChanges = True
            logging.debug("Different number of files now")
            changeFields["Files"] = "[{0}] => [{1}]".format(oldFiles, files)
            config.set("NUM FILES", "FILES", str(files))
    except:
        config.set("NUM FILES", "FILES", str(files))
        changes = True
        fileChanges = True
        changedFields["Files"] = "[{0}] => [{1}]".format(("unset"), files)
        
    ########### the docs #############
    if fileChanges:
        indx = 0
        for i in docs:
            newVal=urllib.unquote(i[1].strip())
            changedDocs.append((i[0], i[1]))
            indx += 1
        '''
        try:
            oldVal = urllib.unquote(config.get('DOCS', i[0]))
            if oldVal != i[1]:
                logging.debug("Found different value for doc {0}".format(i[0]))
                changes = True
                changedDocs[i[0]] = "[{0}] => [{1}]".format(oldVal, i[1].strip())
                config.set("DOCS", i[0], '"'+newVal+'"')
        except:
            logging.debug("New value for doc {0}".format(i[0]))
            config.set("DOCS", i[0], '"'+newVal+'"')
            changes = True
            changedDocs[i[0]] = "[{0}] => [{1}]".format(("unset"), i[1].strip())
        '''
        
    with open('planningstatus.txt', 'w') as configfile:
        config.write(configfile)
    return changes, changedFields, changedDocs



def emailMe(fields, changedDocs, error = False, decision=None):
    if error:
        strToSend = "An error occurred in the processing\n\n"
        for f in fields:
            strToSend += "{0:>10s}:\n".format(f)
            data = fields[f]
            for d in data:
                strToSend += " "*12 + str(d) + "\n"
    else:
        strToSend = ""
        if decision is not None:
            strToSend = "*"*60+"\n*"+" "*58+"*\n*{0:^58s}*".format(decision)+"\n*"+" "*58+"*\n"+"*"*60 + "\n\n"
        strToSend += "The following fields have been changed\n"
        for f in fields:
            strToSend += "{0:>25s}".format(f)+":"+fields[f]+ "\n"
            
        if changedDocs != []:
            strToSend += "\nAnd the following docs have been changed"
            for f in changedDocs:
                strToSend += "\nDoctype:{0:>30s}\n".format(f[0])+f[1]+ "\n"
                
    strToSend += "\n=======================================================\n"
        
    strToSend += "\nAPPLICATION: " +AppUrl + "\nDOCUMENTS: "
    strToSend += docUrl1 + "\n\n"
    
    # Create a text/plain message
    msg = MIMEText(strToSend)
    
    me = "ken.mccullagh@atlas.dublin"
    you = "ken.mccullagh@s3group.com"
    msg['Subject'] = 'Update to planning application'
    msg['From'] = me 
    msg['To'] = you 
    
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()

    import subprocess as ps
    ps.call(["zenity", "--info", "--text", str(strToSend.replace("&","&amp;")), "--display=:0.0"])

if __name__=="__main__":
                 
    docUrl1 = "http://dms.dlrcoco.ie/Exe/ZyNET.exe?ZyAction=ZyActionS&User=ANONYMOUS&Password=anonymous&Client=planning&SearchBack=ZyActionL&SortMethod=h&SortMethod=-&MaximumDocuments=15&ImageQuality=r75g16%2Fr75g16%2Fx150y150g16%2Fi500&Display=hpfrw&DefSeekPage=f&Toc=&TocEntry=&TocRestrict=&QField=Ref_No%5E%22D15A/0254%22&UseQField=Ref_No&IntQFieldOp=1&ExtQFieldOp=1&SearchMethod=1&Time=&Index=Planning+Archive+1%7CPlanning+Archive+2%7CPlanning+Archive+3%7CPlanning+Ext%7CPlanning+Int%7CPlanning+External+B%7CPlanning+External+C%7CPlanning+External+D&FuzzyDegree=0&Query=&IntQFieldOp=1&ExtQFieldOp=1"
    docUrl2 = "http://dms.dlrcoco.ie//Exe/ZyNET.exe?ZyActionS|7=Search&Client=planning&Index=Planning%20Ext&Query=&ResultOffset=&Time=&EndTime=&SearchMethod=1&TocRestrict=&Toc=&TocEntry=&QField=Ref%5FNo%5E%22D15A%2F0254%22&QFieldYear=&QFieldMonth=&QFieldDay=&UseQField=Ref%5FNo&IntQFieldOp=1&ExtQFieldOp=1&XmlQuery=&User=ANONYMOUS&Password=anonymous&SortMethod=h%7C-&MaximumDocuments=15&FuzzyDegree=-1&ImageQuality=r75g16/r75g16/x150y150g16/i500&Display=hpfrw&DefSeekPage=f&MaximumPages=-1"
               

    AppUrl = "http://planning.dlrcoco.ie/swiftlg/apas/run/WPHAPPDETAIL.DisplayUrl?theApnID=D15A/0254&theTabNo=2"

    logging.debug("About to begin")
    info = getStatus(AppUrl)
    Files, docs = getNumFiles(docUrl1, docUrl2)
    
    if Files is None or len(info) == 0:
        emailMe({"FILES":Files if Files is not None else ["Not Found"], "INFO":info if len(info) > 0 else ["Not Found"]}, [], True)
    else:
        decision = None
        for i in info:
            if i[0] == "Decision":
                if len(i[1]) > 0:
                    print "have decision"
                    decision = i[1]
                break
                
                
        changes, fields, changedDocs = compareWithExistingData(info, Files, docs)
        if changes:# or decision:
            emailMe(fields, changedDocs, False, decision)

