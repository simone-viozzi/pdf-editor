# install
# sudo -H pip3 install --upgrade pip
# sudo -H python3.6 -m pip install -U pymupdf


import os


from pdfrw import *

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from itertools import count, takewhile
import regex as re
import json



class PdfReaderW:
    pdf_obj = None
    
    def __init__(self, path):
        if not path.endswith('.pdf'):
            path += ".pdf"
        self.pdf_obj = PdfReader(path)
    
    def getPage(self, i):
        return self.pdf_obj.pages[i]
    
    def get_document_info(self):
        s = ""
        for k in self.pdf_obj.keys():
            a = re.sub(r'\{\.\.\.\}', r'"\g<0>"', re.sub(r'\(\d+,\s?\d+\)', r'"\g<0>"', str(self.pdf_obj[k]).replace("'", '"')))
            a = re.sub(r"\"\/Kids\":\s?(\[(?>([^\[\]])+|\[([^\[\]])+\])*\])", '"/Kids": "{...}"', a)
            json_object = json.loads(a)
            json_formatted_str = json.dumps(json_object, indent=2)
            s += ". " * 5 + "\n" + str(k) + ': ' + "\n" + str(json_formatted_str) + "\n"
        return s
    
    def get_num_pages(self):
        return len(self.pdf_obj.pages)
    
    def get_outlines(self):
        return None


class PdfWriterW:
    fh = None
    pdf_obj = None
    
    def __init__(self, path):
        if not path.endswith('.pdf'):
            path += ".pdf"
        self.fh = open(path, 'wb')
        self.pdf_obj = PdfWriter()
    
    def add_page(self, page):
        self.pdf_obj.addPage(page)
    
    def write(self):
        self.pdf_obj.write(self.fh)


class UserInput:
    val = None
    original_val = None
    
    def __init__(self, prompt, i_prompt, typ, valid_choices=None, invalid_choices=None, fun=None):
        while True:
            try:
                val = input(prompt)
                if typ == "str":
                    val = str(val)
                elif typ == "int":
                    val = int(val)
                if ((valid_choices is not None) and (invalid_choices is not None) and (val not in valid_choices) and
                        (val in invalid_choices)):
                    raise Exception
                elif (valid_choices is not None) and (val not in valid_choices):
                    raise Exception
                elif (invalid_choices is not None) and (val in invalid_choices):
                    raise Exception
                if fun is None:
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
    os.system('clear') if os.name == 'posix' else os.system('cls')
    s = "welcome to pdf editing"
    s = "-" * terminal_width + "\n" + \
        "-" * int((terminal_width - len(s)) / 2) + \
        s + \
        "-" * int((terminal_width - len(s)) / 2) + "\n" + \
        "-" * terminal_width + "\n"
    print(s)


def open_pdf(pdfs, pages, status, protected_names, terminal_width):
    pdf = UserInput("witch is the name of the file? ", "invalid file name", "str", None, None, PdfReaderW)
    path = pdf.get_original_val()
    pdf = pdf.get_obj()
    
    name = str(UserInput("input a name for this pdf: ", "invalid name", "str", None,
                         protected_names + list(pdfs.keys()) + list(pages.keys())))
    
    pdfs[name] = pdf
    
    print("pdf info:" + "\n" + "-" * terminal_width)
    print("getDocumentInfo:" + "\n" + "." * terminal_width)
    print(pdfs[name].get_document_info())
    print("'" * terminal_width)
    print("getNumPages: " + str(pdfs[name].get_num_pages()))
    print("'" * terminal_width)
    print("getOutlines:" + "\n" + "." * terminal_width)
    print(pdfs[name].get_outlines())
    print("'" * terminal_width)
    print("-" * terminal_width)
    input()
    status += "opened new pdf with name: " + name + ", path: " + path + "\n"


