import re


company= re.compile(r'.*?column-1">(.*)')
website = re.compile(r'.*">(.*)</a>')
with open("rows.txt") as f:
    data = f.readlines()
    
for line in data:
    bits = line.split("</td>")
    try:
        print company.findall(bits[0])[0], "\t",  website.findall(bits[2])[0]
    except:
        pass

