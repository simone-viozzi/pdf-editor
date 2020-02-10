

import regex as re
import json
from pdfrw import *
import os


paths = ["pdfs/" + f for f in os.listdir("pdfs/") if os.path.isfile(os.path.join("pdfs/", f))]


def replif1(match):
    if len(re.findall(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', match.group(0))) > 5:
        return match.group(1) + "\"[...]\"" + match.group(3)
    else:
        return match.group(1) + match.group(2) + match.group(3)

def replif2(match):
    if len(re.findall(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', match.group(0))) > 5:
        return match.group(1) + "\"{...}\"" + match.group(3)
    else:
        return match.group(1) + match.group(2) + match.group(3)


for path in paths:
    if not path.endswith('.pdf'):
        path += ".pdf"
    pdf_obj = PdfReader(path)

    s = ""
    for k in pdf_obj.keys():
        print(path, k)
        
        a = str(pdf_obj[k]).replace("'", '"')
        a = re.sub(r'\{\.\.\.\}', r'"\g<0>"', re.sub(r'\(\d+,\s?\d+\)', r'"\g<0>"', a))

        reg1 = re.compile(r'([^\"])(\[[^\[\]]*\])([^\"])')
        a = reg1.sub(replif1, a)
        
        reg2 = re.compile(r'([^\"])(\{[^\{\}]*\})([^\"])')
        a = reg1.sub(replif2, a)
        
        reg3 = re.compile(r'\[[^\[\]\:\.]*\]')
        a = reg3.sub("\"[...]\"", a)

        reg4 = re.compile(r'\{[^\{\}\.]*\}')
        a = reg4.sub("\"{...}\"", a)

        reg5 = re.compile(r'\{[^\{\}\[\]]*\[[^\{\}]*\]\,[^\{\}]*\}(\,?)')
        a = reg5.sub(r'"{...}"\g<1>', a)
        
        print(a)
        print("\n")
        
        json_object = json.loads(a)
        a = json.dumps(json_object, indent=2)
        
        