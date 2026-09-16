"""
generate_report.py
Generates a professional PDF report for the Customer Sentiment & Emotion Intelligence Platform.
Requires: reportlab, Pillow
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Image as RLImage
)
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.colors import HexColor

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = r"d:\techtrek\final_project\emotion-intelligence-platform"
SCREENS = os.path.join(BASE, "screens")
OUTPUT  = os.path.join(BASE, "Project_Report.pdf")

SCHEMA_IMG = os.path.join(BASE, "Screenshot 2026-09-16 142851.png")
SCREEN_IMGS = [
    ("Screenshot 2026-09-16 150950.png", "App Overview – Header and emotion distribution chart (partial)"),
    ("Screenshot 2026-09-16 151043.png", "App Overview – Full emotion distribution bar chart"),
    ("Screenshot 2026-09-16 151145.png", "App Overview – Sample data table and model version log"),
    ("Screenshot 2026-09-16 151235.png", "Classify Tab – Single text input and batch CSV upload"),
    ("Screenshot 2026-09-16 151316.png", "RAG Assistant Tab – Question input interface"),
    ("Screenshot 2026-09-16 151412.png", "RAG Assistant – Retrieved supporting examples in action"),
    ("Screenshot 2026-09-16 151546.png", "Single text classification result with confidence scores"),
    ("Screenshot 2026-09-16 151650.png", "Batch CSV classification – Uploaded data preview"),
]

# ── Colors ─────────────────────────────────────────────────────────────────────
DARK_BLUE  = HexColor("#1a237e")
MID_BLUE   = HexColor("#1976d2")
LIGHT_BLUE = HexColor("#e3f2fd")
ACCENT     = HexColor("#0d47a1")
ROW_ALT    = HexColor("#f5f8ff")
WHITE      = colors.white
BLACK      = colors.black
GRAY_LINE  = HexColor("#b0bec5")
GRAY_TEXT  = HexColor("#455a64")
ROW_HEADER = HexColor("#1565c0")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

# ── Page number canvas callback ────────────────────────────────────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_TEXT)
    page_num = canvas.getPageNumber()
    text = f"Customer Sentiment & Emotion Intelligence Platform  |  Page {page_num}"
    canvas.drawCentredString(PAGE_W / 2, 1.2 * cm, text)
    # Footer line
    canvas.setStrokeColor(GRAY_LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.6 * cm, PAGE_W - MARGIN, 1.6 * cm)
    canvas.restoreState()


# ── Style helpers ──────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=32,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        fontName="Helvetica",
        fontSize=13,
        textColor=HexColor("#bbdefb"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    authors_style = ParagraphStyle(
        "Authors",
        fontName="Helvetica",
        fontSize=11,
        textColor=HexColor("#e3f2fd"),
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    h1_style = ParagraphStyle(
        "H1",
        fontName="Helvetica-Bold",
        fontSize=15,
        textColor=WHITE,
        spaceBefore=14,
        spaceAfter=6,
        leading=20,
        leftIndent=0,
    )
    h2_style = ParagraphStyle(
        "H2",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=DARK_BLUE,
        spaceBefore=10,
        spaceAfter=4,
    )
    h3_style = ParagraphStyle(
        "H3",
        fontName="Helvetica-BoldOblique",
        fontSize=10.5,
        textColor=MID_BLUE,
        spaceBefore=8,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=HexColor("#212121"),
        alignment=TA_JUSTIFY,
        spaceBefore=2,
        spaceAfter=4,
        leading=14,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=HexColor("#212121"),
        leftIndent=14,
        spaceBefore=1,
        spaceAfter=2,
        leading=13,
        bulletIndent=4,
    )
    caption_style = ParagraphStyle(
        "Caption",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        textColor=GRAY_TEXT,
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=8,
    )
    code_style = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=8,
        textColor=HexColor("#263238"),
        backColor=HexColor("#eceff1"),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=4,
        spaceAfter=4,
        leading=12,
        borderPadding=(4, 4, 4, 4),
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "authors": authors_style,
        "h1": h1_style,
        "h2": h2_style,
        "h3": h3_style,
        "body": body_style,
        "bullet": bullet_style,
        "caption": caption_style,
        "code": code_style,
    }


# ── Table factory ──────────────────────────────────────────────────────────────
def make_table(header_row, data_rows, col_widths=None, font_size=8.5):
    all_rows = [header_row] + data_rows
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0), ROW_HEADER),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), font_size),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, ROW_ALT]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), font_size),
        ("ALIGN",         (1, 1), (-1, -1), "CENTER"),
        ("ALIGN",         (0, 1), (0, -1),  "LEFT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


# ── Section header box ─────────────────────────────────────────────────────────
def section_header(title, styles):
    """Returns a styled blue-background paragraph acting as a section header."""
    tbl = Table(
        [[Paragraph(title, styles["h1"])]],
        colWidths=[PAGE_W - 2 * MARGIN],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), [4, 4, 4, 4]),
    ]))
    return tbl


def add_image(path, width=None, caption=None, styles=None):
    """Returns a list of flowables: [image, caption] or empty on error."""
    elems = []
    if not os.path.exists(path):
        return elems
    try:
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            w_px, h_px = im.size
        avail = PAGE_W - 2 * MARGIN
        img_w = width if width else min(avail, 14 * cm)
        ratio = h_px / w_px
        img_h = img_w * ratio
        # Never taller than 10cm
        if img_h > 10 * cm:
            img_h = 10 * cm
            img_w = img_h / ratio
        img = RLImage(path, width=img_w, height=img_h)
        elems.append(img)
        if caption and styles:
            elems.append(Paragraph(caption, styles["caption"]))
    except Exception as e:
        print(f"  [WARN] Could not load image {path}: {e}")
    return elems


# ── Build story ────────────────────────────────────────────────────────────────
def build_story(styles):
    story = []
    S = styles
    B = S["body"]
    BU = S["bullet"]

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE PAGE
    # ──────────────────────────────────────────────────────────────────────────
    avail_w = PAGE_W - 2 * MARGIN

    repo_style = ParagraphStyle(
        "Repo",
        fontName="Helvetica",
        fontSize=10,
        textColor=HexColor("#90caf9"),
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    title_block = Table(
        [
            [Paragraph("Customer Sentiment &amp; Emotion", S["title"])],
            [Paragraph("Intelligence Platform", S["title"])],
            [Spacer(1, 0.3 * cm)],
            [Paragraph("End-to-End NLP System for Emotion Classification,<br/>Business Priority Scoring, and Live Prediction Serving", S["subtitle"])],
            [Spacer(1, 0.6 * cm)],
            [HRFlowable(width=avail_w * 0.6, thickness=1, color=HexColor("#90caf9"), spaceAfter=12)],
            [Spacer(1, 0.3 * cm)],
            [Paragraph("<b>Authors</b>", S["authors"])],
            [Paragraph("Kirellos Nader &nbsp;·&nbsp; Fayrous Hassan &nbsp;·&nbsp; Loaa Elshatby", S["authors"])],
            [Paragraph("Karim Yunis &nbsp;·&nbsp; Mazen Eldayash &nbsp;·&nbsp; Luay Mohamed", S["authors"])],
            [Spacer(1, 0.4 * cm)],
            [Paragraph("September 2026", S["authors"])],
            [Spacer(1, 0.4 * cm)],
            [Paragraph("TechTrek Final Project", S["authors"])],
            [Spacer(1, 0.5 * cm)],
            [HRFlowable(width=avail_w * 0.4, thickness=0.5, color=HexColor("#90caf9"), spaceAfter=8)],
            [Spacer(1, 0.1 * cm)],
            [Paragraph("GitHub Repository", repo_style)],
            [Paragraph("github.com/KirellosNader/emotion-intelligence-platform", repo_style)],
        ],
        colWidths=[avail_w],
    )
    title_block.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),
    ]))

    story.append(Spacer(1, 2.5 * cm))
    story.append(title_block)
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 1 – PROJECT OVERVIEW
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 1 – Project Overview", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The Customer Sentiment &amp; Emotion Intelligence Platform is a comprehensive, end-to-end "
        "Natural Language Processing (NLP) system designed to classify short customer texts into six "
        "distinct emotional categories. Beyond classification, the platform integrates topic modeling "
        "for business triage, a SQL-based analytics layer, and a live Streamlit web application "
        "deployable via Docker.",
        B,
    ))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("<b>System Components:</b>", S["h2"]))
    components = [
        "Emotion Classification: 6-class text classifier (sadness, joy, love, anger, fear, surprise)",
        "Model Benchmarking: 9 models compared – Classical ML, Deep Learning, and fine-tuned Transformer",
        "Topic Modeling: LDA per emotion (3 topics each) for nuanced customer intent analysis",
        "Priority Scoring: Rule-based business priority engine using emotion weights and urgency keywords",
        "SQL Analytics Layer: 30 analytical queries across 7 database tables",
        "Streamlit Application: 3-tab interactive web app (Overview / Classify / RAG Assistant)",
        "Docker Deployment: Containerized for reproducible, portable deployment",
    ]
    for c in components:
        story.append(Paragraph(f"• {c}", BU))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("<b>Dataset:</b>", S["h2"]))
    story.append(Paragraph(
        "The project uses the <b>dair-ai/emotion</b> dataset from Hugging Face Hub — 16,000 labeled "
        "short texts across 6 emotion classes. The dataset is imbalanced with a ~9:1 ratio between "
        "the largest and smallest classes. <i>Joy</i> is the most frequent class (~5,360 samples) "
        "while <i>surprise</i> is the rarest, with only 115 test examples, making minority-class "
        "metrics particularly sensitive to variance.",
        B,
    ))
    story.append(Spacer(1, 0.15 * cm))

    dist_header = ["Emotion", "Train", "Validation", "Test", "Proportion"]
    dist_data = [
        ["joy",      "~5,360", "~696", "~1,072", "Largest (~33%)"],
        ["sadness",  "~4,666", "~606", "~933",   "2nd (~29%)"],
        ["anger",    "~2,159", "~280", "~432",   "3rd (~13%)"],
        ["fear",     "~1,937", "~251", "~387",   "4th (~12%)"],
        ["love",     "~1,304", "~169", "~261",   "5th (~8%)"],
        ["surprise", "~573",   "~74",  "~115",   "Rarest (~4%)"],
    ]
    story.append(make_table(dist_header, dist_data,
                            col_widths=[3.2*cm, 2.5*cm, 2.5*cm, 2.2*cm, 4.0*cm]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Table 1.1 – Approximate emotion class distribution across dataset splits.",
        S["caption"],
    ))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 2 – SYSTEM ARCHITECTURE
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 2 – System Architecture &amp; Project Structure", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The project follows a clean separation of concerns, with dedicated directories for the "
        "application, data, notebooks, trained model artifacts, SQL queries, and experiment results.",
        B,
    ))
    story.append(Spacer(1, 0.1 * cm))
    repo_link_style = ParagraphStyle(
        "RepoLink",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        textColor=MID_BLUE,
        spaceBefore=2,
        spaceAfter=4,
    )
    story.append(Paragraph(
        "GitHub Repository: "
        "<u><a href='https://github.com/KirellosNader/emotion-intelligence-platform' color='#1976d2'>"
        "https://github.com/KirellosNader/emotion-intelligence-platform</a></u>",
        repo_link_style,
    ))
    story.append(Spacer(1, 0.15 * cm))

    folder_lines = [
        "emotion-intelligence-platform/",
        "├── app/",
        "│   └── app.py                     # Streamlit application (Overview / Classify / RAG Assistant)",
        "├── data/",
        "│   ├── emotion_analysis.db        # Full analytics DB (7 tables)",
        "│   ├── predictions_database.db    # Predictions-only subset of the DB",
        "│   └── logs.txt                   # Streamlit server run log",
        "├── notebooks/",
        "│   ├── Teck_Final_merged.ipynb            # Training & analysis pipeline",
        "│   └── Teck_Final_merged_documented.ipynb # Same pipeline with full documentation",
        "├── saved_models/",
        "│   ├── emotion_model.pkl          # Trained TF-IDF + Linear SVM (LinearSVC)",
        "│   ├── tfidf_vectorizer.pkl       # Fitted TF-IDF vectorizer",
        "│   ├── labels.pkl                 # ['sadness','joy','love','anger','fear','surprise']",
        "│   └── emotion_data.csv           # Dataset used by Overview tab & RAG retriever",
        "├── sql/",
        "│   └── analytical_queries.sql     # 30 queries across 7 tables",
        "├── all_results/                   # Full experiment bundle (gitignored – see Section 11)",
        "├── screens/                       # Application screenshots",
        "├── Dockerfile                     # Docker build configuration",
        "├── requirements.txt               # Python dependencies",
        "└── README.md                      # Project documentation",
    ]
    folder_text = "<br/>".join(folder_lines)
    folder_para = Paragraph(folder_text, S["code"])
    story.append(folder_para)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("<b>Technology Stack:</b>", S["h2"]))
    tech_header = ["Layer", "Technology", "Purpose"]
    tech_data = [
        ["ML / NLP", "scikit-learn, PyTorch, HuggingFace", "Model training and inference"],
        ["Feature Extraction", "TF-IDF (scikit-learn)", "Classical model features"],
        ["Transformer", "DistilBERT (HuggingFace Transformers)", "State-of-art fine-tuned model"],
        ["Topic Modeling", "Gensim LDA", "Per-emotion topic extraction"],
        ["Database", "SQLite3", "Analytics database (7 tables)"],
        ["Web App", "Streamlit", "Interactive prediction interface"],
        ["Deployment", "Docker (port 8501)", "Containerized production serving"],
        ["RAG", "TF-IDF cosine retrieval + OpenAI API", "Grounded question answering"],
    ]
    story.append(make_table(tech_header, tech_data,
                            col_widths=[3.5*cm, 5.5*cm, 5.4*cm]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph("Table 2.1 – Technology stack by layer.", S["caption"]))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 3 – DATABASE SCHEMA
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 3 – Database Schema", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The analytics database (<b>emotion_analysis.db</b>) is a SQLite database with 7 tables "
        "organized into two logical groups: the <i>topic &amp; priority</i> group and the "
        "<i>predictions &amp; model benchmarking</i> group. The entity-relationship diagram below "
        "illustrates the table structures and foreign-key relationships.",
        B,
    ))
    story.append(Spacer(1, 0.3 * cm))

    story += add_image(SCHEMA_IMG, width=13 * cm,
                       caption="Figure 3.1 – Database schema for emotion_analysis.db (7 tables)",
                       styles=S)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>Table Descriptions:</b>", S["h2"]))

    tables_info = [
        ["Table", "Key Columns", "Description"],
        ["TOPIC_ASSIGNMENTS", "index, emotion, topic, topic_name, emotion_score, topic_score, text, business_score, priority_score, priority_level",
         "Main triage table. Every customer text is enriched with its LDA topic, emotion-based weights, urgency score, and final priority level."],
        ["MODEL_COMPARISON", "Model, Model_Type, Features, Accuracy, Macro_F1, Weighted_F1, ...",
         "Aggregated benchmark metrics for all 9 models. Used for summary analysis."],
        ["CLASSICAL_SWEEP", "N_gram, Max_Features, Model, Accuracy, Macro_F1, ...",
         "Grid-search results for classical TF-IDF models across n-gram ranges and vocabulary sizes."],
        ["HUMAN_REVIEW_QUEUE", "index, emotion, topic_name, text, priority_score, priority_level",
         "60 curated edge-case texts flagged for quality assurance / human review."],
        ["PREDICTIONS_TEXTS", "text_id (PK), text, true_label",
         "Ground-truth texts and labels used for per-model prediction accuracy analysis."],
        ["PREDICTIONS_MODELS", "model_id (PK), model_name",
         "Lookup table enumerating all 9 benchmarked models."],
        ["MODEL_PREDICTIONS", "text_id (FK), model_id (FK), predicted_label",
         "Bridge table: each row records a single model's predicted label for a single text."],
    ]
    t = Table(tables_info, colWidths=[3.5*cm, 5.0*cm, 5.9*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ROW_HEADER),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, ROW_ALT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph("Table 3.1 – Database table descriptions.", S["caption"]))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 4 – MODELS & EXPERIMENTS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 4 – Models &amp; Experiments", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The project benchmarks <b>9 models</b> across three families: Classical ML (TF-IDF-based), "
        "Deep Learning (embedding-based neural networks), and a Transformer (fine-tuned DistilBERT). "
        "All models are evaluated on the same held-out test set of 3,200 examples.",
        B,
    ))

    # 4.1 Classical
    story.append(Paragraph("4.1  Classical ML Models (TF-IDF-Based)", S["h2"]))
    story.append(Paragraph(
        "Three classical models were evaluated as baselines: Logistic Regression, Linear SVM "
        "(LinearSVC), and Multinomial Naive Bayes, all using TF-IDF features. A hyperparameter "
        "sweep over n-gram range and vocabulary size was then conducted to find the best classical configuration.",
        B,
    ))

    story.append(Paragraph("<b>Baseline Comparison:</b>", S["h3"]))
    cls_base_h = ["Model", "Accuracy", "Macro F1"]
    cls_base_d = [
        ["TF-IDF + Logistic Regression",     "87.44%", "84.79%"],
        ["TF-IDF + Linear SVM (LinearSVC)",  "88.94%", "86.19%"],
        ["TF-IDF + Multinomial Naive Bayes", "62.72%", "33.36%"],
    ]
    story.append(make_table(cls_base_h, cls_base_d, col_widths=[8.5*cm, 3.0*cm, 2.9*cm]))
    story.append(Paragraph("Table 4.1 – Classical baseline comparison.", S["caption"]))

    story.append(Paragraph(
        "<b>Best configuration after sweep:</b> Unigram (1,1) range, max_features=5,000. "
        "This surprisingly simple configuration outperformed all richer n-gram / larger-vocabulary "
        "alternatives, confirming that short emotional texts are well-captured by individual word features.",
        B,
    ))

    story.append(Paragraph("<b>Best Classical Model – Per-Class Performance:</b>", S["h3"]))
    cls_cw_h = ["Emotion", "Precision", "Recall", "F1-Score", "Support"]
    cls_cw_d = [
        ["sadness",  "94.03%", "91.10%", "92.54%", "933"],
        ["joy",      "92.79%", "90.02%", "91.38%", "1,072"],
        ["love",     "75.84%", "86.59%", "80.86%", "261"],
        ["anger",    "87.61%", "90.05%", "88.81%", "432"],
        ["fear",     "85.45%", "85.01%", "85.23%", "387"],
        ["surprise", "77.52%", "86.96%", "81.97%", "115"],
    ]
    story.append(make_table(cls_cw_h, cls_cw_d,
                            col_widths=[3.2*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.5*cm]))
    story.append(Paragraph(
        "Table 4.2 – Best classical model (TF-IDF + LinearSVC, unigram 5k) – per-class report.",
        S["caption"],
    ))

    story.append(Paragraph("<b>Calibration Metrics (Calibrated SVM):</b>", S["h3"]))
    cal_h = ["Metric", "Value"]
    cal_d = [
        ["Multiclass Brier Score", "0.1544"],
        ["Log Loss",               "0.3054"],
        ["Top-label ECE",          "0.0585"],
    ]
    story.append(make_table(cal_h, cal_d, col_widths=[8.0*cm, 6.4*cm]))
    story.append(Paragraph("Table 4.3 – Probability calibration metrics for the CalibratedClassifierCV wrapper.", S["caption"]))

    story.append(Paragraph("<b>Confidence Threshold Analysis:</b>", S["h3"]))
    story.append(Paragraph(
        "By applying a confidence threshold, low-certainty predictions can be deferred for human review, "
        "trading coverage for precision. The table below shows selected operating points:",
        B,
    ))
    thr_h = ["Threshold", "Coverage", "Accuracy (Accepted)", "Macro F1 (Accepted)"]
    thr_d = [
        ["0.30", "99.91%", "89.40%", "86.16%"],
        ["0.50", "96.34%", "90.95%", "88.19%"],
        ["0.60", "87.94%", "93.96%", "91.15%"],
        ["0.70", "80.09%", "96.49%", "94.94%"],
        ["0.80", "69.22%", "98.37%", "97.62%"],
        ["0.90", "49.09%", "99.43%", "98.97%"],
    ]
    story.append(make_table(thr_h, thr_d, col_widths=[3.0*cm, 3.2*cm, 3.8*cm, 4.0*cm]))
    story.append(Paragraph("Table 4.4 – Confidence threshold analysis for the calibrated SVM.", S["caption"]))

    story.append(PageBreak())

    # 4.2 Deep Learning
    story.append(Paragraph("4.2  Deep Learning Models", S["h2"]))
    story.append(Paragraph(
        "Six embedding-based neural network architectures were trained and evaluated: "
        "Embedding MLP, CNN, RNN, LSTM, GRU, and BiLSTM. All models use fixed-dimensional "
        "word embeddings as input. GRU achieved the best performance among the DL family.",
        B,
    ))

    dl_h = ["Model", "Accuracy", "Macro Precision", "Macro Recall", "Macro F1", "Weighted F1"]
    dl_d = [
        ["GRU",           "90.97%", "85.63%", "91.59%", "87.95%", "91.19%"],
        ["LSTM",          "90.34%", "85.07%", "91.51%", "87.59%", "90.60%"],
        ["RNN",           "86.59%", "81.56%", "88.88%", "84.35%", "86.78%"],
        ["CNN",           "84.97%", "81.16%", "85.17%", "82.85%", "84.98%"],
        ["Embedding MLP", "84.38%", "78.83%", "82.55%", "80.38%", "84.60%"],
        ["BiLSTM",        "80.69%", "76.86%", "83.36%", "79.37%", "80.86%"],
    ]
    story.append(make_table(dl_h, dl_d,
                            col_widths=[3.2*cm, 2.2*cm, 2.8*cm, 2.5*cm, 2.5*cm, 2.5*cm],
                            font_size=8))
    story.append(Paragraph("Table 4.5 – Deep learning model comparison.", S["caption"]))

    story.append(Paragraph(
        "<b>Note on BiLSTM:</b> BiLSTM underperformed every other deep learning model by a wide "
        "margin (80.69% vs. 85–91%). This is likely a training issue (learning rate, initialization, "
        "or early-stopping schedule) rather than an architectural limitation, and should be revisited.",
        B,
    ))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("<b>Best DL Model (GRU) – Per-Class Performance:</b>", S["h3"]))
    dl_cw_h = ["Emotion", "Precision", "Recall", "F1-Score", "Support"]
    dl_cw_d = [
        ["sadness",  "96.21%", "95.18%", "95.69%", "933"],
        ["joy",      "96.88%", "87.03%", "91.70%", "1,072"],
        ["love",     "71.55%", "95.40%", "81.77%", "261"],
        ["anger",    "92.59%", "92.59%", "92.59%", "432"],
        ["fear",     "88.83%", "86.30%", "87.55%", "387"],
        ["surprise", "67.72%", "93.04%", "78.39%", "115"],
    ]
    story.append(make_table(dl_cw_h, dl_cw_d,
                            col_widths=[3.2*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.5*cm]))
    story.append(Paragraph("Table 4.6 – GRU model per-class classification report.", S["caption"]))

    story.append(PageBreak())

    # 4.3 Transformer
    story.append(Paragraph("4.3  Transformer Model – DistilBERT (Fine-Tuned)", S["h2"]))
    story.append(Paragraph(
        "A pre-trained DistilBERT model was fine-tuned on the training split of the emotion dataset. "
        "DistilBERT is a distilled version of BERT, retaining ~97% of its language understanding "
        "capability while being 40% smaller and 60% faster. Fine-tuning adapts the model to the "
        "emotion classification task and achieves the best overall performance of all 9 models.",
        B,
    ))

    bert_h = ["Metric", "Value"]
    bert_d = [
        ["Accuracy",           "92.72%"],
        ["Macro Precision",    "87.81%"],
        ["Weighted Precision", "93.59%"],
        ["Macro Recall",       "93.76%"],
        ["Weighted Recall",    "92.72%"],
        ["Macro F1",           "90.21%"],
        ["Weighted F1",        "92.91%"],
    ]
    story.append(make_table(bert_h, bert_d, col_widths=[8.0*cm, 6.4*cm]))
    story.append(Paragraph("Table 4.7 – DistilBERT overall performance metrics.", S["caption"]))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("<b>DistilBERT Per-Class Performance:</b>", S["h3"]))
    bert_cw_h = ["Emotion", "Precision", "Recall", "F1-Score", "Support"]
    bert_cw_d = [
        ["sadness",  "97.79%", "95.07%", "96.41%", "933"],
        ["joy",      "98.07%", "90.21%", "93.97%", "1,072"],
        ["love",     "74.70%", "96.17%", "84.09%", "261"],
        ["anger",    "94.54%", "92.13%", "93.32%", "432"],
        ["fear",     "88.86%", "90.70%", "89.77%", "387"],
        ["surprise", "72.90%", "98.26%", "83.70%", "115"],
    ]
    story.append(make_table(bert_cw_h, bert_cw_d,
                            col_widths=[3.2*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.5*cm]))
    story.append(Paragraph("Table 4.8 – DistilBERT per-class classification report.", S["caption"]))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 5 – FULL MODEL COMPARISON
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 5 – Full Model Comparison", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The table below ranks all 9 benchmarked models by Macro F1 score — the primary metric, "
        "chosen because it is sensitive to class imbalance and reflects performance on minority classes "
        "(particularly <i>surprise</i> and <i>love</i>).",
        B,
    ))
    story.append(Spacer(1, 0.2 * cm))

    cmp_h = ["Rank", "Model", "Type", "Accuracy", "Macro F1", "Weighted F1"]
    cmp_d = [
        ["1", "DistilBERT (fine-tuned)",            "Transformer",  "92.72%", "90.21%", "92.91%"],
        ["2", "GRU",                                "Deep Learning","90.97%", "87.95%", "91.19%"],
        ["3", "LSTM",                               "Deep Learning","90.34%", "87.59%", "90.60%"],
        ["4", "TF-IDF + Linear SVM (tuned)",        "Classical",    "89.34%", "86.80%", "89.43%"],
        ["5", "TF-IDF + Logistic Regression (tuned)","Classical",   "87.84%", "85.29%", "88.04%"],
        ["6", "RNN",                                "Deep Learning","86.59%", "84.35%", "86.78%"],
        ["7", "CNN",                                "Deep Learning","84.97%", "82.85%", "84.98%"],
        ["8", "Embedding MLP",                      "Deep Learning","84.38%", "80.38%", "84.60%"],
        ["9", "BiLSTM",                             "Deep Learning","80.69%", "79.37%", "80.86%"],
    ]
    story.append(make_table(cmp_h, cmp_d,
                            col_widths=[1.1*cm, 5.0*cm, 2.8*cm, 2.2*cm, 2.2*cm, 2.5*cm],
                            font_size=8.5))
    story.append(Paragraph("Table 5.1 – Full model comparison ranked by Macro F1.", S["caption"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("<b>Key Observations:</b>", S["h2"]))
    obs = [
        "DistilBERT leads overall with 92.72% accuracy and 90.21% Macro F1.",
        "GRU is the best non-transformer model at 90.97% accuracy — within 1.75 points of DistilBERT.",
        "The best classical model (TF-IDF + LinearSVC, tuned) reaches 89.34% — only ~3.4 points below DistilBERT.",
        "The gap between DistilBERT and the best classical model is modest, justifying the choice to deploy LinearSVC for its much smaller footprint.",
        "BiLSTM (80.69%) significantly underperforms other deep learning models and warrants further investigation.",
        "Minority classes (love, surprise) show lower precision across all models, reflecting the class imbalance challenge.",
    ]
    for o in obs:
        story.append(Paragraph(f"• {o}", BU))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 6 – TOPIC MODELING
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 6 – Topic Modeling", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "Latent Dirichlet Allocation (LDA) topic modeling was applied <b>per emotion</b>, with "
        "<b>3 topics per emotion</b> (18 topics total). This enables deeper insight into the sub-themes "
        "within each emotion class — for example, distinguishing between different types of sadness or anger — "
        "which is critical for customer-support triage use cases.",
        B,
    ))
    story.append(Spacer(1, 0.2 * cm))

    tm_h = ["Emotion", "Topic 1", "Topic 2", "Topic 3"]
    tm_d = [
        ["Sadness",  "Loss & Daily Sadness",              "Worthlessness & Guilt",              "Self-Blame & Misery"],
        ["Joy",      "Happiness & Gratitude",             "Positive Achievement & Social Conn.", "Contentment & Satisfaction"],
        ["Love",     "Affection & Caring",                "Emotional Attachment & Nostalgia",   "Playful & Romantic Affection"],
        ["Anger",    "Irritation & Anger",                "Conflict & Resentment",              "Intense Anger & Frustration"],
        ["Fear",     "Nervousness & Fear",                "Insecurity & Vulnerability",         "Anxiety & Paranoia"],
        ["Surprise", "Amazement & Unexpected Experiences","Curiosity & Exploration",            "Strangeness & Amazement"],
    ]
    story.append(make_table(tm_h, tm_d,
                            col_widths=[2.0*cm, 4.3*cm, 4.3*cm, 3.8*cm],
                            font_size=8.5))
    story.append(Paragraph("Table 6.1 – LDA topics per emotion class.", S["caption"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Each customer text is assigned to one of its emotion's three topics based on the highest "
        "LDA score. The resulting <b>topic assignment</b> is stored in the <i>TOPIC_ASSIGNMENTS</i> "
        "database table and feeds directly into the priority scoring pipeline (Section 7).",
        B,
    ))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 7 – PRIORITY SCORING
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 7 – Priority Scoring System", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The priority scoring system translates emotion classifications and topic assignments into "
        "actionable business priority levels (<b>High / Medium / Low</b>) for customer-support triage. "
        "The score is computed as a weighted combination of an emotion weight, a topic weight, and "
        "a binary urgency keyword boost.",
        B,
    ))

    story.append(Paragraph("<b>Emotion Weights:</b>", S["h2"]))
    ew_h = ["Emotion", "Weight", "Rationale"]
    ew_d = [
        ["anger",    "90", "Highest priority — strong signal of dissatisfaction"],
        ["fear",     "85", "High priority — indicates distress or urgent concern"],
        ["sadness",  "80", "High priority — signals unresolved customer pain"],
        ["surprise", "50", "Medium priority — ambiguous; may be positive or negative"],
        ["love",     "30", "Low priority — satisfied customer, no immediate action needed"],
        ["joy",      "20", "Lowest priority — positive sentiment, routine follow-up"],
    ]
    story.append(make_table(ew_h, ew_d, col_widths=[2.5*cm, 2.0*cm, 9.9*cm]))
    story.append(Paragraph("Table 7.1 – Emotion weights for priority scoring.", S["caption"]))

    story.append(Paragraph("<b>Urgency Keywords:</b>", S["h2"]))
    story.append(Paragraph(
        "When any of the following keywords appear in the customer text, the business score is "
        "automatically set to <b>100</b> (maximum urgency), overriding the topic weight:",
        B,
    ))
    story.append(Paragraph(
        "urgent &nbsp;·&nbsp; immediately &nbsp;·&nbsp; asap &nbsp;·&nbsp; "
        "critical &nbsp;·&nbsp; emergency &nbsp;·&nbsp; serious",
        ParagraphStyle("keywords", parent=S["body"], alignment=TA_CENTER,
                       fontSize=10, fontName="Helvetica-Bold", textColor=MID_BLUE),
    ))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("<b>Priority Level Thresholds:</b>", S["h2"]))
    pl_h = ["Priority Level", "Score Range", "Action"]
    pl_d = [
        ["High",   "≥ 70",  "Immediate agent escalation"],
        ["Medium", "40–69", "Standard queue, respond within SLA"],
        ["Low",    "< 40",  "Automated reply or low-priority queue"],
    ]
    story.append(make_table(pl_h, pl_d, col_widths=[3.5*cm, 3.0*cm, 7.9*cm]))
    story.append(Paragraph("Table 7.2 – Priority level thresholds and recommended actions.", S["caption"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "<b>Key Finding:</b> Negative emotions (anger, fear, sadness) consistently receive the "
        "highest average business priority scores, confirming that the priority pipeline is "
        "directionally correct for a customer-support triage use case.",
        B,
    ))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 8 – HUMAN REVIEW QUEUE
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 8 – Human Review Queue", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "As part of the quality assurance pipeline, a <b>60-item Human Review Queue</b> was curated "
        "from the dataset. This queue contains edge-case and borderline predictions that warrant "
        "manual inspection by a domain expert before being acted upon.",
        B,
    ))
    story.append(Spacer(1, 0.15 * cm))

    hr_h = ["Property", "Details"]
    hr_d = [
        ["Queue Size",       "60 items"],
        ["File Location",    "all_results/human_review/human_review_queue.csv"],
        ["Selection Criteria","Borderline predictions, low-confidence cases, minority-class texts"],
        ["Schema",           "Same as TOPIC_ASSIGNMENTS (emotion, topic_name, text, priority_score, priority_level)"],
        ["DB Table",         "HUMAN_REVIEW_QUEUE (curated subset of TOPIC_ASSIGNMENTS)"],
        ["Purpose",          "Manual QA, model validation, edge-case analysis"],
    ]
    story.append(make_table(hr_h, hr_d, col_widths=[3.8*cm, 10.6*cm]))
    story.append(Paragraph("Table 8.1 – Human review queue properties.", S["caption"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "The human review queue enables a hybrid AI + human workflow: the model handles the bulk of "
        "predictions automatically, while uncertain or high-stakes cases are routed to human agents. "
        "This approach is particularly important for the <i>love</i> and <i>surprise</i> classes, "
        "which have the fewest test examples and highest prediction variance.",
        B,
    ))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 9 – SQL ANALYTICS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 9 – SQL Analytics Layer", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The file <b>sql/analytical_queries.sql</b> contains <b>30 SQL queries</b> organized into "
        "4 thematic sections. All queries target the <i>emotion_analysis.db</i> SQLite database and "
        "demonstrate a range of SQL techniques from simple aggregations to advanced window functions.",
        B,
    ))
    story.append(Spacer(1, 0.2 * cm))

    sql_h = ["Section", "Query Range", "Tables Used", "Focus Area"]
    sql_d = [
        ["Topic & Business", "Q1–Q9",   "topic_assignments",                              "Priority queue, emotion/topic distributions, urgency hit rates"],
        ["Model Benchmarks", "Q10–Q16", "model_comparison, classical_sweep",              "Best models, average metrics by type, hyperparameter sweep analysis"],
        ["Human Review",     "Q17–Q20", "human_review_queue, topic_assignments",          "Queue breakdown, missed-urgent items, business score by priority level"],
        ["Prediction Analytics","Q21–Q30","predictions_texts, predictions_models, model_predictions","Per-model accuracy, ranking, confusion analysis, minority-class error rates"],
    ]
    story.append(make_table(sql_h, sql_d,
                            col_widths=[2.5*cm, 2.2*cm, 4.5*cm, 5.2*cm],
                            font_size=8))
    story.append(Paragraph("Table 9.1 – SQL query sections overview.", S["caption"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("<b>Advanced SQL Techniques Demonstrated:</b>", S["h2"]))
    sql_techniques = [
        "<b>Multi-table JOINs:</b> Queries 21–30 JOIN across model_predictions, predictions_texts, and predictions_models (3-way join) to compute per-model accuracy.",
        "<b>CTE (Common Table Expressions):</b> Query 23 uses a CTE (WITH model_accuracy AS ...) to cleanly isolate the best model selection logic.",
        "<b>RANK() Window Function:</b> Query 22 ranks all models by accuracy using RANK() OVER (ORDER BY accuracy DESC).",
        "<b>Running Average:</b> Query 29 computes a cumulative running average of accuracy using AVG() OVER (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW).",
        "<b>PARTITION BY:</b> Query 30 uses RANK() OVER (PARTITION BY true_label ORDER BY ...) to find the best model for each emotion class independently.",
        "<b>CASE-based pivot:</b> Accuracy is computed as AVG(CASE WHEN predicted_label = true_label THEN 1.0 ELSE 0.0 END), a standard SQL accuracy pattern.",
        "<b>Subqueries:</b> Query 27 uses a nested subquery to identify the rarest class before computing per-model error rates on that class.",
    ]
    for t in sql_techniques:
        story.append(Paragraph(f"• {t}", BU))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("<b>Sample Query (Q22 – Model Ranking with RANK()):</b>", S["h3"]))
    sql_sample = (
        "SELECT model_name, accuracy,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;RANK() OVER (ORDER BY accuracy DESC) AS rank<br/>"
        "FROM (<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;SELECT pm.model_name,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END) AS accuracy<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;FROM model_predictions mp<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;JOIN predictions_texts pt ON mp.text_id = pt.text_id<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;JOIN predictions_models pm ON mp.model_id = pm.model_id<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GROUP BY pm.model_name<br/>"
        ");"
    )
    story.append(Paragraph(sql_sample, S["code"]))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 10 – STREAMLIT APPLICATION
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 10 – Streamlit Application", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The Streamlit application serves live emotion predictions via a clean three-tab web interface, "
        "accessible at <b>http://localhost:8501</b>. The deployed model is the TF-IDF + LinearSVC, "
        "chosen for its lightweight footprint over DistilBERT while still achieving strong performance.",
        B,
    ))

    story.append(Paragraph("<b>Deployment:</b>", S["h2"]))
    dep_h = ["Property", "Value"]
    dep_d = [
        ["Deployed Model",  "TF-IDF + LinearSVC (emotion_model.pkl)"],
        ["Framework",       "Streamlit"],
        ["Container",       "Docker (dockerfile at project root)"],
        ["Port",            "8501"],
        ["Run Command",     "streamlit run app/app.py  OR  docker run -p 8501:8501 emotion-app"],
        ["RAG Generation",  "Enabled when OPENAI_API_KEY is set in .env; extractive fallback otherwise"],
    ]
    story.append(make_table(dep_h, dep_d, col_widths=[3.5*cm, 10.9*cm]))
    story.append(Paragraph("Table 10.1 – Application deployment properties.", S["caption"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>Application Tabs:</b>", S["h2"]))

    # Tab 1
    story.append(Paragraph("Tab 1 – Overview", S["h3"]))
    story.append(Paragraph(
        "Displays a bar chart of the emotion class distribution in the training dataset, "
        "a sample of 5 random texts with their labels, the model version log (model name, "
        "feature extraction, dataset, version, date), and a live scrolling log of recent "
        "predictions made through the app.",
        B,
    ))
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 150950.png"),
        caption="Figure 10.1 – Overview tab: App header and emotion distribution chart (partial view)",
        styles=S,
    )
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151043.png"),
        caption="Figure 10.2 – Overview tab: Full emotion distribution bar chart",
        styles=S,
    )
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151145.png"),
        caption="Figure 10.3 – Overview tab: Sample data table and model version log",
        styles=S,
    )

    story.append(Spacer(1, 0.15 * cm))
    # Tab 2
    story.append(Paragraph("Tab 2 – Classify (Single &amp; Batch)", S["h3"]))
    story.append(Paragraph(
        "Provides two classification modes: (1) <b>Single Text Classification</b> — enter any "
        "customer text, click 'Predict Emotion', and receive the predicted emotion label along with "
        "a bar chart of decision function scores for all 6 classes. "
        "(2) <b>Batch CSV Classification</b> — upload a CSV file with a 'text' column, run batch "
        "classification, and download the results as a new CSV. An emotion distribution pie chart "
        "is shown for the batch output.",
        B,
    ))
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151235.png"),
        caption="Figure 10.4 – Classify tab: Single text and batch CSV upload interface",
        styles=S,
    )
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151546.png"),
        caption="Figure 10.5 – Single text classification: 'i am really happy' predicted as Joy with decision scores",
        styles=S,
    )
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151650.png"),
        caption="Figure 10.6 – Batch CSV classification: Uploaded emotion_data.csv preview",
        styles=S,
    )

    story.append(Spacer(1, 0.15 * cm))
    # Tab 3
    story.append(Paragraph("Tab 3 – RAG Assistant", S["h3"]))
    story.append(Paragraph(
        "A <b>Retrieval-Augmented Generation (RAG)</b> assistant that answers questions about "
        "customer emotions grounded in real classified examples from the dataset. "
        "The retrieval step uses TF-IDF cosine similarity to find the 5 most relevant examples. "
        "If an OpenAI API key is configured, the retrieved context is passed to GPT-4o-mini to "
        "generate a synthesized answer. Without an API key, the app operates in extractive-only "
        "fallback mode, displaying the retrieved examples directly.",
        B,
    ))
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151316.png"),
        caption="Figure 10.7 – RAG Assistant tab: Question input interface",
        styles=S,
    )
    story += add_image(
        os.path.join(SCREENS, "Screenshot 2026-09-16 151412.png"),
        caption="Figure 10.8 – RAG Assistant: Retrieved examples for query 'What triggers anger?'",
        styles=S,
    )

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 11 – all_results/ (NOT UPLOADED)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 11 – Experiment Artifacts (all_results/) – Not Uploaded to Git", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "The <b>all_results/</b> folder holds every intermediate artifact from the full experiment "
        "run — trained model weights, training histories, and detailed reports. This folder is "
        "<b>excluded from version control</b> (listed in <i>.gitignore</i>) due to large file sizes. "
        "The table below documents its complete contents.",
        B,
    ))
    story.append(Spacer(1, 0.2 * cm))

    ar_h = ["Folder / File", "Contents", "Why Not Uploaded"]
    ar_d = [
        ["classical/",
         "best_model.joblib, best_vectorizer.joblib, calibrated_model.joblib, calibration_summary.csv, confidence_threshold_analysis.csv, lr_vs_svm_baseline.csv, ngram_and_maxfeatures_sweep.csv",
         "Joblib model files are large"],
        ["deep_learning/",
         "best_dl_model_classwise_report.csv, dl_metrics.csv, histories/*.json (training histories), weights/*.pt (PyTorch weights for MLP, CNN, RNN, LSTM, GRU, BiLSTM)",
         ".pt weight files are large (hundreds of MB)"],
        ["transformer/",
         "history.json, transformer_metrics.csv, transformer_classwise_report.csv, model/ (config.json, model.safetensors, tokenizer files)",
         "model.safetensors alone is ~260 MB"],
        ["topic_modeling/",
         "topic_name_mapping.json, topic_top_words_by_emotion.json, emotion_topic_counts.csv, emotion_topic_percentage.csv",
         "Included for reference — not uploaded due to overall folder gitignore"],
        ["priority_scoring/",
         "emotion_weights.json, topic_weights.json, urgency_keywords.json, topic_assignments_master.csv (~2 MB)",
         "master CSV is large"],
        ["human_review/",
         "human_review_queue.csv (60-item QA queue)",
         "Included for reference — not uploaded due to folder gitignore"],
        ["summary/",
         "full_model_comparison.csv — source of the model_comparison SQL table",
         "Included for reference — not uploaded due to folder gitignore"],
        ["emotion_analysis.db",
         "Full copy of the analytics database bundled with the experiment run (~2.7 MB)",
         "Included for reference — not uploaded due to folder gitignore"],
    ]
    t_ar = Table(ar_h + ar_d if False else [ar_h] + ar_d,
                 colWidths=[2.8*cm, 6.2*cm, 5.4*cm], repeatRows=1)
    t_ar.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ROW_HEADER),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, ROW_ALT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
    ]))
    story.append(t_ar)
    story.append(Paragraph("Table 11.1 – Contents of all_results/ and reason for gitignore exclusion.", S["caption"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "<b>To regenerate:</b> Re-run <i>notebooks/Teck_Final_merged.ipynb</i> end-to-end. "
        "Alternatively, keep a copy of <i>all_results.zip</i> in external storage (Google Drive, S3, etc.).",
        B,
    ))

    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 12 – KEY FINDINGS & LIMITATIONS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(section_header("Section 12 – Key Findings &amp; Limitations", S))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("<b>Key Findings:</b>", S["h2"]))
    findings = [
        "<b>Transformer advantage is modest:</b> DistilBERT (92.72%) beats the best classical model "
        "(LinearSVC, 89.34%) by only ~3.4 accuracy points. A well-tuned TF-IDF + LinearSVM remains "
        "a strong, deployable baseline for short-text emotion classification.",
        "<b>Unigrams win the sweep:</b> Plain unigrams with a 5,000-word vocabulary outperformed every "
        "richer n-gram configuration tested. Adding bigrams or trigrams, or expanding the vocabulary, "
        "did not improve performance — confirming that emotional signal is primarily carried by individual words.",
        "<b>Priority scoring is directionally correct:</b> Negative emotions (anger, fear, sadness) "
        "receive significantly higher average business-priority scores than positive emotions, validating "
        "the scoring pipeline for customer-support triage.",
        "<b>GRU is the best deep learning model:</b> Among the 6 DL architectures, GRU (90.97%) "
        "outperforms LSTM (90.34%) and all simpler models, while BiLSTM severely underperforms (80.69%).",
        "<b>Confidence thresholding is powerful:</b> Setting a confidence threshold of 0.9 allows the "
        "calibrated SVM to achieve 99.43% accuracy on the 49% of data it accepts — suitable for "
        "high-stakes automated decisions.",
        "<b>RAG adds explainability:</b> The RAG assistant provides grounded, evidence-backed answers "
        "about customer emotion patterns, useful for business analysts without ML expertise.",
    ]
    for f in findings:
        story.append(Paragraph(f"• {f}", BU))
        story.append(Spacer(1, 0.05 * cm))

    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width=PAGE_W - 2 * MARGIN, thickness=0.5, color=GRAY_LINE))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("<b>Limitations &amp; Future Work:</b>", S["h2"]))
    limitations = [
        "<b>Small, single-domain dataset:</b> Trained on 16K pre-cleaned, single-domain (Twitter-style) "
        "texts. Results may not generalize to longer or more varied customer text such as emails, "
        "support tickets, or product reviews.",
        "<b>Deployed model accuracy trade-off:</b> The deployed LinearSVC model trades ~3.4 accuracy "
        "points for a dramatically smaller deployment footprint. Serving the fine-tuned DistilBERT is "
        "a natural next step when more compute is available.",
        "<b>BiLSTM training issue:</b> BiLSTM's anomalously low performance (80.69%) should be revisited "
        "with tuned learning rates, different initialization, or adjusted early-stopping. Its result "
        "is not a reliable architectural data point in its current form.",
        "<b>RAG depends on external API:</b> The generative step of the RAG Assistant requires an "
        "OpenAI API key. Without one, only extractive retrieval is available, limiting the system's "
        "natural-language response quality.",
        "<b>Minority class variance:</b> Metrics for <i>love</i> (261 test examples) and "
        "<i>surprise</i> (115 test examples) carry high variance. Single-run results should be "
        "interpreted cautiously; cross-validation or repeated evaluation would yield more stable estimates.",
        "<b>No multi-label support:</b> The system assumes a single emotion per text. Real customer "
        "messages may express multiple emotions simultaneously, requiring a multi-label classification approach.",
    ]
    for l in limitations:
        story.append(Paragraph(f"• {l}", BU))
        story.append(Spacer(1, 0.05 * cm))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width=PAGE_W - 2 * MARGIN, thickness=1, color=DARK_BLUE))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "End of Report",
        ParagraphStyle("end", parent=S["body"], alignment=TA_CENTER,
                       fontName="Helvetica-Bold", fontSize=11, textColor=DARK_BLUE),
    ))

    return story


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    print(f"Building report -> {OUTPUT}")
    styles = make_styles()

    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=2.2 * cm,
        title="Customer Sentiment & Emotion Intelligence Platform – Project Report",
        author="Kirellos Nader, Fayrous Hassan, Loaa Elshatby, Karim Yunis, Mazen Eldayash, Luay Mohamed",
        subject="NLP Emotion Classification Platform Report",
        creator="ReportLab",
    )

    story = build_story(styles)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"Done! File saved: {OUTPUT}")
    print(f"File size: {size_kb:.1f} KB  ({size_kb/1024:.2f} MB)")


if __name__ == "__main__":
    main()
