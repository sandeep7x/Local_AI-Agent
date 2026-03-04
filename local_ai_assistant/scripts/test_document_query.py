import os
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image
import pytesseract
import pandas as pd

DOCS_PATH = os.path.join('data','documents')
q = 'when will the company expand into robotics'
q_tokens = [t for t in q.lower().split() if len(t) > 2]

print('Query tokens:', q_tokens)

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
        print('Error loading', file, e)
        continue

    low = content.lower()
    if any(tok in low for tok in q_tokens):
        print('Match in', file)
        print('Snippet:', low[:500])
    else:
        print('No match in', file)
