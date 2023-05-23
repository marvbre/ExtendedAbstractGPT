import os

import tkinter as tk
from tkinter import filedialog
import requests
import json
import os
import openai
import re
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import numpy as np

openai.organization = "YOUR_ORG_KEY"
openai.api_key = os.getenv("OPENAI_API_KEY")

def count_letters(s):
    return sum(c.isalpha() for c in s)

def count_digits(s):
    return sum(c.isdigit() for c in s)

def filter_letters(input_string):
    return ''.join(char for char in input_string if char.isalpha())

def check_tokencount(prompt):
    tcount = len(re.findall(r'\w+', prompt))
    tcount += sum(1 for char in prompt if char == "?")
    return tcount

def reduceTokens(text_batches, maxTokens):
    
    "This function divides a string text into halves until it is smaller than the specified number of tokens"
        
    for batch in text_batches:
                
        if(check_tokencount(batch) > maxTokens):
            
            batchA = batch[0:len(batch)//2]
            batchB = batch[len(batch)//2:]
            text_batches = [batchA, batchB]
            return reduceTokens(text_batches, maxTokens)
        else:
            return text_batches
        
def read_pdf(path):

    psum = {}
    current_chapter = "metadata"


    # Open a PDF file
    with open(path, 'rb') as fp:

        # Create a PDF parser object associated with the file object
        parser = PDFParser(fp)
        # Create a PDF document object that stores the document structure
        document = PDFDocument(parser)
        # Connect the parser and document objects
        parser.set_document(document)

        # Set up the PDF resources manager and device
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        abstractFound = False
        clines = []

        # collect fonts

        fontsizes = []

        for page in PDFPage.create_pages(document):

            interpreter.process_page(page)
            layout = device.get_result()

            for element in layout:
                fontsizes.append(int(element.height))
                
                if hasattr(element, "get_text"):
                    
                    if("Introduction" in element.get_text()):
                        headingsize = int(element.height)
                        print("Heading size:", headingsize)
                        break
                    

        avgfontsize = np.median(fontsizes)
        unique, counts = np.unique(fontsizes, return_counts=True)
        fontsizeOcc = dict(zip(unique, counts))
        
        print(np.median(counts[counts > 5]))
        
        possibles = []
        for fs, occ in zip(unique, counts):
            if(occ < 2):
                pass
            elif(occ > np.max(counts)//2):
                pass
            else:
                #print("Fontsize:", int(fs), " and occurence: ", occ, " times")
                possibles.append(int(fs))
        
        
        

        # Loop through the pages
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()



            for element in layout:
                if hasattr(element, "get_text"):

                    text = element.get_text()

                    if("abstract" in text.lower()):

                        if not abstractFound:
                            psum[current_chapter]=' '.join(clines).replace("- ", "")
                            abstractFound = True
                            clines = []
                            current_chapter = "abstract"

                    if("References" in text):
                        psum["Conclusion"]=' '.join(clines).replace("- ", "").replace("-\n", "").replace("\n", "")
                        clines = []
                        break
                         
                    if(int(element.height) == headingsize):
                        if(0 < count_digits(text) < 3):
                            
                            if(("(" in text) or (":" in text) or ("=" in text) or ("citation" in text.lower()) or ("figure" in text.lower()) or ("table" in text.lower())):
                                    pass
                            else:
                                print(f"Font size: {element.height}, Text: {element.get_text()}")
                                #print(round(element.height,1))
                                psum[current_chapter]=' '.join(clines).replace("- ", "").replace("-\n", "").replace("\n", "")
                                clines = []
                                current_chapter =  filter_letters(text)

                    clines.append(text)
    print("Subdivided PDF")
    return psum

def askGPT(prompt):

    openai.api_key = entry.get()
    
    print(check_tokencount(prompt) )
    if(check_tokencount(prompt) > 1500):
        return "prompt is too long!"
    else:
        # Set up your key, headers and endpoint
        url = 'https://api.openai.com/v1/completions'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {openai.api_key}'}
        # Set up the data for your prompt
        data = {'model' : 'text-davinci-003',
                'prompt' :  prompt,
                'max_tokens' : 1000}

        data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data)
        #response = 0
        try:
            answer = response.json()["choices"][0]['text'].replace("\n","")
            return answer
        except:
            return response.json()


# Function to open a file dialog and extract text from the selected PDF file
def open_file():

    filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

    text_box.delete('1.0', tk.END)  # clear the text box

    text_box.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))

    if filepath:

        chapters = read_pdf(filepath)

        for chapter in chapters.keys():
    
            if(chapter == "metadata"):
                pass
            elif(chapter == "abstract"):
                pass
            else:
                text_box.insert(tk.END, chapter + "\n", "bold")  # insert the text into the text box
                print(chapter)

                ctext = chapters[chapter]

                ctextList = reduceTokens([ctext], 1500)

                text_box.insert(tk.END, "Response:")

                for ctex in ctextList:

                    responded = askGPT("Summarize the most important points of the following text in 1-2 sentences: " + ctex)
                    print(responded)
                    
                    text_box.insert(tk.END, str(responded) + "\n")
                    print("\n")
                

# Create the main window
root = tk.Tk()

# Create a scrollable text box
text_box = tk.Text(root, wrap='word')
text_box.grid(row=3, column=0)

#create a user input field
# Create an Entry widget
entry = tk.Entry(root)
entry.insert(0, ">Put in your OPENAI API key here:<")
entry.grid(row=0, column=0,sticky='ew')

# Add a scrollbar to the text box
scrollbar = tk.Scrollbar(root, command=text_box.yview)
scrollbar.grid(row=3, column=1)

# Configure the text box to use the scrollbar
text_box['yscrollcommand'] = scrollbar.set

# Create a button to open the file dialog
text_box.insert(tk.END, "Processing may take a few minutes! Watch the console for error messages.")

open_button = tk.Button(root, text="Open PDF", command=open_file)
open_button.grid(row=2, column=0)

# Start the main event loop
root.mainloop()
