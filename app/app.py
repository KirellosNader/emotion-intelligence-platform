import os
import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# python-dotenv اختياري وقت التشغيل: على Colab لازم نقرا ملف .env بالإيد، بينما على
# Streamlit Cloud / Docker المتغيرات بتتحقن مباشرة كـ environment variables حقيقية.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

st.set_page_config(page_title="Customer Emotion Intelligence", page_icon="\\U0001F60A", layout="wide")

MODEL_PATH = "saved_models/emotion_model.pkl"
VECTORIZER_PATH = "saved_models/tfidf_vectorizer.pkl"
LABELS_PATH = "saved_models/labels.pkl"
DATA_PATH = "saved_models/emotion_data.csv"

LOG_PATH = "logs/prediction_log.csv"
os.makedirs("logs", exist_ok=True)


def log_prediction(text, predicted_label, source="single", confidence=None):
    """Append a single prediction to the on-disk log so every classification made
    through the app is traceable later (prediction logging / MLOps requirement)."""
    row = pd.DataFrame([{
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "text": text,
        "predicted_emotion": predicted_label,
        "confidence": confidence,
    }])
    header = not os.path.exists(LOG_PATH)
    row.to_csv(LOG_PATH, mode="a", header=header, index=False)


def log_batch_predictions(texts_series, predicted_labels_series):
    """Append a whole batch of predictions to the same log in one write."""
    batch_df = pd.DataFrame({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": "batch",
        "text": texts_series.values,
        "predicted_emotion": predicted_labels_series.values,
        "confidence": None,
    })
    header = not os.path.exists(LOG_PATH)
    batch_df.to_csv(LOG_PATH, mode="a", header=header, index=False)



@st.cache_resource
def load_artifacts():
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    labels = joblib.load(LABELS_PATH)
    return model, vectorizer, labels


try:
    model, vectorizer, labels = load_artifacts()
except Exception as e:
    st.error(
        "تعذر تحميل ملفات الموديل من مجلد saved_models/. "
        f"شغّل خلية 'تجهيز وحفظ الموديل' في النوت بوك الأول. ({e})"
    )
    st.stop()


@st.cache_resource
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None


df_app = load_data()


@st.cache_resource
def build_retrieval_index(_df):
    if _df is None or "text" not in _df.columns:
        return None, None
    vec = TfidfVectorizer()
    matrix = vec.fit_transform(_df["text"].astype(str))
    return vec, matrix


retriever_vectorizer, retriever_matrix = build_retrieval_index(df_app)

st.title("Customer Sentiment & Emotion Intelligence")
st.write("NLP system for customer emotion classification.")

st.sidebar.header("Model Information")
st.sidebar.write(f"Model: {type(model).__name__}")
st.sidebar.write("Features: TF-IDF")
st.sidebar.write("Dataset: DAIR.AI Emotion")
st.sidebar.write(f"Classes: {len(labels)}")
if os.getenv("OPENAI_API_KEY"):
    st.sidebar.success("RAG: LLM answers enabled (OPENAI_API_KEY found)")
else:
    st.sidebar.info("RAG: extractive-only fallback (no OPENAI_API_KEY set)")

tab1, tab2, tab3 = st.tabs(["\\U0001F4CA Overview", "\\U0001F50D Classify (Single & Batch)", "\\U0001F916 RAG Assistant"])

# ------------------------------------------------------------------
# Tab 1: Overview + Model/Version Log (زي التيم)
# ------------------------------------------------------------------
with tab1:
    st.header("Dataset Overview")
    if df_app is not None and "label" in df_app.columns:
        counts = df_app["label"].map(lambda i: labels[i] if i < len(labels) else i).value_counts()
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax)
        ax.set_ylabel("Count")
        ax.set_title("Emotion Distribution")
        st.pyplot(fig)
        st.dataframe(df_app.sample(min(5, len(df_app)))[["text", "label"]])
    else:
        st.info("مفيش emotion_data.csv متاح -- شغّل خلية تجهيز الموديل عشان يتحفظ.")

    st.subheader("Model / Version Log")
    version_log = pd.DataFrame({
        "Model": [type(model).__name__],
        "Feature Extraction": ["TF-IDF"],
        "Dataset": ["DAIR.AI Emotion"],
        "Number of Classes": [len(labels)],
        "Version": ["v1.0"],
        "Date": [datetime.now().strftime("%Y-%m-%d")],
    })
    st.dataframe(version_log)
    st.caption("This system is for customer emotion classification and is not a clinical mental health assessment.")

    st.subheader("Recent Predictions Log")
    if os.path.exists(LOG_PATH):
        log_df = pd.read_csv(LOG_PATH)
        st.dataframe(log_df.tail(20).iloc[::-1], use_container_width=True)
        st.caption(f"{len(log_df)} predictions logged in total (single + batch), stored at {LOG_PATH}.")
    else:
        st.info("لسه مفيش أي تصنيف اتسجل. جرّب تاب 'Classify (Single & Batch)' الأول.")

