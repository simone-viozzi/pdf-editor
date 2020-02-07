
# install
# sudo -H pip3 install --upgrade pip
# sudo -H python3.6 -m pip install -U pymupdf



import os
from PyPDF2 import PdfFileWriter, PdfFileReader

from pdfrw import *

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from itertools import count, takewhile
import re

# https://pymupdf.readthedocs.io/en/latest/tutorial/#importing-the-bindings
class pdfReader:
    pdf_obj = None
    def __init__(self, path):
        if(not path.endswith('.pdf')):
            path += ".pdf"
        self.pdf_obj = fitz.open(path)
    
    def getPage(self, i):
        return self.pdf_obj[i]
    
    def getDocumentInfo(self):
        s = ""
        for k, v in self.pdf_obj.metadata.items():
            s += str(k) + '-->' + str(v) + "\n"
        return s
    
    def getNumPages(self):
        return self.pdf_obj.pageCount
    
    def getOutlines(self):
        return self.pdf_obj.getToC()


class pdfWriter:
    fh = None
    pdf_obj = None
    
    def __init__(self, path):
        if(not path.endswith('.pdf')):
            path += ".pdf"
        self.fh = open(path, 'wb')
        self.pdf_obj = PdfFileWriter()
    
    def addPage(self, page):
        self.pdf_obj.addPage(page)
    
    def write(self):
        self.pdf_obj.write(self.fh)

class user_input:
    val = None
    original_val = None
    def __init__(self, prompt, i_prompt, typ, valid_choices = None, invalid_choices = None, fun = None):
        while(True):
            try:
                val = input(prompt)
                if (typ == "str"):
                    val = str(val)
                elif (typ == "int"):
                    val = int(val)
                if ((valid_choices != None) and (invalid_choices != None) and (val not in valid_choices) and
                        (val in invalid_choices)):
                    raise Exception
                elif (valid_choices != None) and (val not in valid_choices):
                    raise Exception
                elif (invalid_choices != None) and (val in invalid_choices):
                    raise Exception
                if fun == None:
                    self.val = val
                else:
                    self.val = fun(val)
                    self.original_val = val
                break
            except Exception as e:
                print(i_prompt)
                print(e)
    
    def __str__(self):
        return self.val
    
    def __int__(self):
        return self.val
    
    def get_obj(self):
        return self.val
    
    def get_original_val(self):
        return self.original_val


def print_intro(terminal_width):
    os.system('clear')
    s = "welcome to pdf editing"
    s = "-" * terminal_width + "\n" + \
        "-" * int((terminal_width - len(s)) / 2) + \
        s + \
        "-" * int((terminal_width - len(s)) / 2) + "\n" + \
        "-" * terminal_width + "\n"
    print(s)


def open_pdf(pdfs, pages, status, protected_names, terminal_width):
    pdf = user_input("witch is the name of the file? ", "invaid file name", "str", None, None, pdfReader)
    path = pdf.get_original_val()
    pdf = pdf.get_obj()
    
    name = str(user_input("input a name for this pdf: ", "invalid name", "str", None,
                          protected_names + list(pdfs.keys()) + list(pages.keys())))
    
    pdfs[name] = pdf
    
    print("pdf info:" + "\n" + "-" * terminal_width)
    print("getDocumentInfo:" + "\n" + "." * terminal_width)
    print(pdfs[name].getDocumentInfo())
    print("'" * terminal_width)
    print("getNumPages: " + str(pdfs[name].getNumPages()))
    print("'" * terminal_width)
    print("getOutlines:" + "\n" + "." * terminal_width)
    print(pdfs[name].getOutlines())
    print("'" * terminal_width)
    print("-" * terminal_width)
    input()
    status += "opened new pdf with name: " + name + ", path: " + path + "\n"


def get_page_from_range(pdfs, pages, status, protected_names, terminal_width, name, pdf):
    p = []
    
    #### hereeeeeee
    
    while (True):
        r = input("\tspecify the range of pages to be extracted in the format: [min, max] \n" + "\t" + "-" * 10 + "> ")
        # TODO: refactor this part, is ugly, issue #2
        try:
            rej = re.compile(r"\[(\d+),\s*(\d+)\]")
            ins = rej.match(r)
            lim_inf = int(ins.group(1))
            lim_sup = int(ins.group(2))
        except:
            try:
                rej = re.compile(r"(\d+),\s*(\d+)")
                ins = rej.match(r)
                lim_inf = int(ins.group(1))
                lim_sup = int(ins.group(2))
            except:
                print("\tinvalid limits")
                continue
        if (lim_inf < 0) or (lim_sup > pdf.getNumPages()) or (lim_inf > lim_sup):
            print("\tinvalid limits")
            continue
        for i in range(lim_inf, lim_sup):
            p.append(pdf.getPage(i))
        break
    
    namepage = user_input("input a name for this pages: ", "invalid name", "str", None,
                          protected_names + list(pdfs.keys()) + list(pages.keys())).get_obj()
    
    pages[namepage] = p
    
    status += "extracted from pdf \"" + name + "\" a range of pages [" + str(lim_inf) + ", " + str(
        lim_sup) + "] and saved in \"" + namepage + "\n"


