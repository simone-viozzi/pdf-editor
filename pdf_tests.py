

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
        a = str(pdf_obj[k]).replace("'", '"')
        a = re.sub(r'\{\.\.\.\}', r'"\g<0>"', re.sub(r'\(\d+,\s?\d+\)', r'"\g<0>"', a))
        
        

        json_object = json.loads(a)
        a = json.dumps(json_object, indent=2)

        reg1 = re.compile(r'([^\"])(\[[^\[\]]*\])([^\"])')
        a = reg1.sub(replif1, a)
        
        reg2 = re.compile(r'([^\"])(\{[^\{\}]*\})([^\"])')
        a = reg1.sub(replif2, a)
        
        #print("*"*20)
        if len(a) > 5000:
            print(a)
        #print("*" * 20)
        
        a = re.sub(r"\"\/Kids\":\s?(\[(?>([^\[\]])+|\[([^\[\]])+\])*\])", '"/Kids": "{...}"', a)
        json_object = json.loads(a)
        json_formatted_str = json.dumps(json_object, indent=2)
        s += ". " * 5 + "\n" + str(k) + ': ' + "\n" + str(json_formatted_str) + "\n"
    