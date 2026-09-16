# Customer Sentiment & Emotion Intelligence Platform

An end-to-end NLP system that classifies customer text into 6 emotions (sadness, joy, love,
anger, fear, surprise), benchmarks 9 models spanning classical ML, deep learning and a
fine-tuned Transformer, scores texts for business priority via topic modeling, exposes the
results through a SQL analytics layer, and serves live predictions through a Streamlit
application deployed with Docker.

## Overview
- **Dataset:** [dair-ai/emotion](https://huggingface.co/datasets/dair-ai/emotion) — 16,000
  labeled texts, 6 emotion classes, imbalanced (~9:1 largest:smallest class, `surprise` being
  the rarest at 115 test examples).
- **Models compared (9 total):** TF-IDF + Logistic Regression, TF-IDF + Linear SVM (both
  hyperparameter-swept over n-gram range / vocabulary size), Embedding MLP, CNN, RNN, LSTM,
  BiLSTM, GRU, and a fine-tuned DistilBERT Transformer.
- **Best model overall:** DistilBERT (fine-tuned) — **92.63% accuracy / 89.63% Macro F1** —
  ahead of the best RNN-family model, GRU (90.84%), and the best classical baseline, tuned
  Linear SVM (89.38%).
- **Deployed model:** the Streamlit app serves the lighter **TF-IDF + Linear SVM** model
  (`saved_models/emotion_model.pkl`) rather than DistilBERT, trading a few accuracy points for
  a much smaller/faster deployment footprint. See *Key Findings* below.

## Project Structure
```
emotion-intelligence-platform/
├── app/
│   └── app.py                     # Streamlit application (Overview / Classify / RAG Assistant)
├── data/
│   ├── emotion_analysis.db        # full analytics DB (7 tables, see "SQL Analytics")
│   ├── predictions_database.db    # predictions-only subset of the DB above
│   └── logs.txt                   # Streamlit server run log
├── notebooks/
│   ├── Teck_Final_merged.ipynb            # training / analysis pipeline
│   └── Teck_Final_merged_documented.ipynb # same pipeline, with markdown documentation
├── saved_models/
│   ├── emotion_model.pkl          # trained TF-IDF + Linear SVM (LinearSVC)
│   ├── tfidf_vectorizer.pkl
│   ├── labels.pkl                 # ['sadness','joy','love','anger','fear','surprise']
│   └── emotion_data.csv           # dataset used by the app's Overview tab + RAG retriever
├── sql/
│   └── analytical_queries.sql     # 30 queries across all 7 tables (see below)
├── all_results/                   # full experiment bundle -- gitignored, documented below
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup
```bash
pip install -r requirements.txt
```

## Run the Streamlit App (locally, no Docker)
Run from the project root so the relative `saved_models/` path resolves correctly:
```bash
streamlit run app/app.py
```
The app opens at `http://localhost:8501`. The **RAG Assistant** tab works in extractive-only
mode out of the box; to enable LLM-generated answers, put `OPENAI_API_KEY=...` in a `.env`
file at the project root before launching (`.env` is gitignored, see `.env.example` if present).

## Run with Docker
```bash
docker build -t emotion-app .
docker run -p 8501:8501 emotion-app
# with the RAG LLM step enabled:
docker run -p 8501:8501 --env-file .env emotion-app
```
Then open `http://localhost:8501` in your browser.

> **Fix applied in this version:** the previous `Dockerfile` copied `app.py` from the project
> root and looked for a `saved_model/` folder (singular), but the real files live at
> `app/app.py` and `saved_models/` (plural) — so the build/run used to fail. Both the
> `Dockerfile` and the `saved_models/...` paths inside `app.py` have been corrected here to
> match the actual project layout. `requirements.txt` also now pins
> `scikit-learn==1.6.1` (the exact version the model was trained with) to avoid
> `InconsistentVersionWarning` when unpickling.

## SQL Analytics
`sql/analytical_queries.sql` now contains **30 queries** (JOINs, CTEs, window functions,
CASE-based pivots) run against `data/emotion_analysis.db`, organized in 4 sections that match
the database's 7 tables:
1. **Queries 1–9** — Topic, priority & business insights (`topic_assignments`)
2. **Queries 10–16** — Model comparison & classical hyperparameter sweep (`model_comparison`,
   `classical_sweep`)
3. **Queries 17–20** — Human review queue composition & QA checks (`human_review_queue`)
4. **Queries 21–30** — Prediction accuracy analytics — per-model accuracy, `RANK()` /
   running-average window functions, a best-model CTE, and confusion analysis
   (`predictions_texts`, `predictions_models`, `model_predictions`)

## Key Findings
- A fine-tuned Transformer (DistilBERT) beats every other approach, but by a modest margin —
  under 4 accuracy points over the best classical model — so a well-tuned TF-IDF + Linear SVM
  remains a strong, cheap baseline for this kind of short-text classification, which is why
  it's the model actually deployed in the app.
- Plain unigrams with a 5,000-word vocabulary beat every richer n-gram / larger-vocabulary
  configuration tested in the classical sweep.
- Negative emotions (fear, anger, sadness) receive noticeably higher average business-priority
  scores than positive ones, confirming the priority-scoring pipeline is directionally correct
  for a customer-support triage use case.
- BiLSTM underperformed every other deep learning model by a wide margin (67.1% vs. 85–91%)
  and should be treated as a training issue to revisit, not a reliable data point.

## Experiment Artifacts (`all_results/`, not pushed to git)
`all_results/` (and `all_results.zip`) hold every intermediate artifact from the full
experiment run — multiple model weights, embeddings and reports — and are excluded from
version control via `.gitignore` due to size. They're documented here instead:

| Folder | Contents |
|---|---|
| `classical/` | Best model + vectorizer (`.joblib`), calibrated model, calibration summary, confidence-threshold analysis, LR-vs-SVM baseline, n-gram/max_features sweep |
| `deep_learning/` | Per-model classwise report, metrics, training histories (`histories/*.json`) and weights (`weights/*.pt`) for Embedding MLP, CNN, RNN, LSTM, GRU, BiLSTM |
| `transformer/` | DistilBERT training history, metrics, classwise report, and the saved HuggingFace model (`model/config.json`, `model.safetensors`, tokenizer files) |
| `topic_modeling/` | Topic-to-word mappings, topic name mapping, emotion/topic cross-tabulations (counts & percentages) |
| `priority_scoring/` | Emotion/topic/urgency weight configs used to compute `priority_score`, plus the master topic-assignments table |
| `human_review/` | The exported 60-item curated human review queue (`human_review_queue.csv`) |
| `summary/` | `full_model_comparison.csv` — source of the `model_comparison` SQL table |
| `emotion_analysis.db` | A copy of the full analytics database bundled with the run |

Regenerate the whole folder by re-running `notebooks/Teck_Final_merged.ipynb` end to end, or
keep a copy of `all_results.zip` somewhere outside the repo (Drive/S3/etc.).

## Limitations
- Trained on a relatively small (16K), pre-cleaned, single-domain dataset (short Twitter-style
  text); results may not generalize to longer or more varied customer text (emails, tickets,
  reviews).
- The deployed classical model trades accuracy for simplicity; serving the fine-tuned
  DistilBERT model instead is a natural next step once the deployment can afford the extra
  memory/latency footprint.
- BiLSTM training should be revisited (learning rate, initialization, or early-stopping
  schedule) before drawing conclusions from its result.
- The RAG Assistant's generation step depends on an external LLM API key; without one, only
  the retrieval half of RAG is exercised.
- Rare-class metrics (`love`, `surprise`) are based on few test examples and carry high
  variance.

## Author(s)
Kirellos Nader
Fayrous Hassan
Loaa Elshatby
Karim Yunis
Mazen Eldayash
Luay Mohamed