# ExtendedAbstractGPT
Breaks down PDFs by the main chapter headlines and lets GPT summarize each chapter in 1-2 sentences
Limitation: If the chapter headlines have inconsistent font sizes or there is new abstract or introduction in the paper


Installation:
- get an API key for OPENAI 
- pip install the requirements
- pip install pyinstaller
- cd .../ExtendedAbstractGPT
-  pyinstaller --onefile --windowed --console .\pdfGPT.py

TODO
(x) add connection to GPT <br>
(x) let user enter own API key<br>
(x) create simple GUI<br>
(x) reduce tokensize of each text input to under 1000 tokens by recursively subdividing the paragraph in two halves<br>
() support subchapters<br>
() improve GUI<br>


