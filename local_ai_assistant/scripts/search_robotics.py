import os
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd
from PIL import Image
import pytesseract

DOCS_PATH = os.path.join('data','documents')
term = 'robot'
print('Searching for term:', term)
for file in os.listdir(DOCS_PATH):
    full = os.path.join(DOCS_PATH, file)
    content = ''
    try:
        if file.endswith('.pdf'):
            loader = PyPDFLoader(full)
            docs = list(loader.load())
            content = '\n\n'.join([d.page_content for d in docs])
        elif file.endswith('.csv'):
            df = pd.read_csv(full)
            content = df.to_csv(index=False)
        elif file.lower().endswith(('.png','.jpg','.jpeg')):
            content = pytesseract.image_to_string(Image.open(full))
        else:
            with open(full,'r',encoding='utf-8',errors='ignore') as f:
                content = f.read()
    except Exception as e:
        print('Error', file, e)
        continue
    if term in content.lower():
        print('Found in', file)
        start = content.lower().find(term)
        print(content[max(0,start-200):start+200])
    else:
        print('Not found in', file)
