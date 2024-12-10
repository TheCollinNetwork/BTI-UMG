import argparse
import os
import shutil
import concurrent.futures
import time
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader

CHROMA_PATH = "chroma"
DATA_PATH = os.getenv("DATA_PATH", "data")  # Default to "data" if the env var isn't set
CHECK_INTERVAL = 60  # Time in seconds between directory checks

def main():
    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Initialize the Chroma database and start monitoring.
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    
    # Periodically check for new documents and update the database.
    while True:
        print("🔍 Checking for new documents...")
        print(f"DATA_PATH is set to: {DATA_PATH}")
        documents = load_documents()
        chunks = split_documents(documents)  # Split documents into chunks
        add_to_chroma(db, chunks)  # Add chunks to the Chroma database

        print(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)  # Wait before checking again

def load_documents():
    # Load all PDF documents from the specified directory.
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def load_csv():
    # Prompt user for the CSV file path, if any.
    x = input('Enter the path of the CSV (if there is none press enter): ')
    if x == '':
        return []
    else:
        # Load CSV documents.
        csv_loader = CSVLoader(file_path=x, encoding='utf-8')
        return csv_loader.load()

def split_documents(documents: list[Document]):
    # Initialize the text splitter to break documents into manageable chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )

    # Split documents into chunks concurrently.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(text_splitter.split_documents, [doc]): doc for doc in documents}
        chunks = []
        for future in concurrent.futures.as_completed(futures):
            chunks.extend(future.result())
    
    return chunks  # Return the list of document chunks

def add_to_chroma(db, chunks: list[Document]):
    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents in the Chroma DB.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")

def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks  # Return the chunks with calculated IDs

def clear_database():
    # Remove the Chroma database directory.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

if __name__ == "__main__":
    main()  # Run the main function