# ------------------------------------------------------------------
# Tab 2: Single text + Batch CSV (زي التيم بالظبط)
# ------------------------------------------------------------------
with tab2:
    st.header("1. Single Text Classification")
    text = st.text_area("Enter customer text:", placeholder="Example: I am really happy with the service!")
    if st.button("Predict Emotion"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            vec_text = vectorizer.transform([text])
            pred = model.predict(vec_text)[0]
            st.success(f"Predicted Emotion: {labels[pred]}")

            confidence_val = None
            if hasattr(model, "decision_function"):
                scores = model.decision_function(vec_text)[0]
                confidence_val = float(scores.max())
                score_df = pd.DataFrame({"Emotion": labels, "Score": scores})
                st.bar_chart(score_df.set_index("Emotion"))

            log_prediction(text, labels[pred], source="single", confidence=confidence_val)

    st.header("2. Batch CSV Classification")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:")
        st.dataframe(data.head())

        text_column = next(
            (c for c in data.columns if c.lower() in ["text", "review", "comment", "message"]), None
        )
        if text_column is None:
            st.error("No text column found. Please use a column named text, review, comment, or message.")
        elif st.button("Classify CSV"):
            texts = data[text_column].fillna("").astype(str)
            vectors = vectorizer.transform(texts)
            predictions = model.predict(vectors)
            data["predicted_emotion"] = [labels[p] for p in predictions]
            log_batch_predictions(texts, data["predicted_emotion"])
            st.success("Classification completed!")
            st.dataframe(data)

            csv_bytes = data.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Results CSV", data=csv_bytes,
                file_name="emotion_predictions.csv", mime="text/csv",
            )

            st.header("3. Emotion Distribution")
            emotion_counts = data["predicted_emotion"].value_counts()
            st.bar_chart(emotion_counts)
            fig, ax = plt.subplots()
            ax.pie(emotion_counts.values, labels=emotion_counts.index, autopct="%1.1f%%")
            ax.set_title("Customer Emotion Distribution")
            st.pyplot(fig)

# ------------------------------------------------------------------
# Tab 3: RAG Assistant (من القديمة، لكن المفتاح بيتقرا من .env ومفيش انهيار)
# ------------------------------------------------------------------
with tab3:
    st.header("Ask the RAG Assistant")
    st.caption("Answers are grounded in real classified examples from the dataset, not invented.")

    if retriever_vectorizer is None:
        st.warning("مفيش بيانات نصية متاحة لبناء الـ retrieval index (emotion_data.csv مش موجود).")
    else:
        question = st.text_input("Ask a question about customer emotions, e.g. 'What triggers anger?'")
        if st.button("Ask") and question.strip():
            q_vec = retriever_vectorizer.transform([question])
            similarities = cosine_similarity(q_vec, retriever_matrix).flatten()
            top_indices = similarities.argsort()[-5:][::-1]
            retrieved = df_app.iloc[top_indices]

            st.subheader("Retrieved supporting examples:")
            for _, row in retrieved.iterrows():
                label_i = row["label"]
                label_name = labels[label_i] if label_i < len(labels) else label_i
                st.write(f"- *({label_name})* {row['text']}")

            context = "\\n".join(
                f"- ({labels[row['label']] if row['label'] < len(labels) else row['label']}) {row['text']}"
                for _, row in retrieved.iterrows()
            )
            prompt = f"""Based ONLY on the following real customer examples, answer the question concisely.
Do not invent information not present in the examples.

Examples:
{context}

Question: {question}
Answer:"""

            # -- التصليح الأساسي هنا: المفتاح من .env مش مكتوب صريح، وأي فشل (مفتاح
            # مفقود / مكتبة openai مش متاحة / خطأ في الـ API) بيرجّع extractive
            # fallback بدل ما يوقع التطبيق كله. --
            api_key = os.getenv("OPENAI_API_KEY")
            answered = False
            if api_key:
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    st.subheader("Assistant's answer:")
                    st.write(response.choices[0].message.content)
                    answered = True
                except Exception as e:
                    st.warning(f"تعذر استدعاء الـ LLM ({e}) -- هيتم عرض الأمثلة المسترجعة فقط.")
            if not answered:
                st.info(
                    "LLM not configured (no OPENAI_API_KEY, or the `openai` package isn't installed) -- "
                    "showing retrieved context only (extractive fallback)."
                )