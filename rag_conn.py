# lets make all the required rag connections
import numpy as np 
import faiss
from sentence_transformers import SentenceTransformer 

from langchain_text_splitters import CharacterTextSplitter

model = SentenceTransformer('all-MiniLM-L6-v2')

idx = faiss.IndexFlatL2(384)

all_doc = []

# function gives us the chunk text from the docs
def add_doc(text, doc_id):
    global all_doc

    split = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = split.split_text(text)
    if not chunks:
        return
    embds =  model.encode(chunks)

    idx.add(np.array(embds).astype('float32'))

    for c in chunks:
        all_doc.append({
            "doc_id": doc_id,
            "text": c
        })  

# implement the search method and retrieve the top 5 result

def find(query):
    if len(all_doc) == 0:
        return []
    query_vec = model.encode([query])

    D,I = idx.search(np.array(query_vec).astype('float32'),20)

    res = []
    for i in I[0]:
        if i < len(all_doc):
            res.append(all_doc[i])

    res = sorted(res,key = lambda x: query.lower() in x["text"].lower(),reverse=True)

    return res[:5]    


# function for deleting the doc

def del_doc(doc_id):
    global all_doc

    all_doc = [doc for doc in all_doc if doc["doc_id"] != doc_id]

    return True                