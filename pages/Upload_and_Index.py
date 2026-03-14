import streamlit as st

from knowledge_ingest import index_uploaded_file

st.set_page_config(page_title="Upload & Index")

st.title("Upload and Index Documents")
st.subheader("Add PDF or CSV files to your vector database")
st.caption("1) Choose a file, 2) Click Upload and Index")

if st.button("💬 Back to Chat"):
    try:
        st.switch_page("app.py")
    except Exception:
        st.info("Use the left sidebar to return to the chat page.")

uploaded_file = st.file_uploader(
    "Upload a PDF or CSV file",
    type=["pdf", "csv"],
    help="The file will be chunked, embedded, and added to the vector database."
)

if st.button("Upload and Index", type="primary", disabled=uploaded_file is None):
    with st.spinner("Reading file and indexing to vector database..."):
        try:
            result = index_uploaded_file(uploaded_file)
            st.success(
                f"Indexed {result['chunks_indexed']} chunks from {result['file_name']}"
            )
        except Exception as error:
            st.error(f"Indexing failed: {error}")
