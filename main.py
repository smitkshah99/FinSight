import os
import streamlit as st
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.vectorstores import AstraDB

load_dotenv()


def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.vectorstore = None
        st.session_state.query = ""


def display_title_and_sidebar():
    st.header("Today's Finance News\nYour Opportunity to Ask Me Anything! 📈")
    # st.sidebar.title("News Article URLs")


def process_urls(urls):
    loader = UnstructuredURLLoader(urls=urls)
    st.empty().text("Data Loading...Started...✅✅✅")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000
    )
    st.empty().text("Text Splitter...Started...✅✅✅")
    docs = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings()

    astra_vector_store = AstraDB(
        embedding=embeddings,
        collection_name="astra_vector_demo",
        api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
        token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
    )
    inserted_ids = astra_vector_store.add_documents(docs)
    print(f"\nInserted {len(inserted_ids)} documents.")

    vectorstore = FAISS.from_documents(docs, embeddings)
    st.empty().text("Embedding Vector Started Building...✅✅✅")

    st.session_state.vectorstore = vectorstore


@st.cache_data
def proces_questions(query, _astra_vector_store):
    llm = OpenAI(temperature=0.3, max_tokens=1000)
    chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=_astra_vector_store.as_retriever())
    result = chain({"question": query}, return_only_outputs=True)
    return result


def get_question_and_answer(query, astra_vector_store):
    if query and st.session_state.initialized:
        result = proces_questions(query, astra_vector_store)

        st.header("Answer")
        st.write(result["answer"])

        sources = result.get("sources", "")
        if sources:
            st.subheader("Sources:")
            sources_list = sources.split("\n")
            for source in sources_list:
                st.write(source)


@st.cache_resource
def openaiembedding():
    print("++++++++++++++++++++++++")
    embeddings = OpenAIEmbeddings()
    astra_vector_store = AstraDB(
        embedding=embeddings,
        collection_name="astra_vector_demo",
        api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
        token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
    )
    return embeddings, astra_vector_store


def main1():
    initialize_session_state()
    embeddings, astra_vector_store = openaiembedding()
    display_title_and_sidebar()

    predefined_questions = [
        "What are the latest market trends?",
        "Tell me about recent financial innovations.",
        "How did the stock market perform today?"
    ]

    columns = st.columns(len(predefined_questions))
    # Display buttons in columns
    for i, predefined_question in enumerate(predefined_questions):
        with columns[i]:
            # If a predefined question button is clicked, update the text input
            if st.button(predefined_question, key=f"button_{predefined_question}"):
                st.session_state.query = predefined_question

    # Text input for user-defined questions
    user_question_key = "user_question_input"
    st.session_state.query = st.text_input("Question:", value=st.session_state.query, key=user_question_key)

    # Check if the user has typed a question and trigger the function
    if st.session_state.query:
        st.session_state.initialized = True
        get_question_and_answer(st.session_state.query, astra_vector_store)


if __name__ == "__main__":
    main1()