def get_page_from_range(pdfs, pages, status, protected_names, terminal_width, name, pdf):
    p = []
    
    #### hereeeeeee
    
    while True:
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
        if (lim_inf < 0) or (lim_sup > pdf.get_num_pages()) or (lim_inf > lim_sup):
            print("\tinvalid limits")
            continue
        for i in range(lim_inf, lim_sup):
            p.append(pdf.getPage(i))
        break
    
    name_page = UserInput("input a name for this pages: ", "invalid name", "str", None,
                          protected_names + list(pdfs.keys()) + list(pages.keys())).get_obj()
    
    pages[name_page] = p
    
    status += "extracted from pdf \"" + name + "\" a range of pages [" + str(lim_inf) + ", " + str(
            lim_sup) + "] and saved in \"" + name_page + "\n"


def get_page_from_gen(pdfs, pages, status, protected_names, terminal_width, name, pdf):
    p = []
    k = symbols('k')
    
    eq = UserInput("\tinput a generator using k as the variable" + \
                   "\n\texamples\n\t-> 2*k = all the even pages\n\t-> 2*k+1 all the odd pages\n\t" + \
                   "-" * 10 + "> ",
                   "invalid syntax", "str", None, None, parse_expr)
    
    generator = eq.get_original_val()
    eq = eq.get_obj()
    
    ############# da includere nel try dell'input, issue #1
    subs = (eq.subs(k, i) for i in count())
    gen = takewhile(lambda x: x < pdf.get_num_pages(), subs)
    for n in gen:
        p.append(pdf.getPage(n))
    ###############
    
    namepage = UserInput("input a name for this pages: ", "invalid name", "str", None,
                         protected_names + list(pdfs.keys()) + list(pages.keys())).get_obj()
    
    pages[namepage] = p
    
    status += "extracted from pdf \"" + name + "\" a generated set of pages through a generator: " + generator + ", and saved in \"" + namepage + "\n"


def get_pages_from_pdf(pdfs, pages, status, protected_names, terminal_width):
    #### hereeeeeeeee
    while True:
        name = input("from witch pdf you want to extract the pages? \n" + \
                     "type [lsPdf] to get the list of opened pdfs \n " + \
                     "-" * 10 + "> ")
        if name == '' or name == "lsPdf":
            print("\t-> " + "\n\t-> ".join(pdfs.keys()))
        elif name not in pdfs.keys():
            print("invalid name, the list of all valid name are: \n\t-> " + "\n\t-> ".join(pdfs.keys()))
        else:
            break
    pdf = pdfs[name]
    
    while (True):
        s = "\t1. get the number of pages in this pdf \n" + \
            "\t2. select a range and get those pages \n" + \
            "\t3. specify a generator for getting the pages \n" + \
            "\t4. return to main menu \n" + \
            "\t" + "-" * 10 + "> "
        choice = UserInput(s, "invalid input", "int", range(1, 5)).get_obj()
        
        if choice == 1:
            print("\tthe pdf have " + str(pdf.get_num_pages()) + " pages\n")
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
        if name == '' or name == "lsPg":
            print("\t-> " + "\n\t-> ".join(pages.keys()))
        elif name not in pages.keys():
            print("invalid name, the list of all valid name are: \n\t-> " + "\n\t-> ".join(pages.keys()))
        else:
            break
    
    pdf = UserInput("witch is the name of the file? ", "invaid file name", "str", None, None, PdfWriterW)
    path = pdf.get_original_val()
    pdf = pdf.get_obj()
    
    ########### da includere nel try dell'input, issue #1
    for page in pages[name]:
        pdf.add_page(page)
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


import os


def get_windows_terminal():
    from ctypes import windll, create_string_buffer
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    
    # return default size if actual size can't be determined
    if not res: return 80, 25
    
    import struct
    (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) \
        = struct.unpack("hhhhHhhhhhh", csbi.raw)
    width = right - left + 1
    height = bottom - top + 1
    
    return width, height


def get_linux_terminal():
    width = os.popen('tput cols', 'r').readline()
    height = os.popen('tput lines', 'r').readline()
    
    return int(width), int(height)


if __name__ == '__main__':
    terminal_dim = get_linux_terminal() if os.name == 'posix' else get_windows_terminal()
    
    print_intro(terminal_dim[0])
    
    opt = input("configure from [f]ile or [T]erminal: ")
    if opt == "" or opt == "t" or opt == "T":
        terminal_input(terminal_dim[0])
    elif opt == "f" or opt == "F":
        print("file")
    
    input("\n\nwaiting")


