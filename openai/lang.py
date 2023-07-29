import pandas as pd
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

def load_and_convert_data(path_excel, path_csv):
    # Leer el archivo de Excel
    df = pd.read_excel(path_excel)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv(path_csv, index=False)

def load_data_from_csv(path_csv):
    loader = CSVLoader(file_path=path_csv)
    data = loader.load()
    return data

def split_text(data, chunk_size=1500, chunk_overlap=150):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size, chunk_overlap)
    splits = text_splitter.split_documents(data)
    return splits

def embed_text(splits):
    embedding = OpenAIEmbeddings()

    # Crear lista de textos desde documentos divididos
    text_list = [doc.page_content for doc in splits]

    # Realizar embedding en los textos
    embeddings = embedding.embed_documents(text_list)
    return embeddings

def load_into_chroma(splits, embeddings):
    # Load embeddings into Chroma
    db = Chroma.from_documents(splits, embeddings)
    return db

def find_similar_documents(db, query, top_k=50, limit=50):
    # Realizar una búsqueda de similitud
    similar_docs = db.similarity_search(query, top_k, limit)
    return similar_docs
