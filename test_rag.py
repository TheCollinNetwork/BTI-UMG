import argparse
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = Ollama(model="mistral")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

def main():
    print("Welcome to the Q&A system. Type 'exit' to quit.")
    while True:
        # Prompt the user for a question.
        question = input("Enter your question: ")
        if question.lower() == 'exit':
            print("Goodbye!")
            break

        # Prompt the user for the expected response (optional).
        expected_response = input("Enter the expected response (or press Enter to skip): ")

        # Query the system.
        print("\nQuerying...\n")
        actual_response = query_rag(question)

        # If an expected response is provided, evaluate it.
        if expected_response:
            evaluation_prompt = f"""
            Expected Response: {expected_response}
            Actual Response: {actual_response}
            ---
            (Answer with 'true' or 'false') Does the actual response match the expected response? 
            """
            model = Ollama(model="mistral")
            evaluation_result = model.invoke(evaluation_prompt).strip().lower()

            if "true" in evaluation_result:
                print("\033[92mThe response matches the expected answer.\033[0m")
            elif "false" in evaluation_result:
                print("\033[91mThe response does not match the expected answer.\033[0m")
            else:
                print("\033[93mCould not determine if the response matches.\033[0m")

if __name__ == "__main__":
    main()
