import streamlit as st
import math
import re
import wikipedia


st.set_page_config(page_title="CosmoSearch Google-Edition", page_icon="🌌", layout="centered")


base_documents = [
    {"id": 1, "title": "Wormhole",
     "content": "A wormhole or Einstein-Rosen bridge is a hypothetical structure connecting disparate points in spacetime."},
    {"id": 2, "title": "White Hole",
     "content": "A white hole is a hypothetical celestial object and cosmic region which matter and light can escape from."},
    {"id": 3, "title": "Black Hole",
     "content": "A black hole is a region of spacetime where gravity is so strong that nothing, including light, can escape."},
    {"id": 4, "title": "Milky Way Galaxy",
     "content": "The Milky Way is the barred spiral galaxy that contains our Solar System, Earth, and billions of stars."}
]



def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()


def build_inverted_index(docs):
    inverted_index = {}
    for doc in docs:
        doc_id = doc['id']
        combined_text = doc['title'] + " " + doc['content']
        tokens = preprocess(combined_text)
        for token in tokens:
            if token not in inverted_index:
                inverted_index[token] = set()
            inverted_index[token].add(doc_id)
    return inverted_index


def calculate_tfidf(query_tokens, doc_id, docs, index):
    total_docs = len(docs)
    score = 0.0
    doc_text = next(d for d in docs if d['id'] == doc_id)
    total_words = len(preprocess(doc_text['title'] + " " + doc_text['content']))

    for token in query_tokens:
        if token in index and doc_id in index[token]:
            tf = len([t for t in preprocess(doc_text['title'] + " " + doc_text['content']) if t == token]) / total_words
            docs_with_token = len(index[token])
            idf = math.log(total_docs / docs_with_token) + 1
            score += tf * idf
    return score



def search_universe(query, mode="OR"):

    dynamic_docs = list(base_documents)
    try:

        search_titles = wikipedia.search(query + " space astronomy", results=5)

        current_id = 100
        for title in search_titles:
            try:
                page_summary = wikipedia.summary(title, sentences=3, auto_suggest=False)
                dynamic_docs.append({
                    "id": current_id,
                    "title": title,
                    "content": page_summary
                })
                current_id += 1
            except:
                continue
    except:
        pass


    live_index = build_inverted_index(dynamic_docs)


    query_tokens = preprocess(query)
    if not query_tokens:
        return []

    matched_doc_ids = set()
    if mode == "AND":
        if query_tokens[0] in live_index:
            matched_doc_ids = set(live_index[query_tokens[0]])
        for token in query_tokens[1:]:
            if token in live_index:
                matched_doc_ids = matched_doc_ids.intersection(live_index[token])
            else:
                matched_doc_ids = set()
    else:
        for token in query_tokens:
            if token in live_index:
                matched_doc_ids = matched_doc_ids.union(live_index[token])

    results = []
    for doc_id in matched_doc_ids:
        score = calculate_tfidf(query_tokens, doc_id, dynamic_docs, live_index)
        doc_details = next(d for d in dynamic_docs if d['id'] == doc_id)
        results.append({
            "title": doc_details['title'],
            "content": doc_details['content'],
            "score": round(score, 4)
        })
    return sorted(results, key=lambda x: x['score'], reverse=True)




st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🌌 CosmoSearch</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #757575;'>Explore Planets, Exoplanets, and Nebulae beyond our Solar System</p>", unsafe_allow_html=True)


query = st.text_input("", placeholder="🔍 Search the entire universe (e.g., Mars, Supernova, Hubble, Yuri Gagarin)...",
                      label_visibility="collapsed")

st.sidebar.header("⚙️ Search Engine Core")
search_mode = st.sidebar.radio("Logic Mode:", ("OR (Broad Search)", "AND (Strict Filter)"))
mode = "AND" if "AND" in search_mode else "OR"

st.sidebar.markdown("---")
st.sidebar.success("🚀 Now Connected to Global Space Archives! Infinite Data Mode Enabled.")

if query:
    with st.spinner('Scanning the universe...'):
        results = search_universe(query, mode=mode)

    if results:
        st.write(f"✨ About {len(results)} cosmic results found:")
        for res in results:
            with st.container():
                st.markdown(f"<h3 style='color: #1a0dab; margin-bottom: 0px;'>🪐 {res['title']}</h3>",
                            unsafe_allow_html=True)

                content = res['content']
                for q_token in preprocess(query):
                    pattern = re.compile(f"({q_token})", re.IGNORECASE)
                    content = pattern.sub(r"**\1**", content)

                st.write(content)
                st.markdown(
                    f"<span style='color: #006621; font-size: 12px;'>Data Mining Match Score: {res['score']}</span>",
                    unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.error("🚀 Nothing found in this galaxy. Try another cosmic term!")