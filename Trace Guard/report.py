import os
import re
import pandas as pd
from transformers import pipeline
from fpdf import FPDF
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', str(text))

def check_suspicious(scraped_file, reference_file):
    try:
        scraped = pd.read_csv(scraped_file)
        reference = pd.read_csv(reference_file)
        
        scraped_text = " ".join(scraped['text'].fillna('').apply(clean_text))
        reference_text = " ".join(reference['text'].fillna('').apply(clean_text))
        
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([scraped_text, reference_text])
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        
        return min(100, max(0, round(similarity * 100, 2)))
    
    except Exception:
        return 0.0

def generate_nlp_report(data_file, score, output_pdf):
    try:
        data = pd.read_csv(data_file)
        texts = " ".join(data['text'].fillna('').apply(clean_text))
        
        # Summary
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(texts[:1024], max_length=130, min_length=30)[0]['summary_text']
        
        # Word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texts)
        wc_file = "temp_wc.png"
        wordcloud.to_file(wc_file)
        
        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Social Media Activity Analysis Report", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Suspicious Content Score: {score}%", ln=1)
        
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"Key Findings:\n{summary}")
        
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Frequent Terms", ln=1)
        pdf.image(wc_file, x=10, y=30, w=190)
        
        pdf.output(output_pdf)
        os.remove(wc_file)
        return True
    
    except Exception:
        return False