def get_page_from_gen(pdfs, pages, status, protected_names, terminal_width, name, pdf):
    p = []
    k = symbols('k')
    
    eq = user_input("\tinput a generator using k as the variable" + \
                    "\n\texamples\n\t-> 2*k = all the even pages\n\t-> 2*k+1 all the odd pages\n\t" + \
                    "-" * 10 + "> ",
                    "invalid syntax", "str", None, None, parse_expr)
    
    generator = eq.get_original_val()
    eq = eq.get_obj()
    
    ############# da includere nel try dell'input, issue #1
    subs = (eq.subs(k, i) for i in count())
    gen = takewhile(lambda x: x < pdf.getNumPages(), subs)
    for n in gen:
        p.append(pdf.getPage(n))
    ###############
    
    namepage = user_input("input a name for this pages: ", "invalid name", "str", None,
                          protected_names + list(pdfs.keys()) + list(pages.keys())).get_obj()
    
    pages[namepage] = p
    
    status += "extracted from pdf \"" + name + "\" a generated set of pages through a generator: " + generator + ", and saved in \"" + namepage + "\n"


def get_pages_from_pdf(pdfs, pages, status, protected_names, terminal_width):
    #### hereeeeeeeee
    while (True):
        name = input("from witch pdf you want to extract the pages? \n" + \
                     "type [lsPdf] to get the list of opened pdfs \n " + \
                     "-" * 10 + "> ")
        if (name == '' or name == "lsPdf"):
            print("\t-> " + "\n\t-> ".join(pdfs.keys()))
        elif (name not in pdfs.keys()):
            print("invalid name, the list of all valid name are: \n\t-> " + "\n\t-> ".join(pdfs.keys()))
        else:
            break
    pdf = pdfs[name]
    
    while (True):
        s = "\t1. get the number of pages in this pdf \n" + \
            "\t2. select a range and get those pages \n" + \
            "\t3. specify a generator for getting the pages \n" + \
            "\t4. return to main manu \n" + \
            "\t" + "-" * 10 + "> "
        choice = user_input(s, "invalid input", "int", range(1, 5)).get_obj()
        
        if choice == 1:
            print("\tthe pdf have " + str(pdf.getNumPages()) + " pages\n")
        elif choice == 2:
            get_page_from_range(pdfs, pages, status, protected_names, terminal_width, name, pdf)
        elif choice == 3:
            get_page_from_gen(pdfs, pages, status, protected_names, terminal_width, name, pdf)
        elif choice == 4:
            break


def save_pdf(pdfs, pages, status, protected_names, terminal_width):
    #### hereeeeeee
    
    while (True):
        name = input("which set of page do you wanto to save in pdf? \n" + \
                     "type [lsPg] to get the list of saved sets of page \n " + \
                     "-" * 10 + "> ")
        if (name == '' or name == "lsPg"):
            print("\t-> " + "\n\t-> ".join(pages.keys()))
        elif (name not in pages.keys()):
            print("invalid name, the list of all valid name are: \n\t-> " + "\n\t-> ".join(pages.keys()))
        else:
            break
    
    pdf = user_input("witch is the name of the file? ", "invaid file name", "str", None, None, pdfWriter)
    path = pdf.get_original_val()
    pdf = pdf.get_obj()
    
    ########### da includere nel try dell'input, issue #1
    for page in pages[name]:
        pdf.addPage(page)
    pdf.write()
    #############
    
    status += "saved the set of pages \"" + name + "\" in the file located in  \"" + path + "\"\n"


def terminal_input(terminal_width):
    protected_names = ["lsPdf", "lsPg", "ls", "cd", "k"]
    pdfs = dict()
    pages = dict()
    status = ""
    while (True):
        
        s = "1. open pdf file" + "\n" + \
            "2. get pages from an opened pdf" + "\n" + \
            "3. mix sets of pages" + "\n" + \
            "4. remove pages from a set of pages" + "\n" + \
            "5. " + "\n" + \
            "6. print the status" + "\n" + \
            "7. save a pdf" + "\n" + \
            "8. exit" + "\n" + \
            "-" * 10 + "> "
        try:
            choice = int(input(s))
        except:
            choice = -1
        if choice == 1:
            # TODO: aggiungere ls quando devi aprire un file e magari anche
            # cd e qualcosa per far funzionare il tab
            # vedi --> https://stackoverflow.com/questions/187621/how-to-make-a-python-command-line-program-autocomplete-arbitrary-things-not-int
            open_pdf(pdfs, pages, status, protected_names, terminal_width)
        elif choice == 2:
            get_pages_from_pdf(pdfs, pages, status, protected_names, terminal_width)
        elif choice == 3:
            pass
        elif choice == 4:
            pass
        elif choice == 5:
            pass
        elif choice == 6:
            print(status)
        elif choice == 7:
            save_pdf(pdfs, pages, status, protected_names, terminal_width)
        elif choice == 8:
            break
        else:
            print("invalid choice")
        os.system('clear')
        print_intro(terminal_width)


if __name__ == '__main__':
    
    terminal_dim = os.popen('stty size', 'r').read().split()
    terminal_dim = [int(terminal_dim[0]), int(terminal_dim[1])]
    
    print_intro(terminal_dim[1])
    
    opt = input("configure from [f]ile or [T]erminal: ")
    if opt == "" or opt == "t" or opt == "T":
        terminal_input(terminal_dim[1])
    elif opt == "f" or opt == "F":
        print("file")
    
    input("\n\nwaiting")

# pages = pdf_splitter("slide.pdf")
# pdf_concatenate(pages, "aaa2.pdf", "out.pdf")
