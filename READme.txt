Project: Identification of the User behind Drug Trafficking on Social Media (Traceguard)


-> Overview:

The Drug Trafficking User Identification System is an AI-powered web platform designed to detect and monitor potential drug trafficking activities on Twitter (X), Instagram, and Telegram.

Using NLP, Machine Learning, and Web Scraping, the system processes public social media content to identify suspicious activities and provide analytical insights for research, cybersecurity, and public safety purposes.

-> Key Features: 

Multi-Platform Data Collection

    1. Publicly available content from social platforms

    2. Modular scraping components for extendability

Advanced NLP Processing

    1. Text preprocessing with spaCy and NLTK

    2. Keyword and pattern recognition for high-risk terms

Machine Learning Classification

    1. Multiple model support (SVM, Logistic Regression, BERT)

    2. Risk scoring based on analyzed content

Interactive Dashboard

    1. Built with Flask + HTML/CSS/JS

    2. Visual analytics and trend monitoring

-> Tech Stack: 

Frontend: HTML, CSS, JavaScript
Backend: Python (Flask)
NLP/ML: spaCy, NLTK, BERT, scikit-learn
Data Handling: pandas, NumPy
Visualization: Matplotlib, Plotly
Deployment: Docker, AWS/Cloud-ready

-> Project Structure: 

├── data/                # Sample or placeholder datasets  
├── models/              # Trained ML models (example models only)  
├── scripts/             # Non-sensitive data processing scripts  
├── static/              # Frontend assets (CSS, JS, images)  
├── templates/           # HTML templates for Flask  
├── app.py               # Flask application entry point  
├── requirements.txt     # Project dependencies  
└── README.md            # Project documentation  


-> Installation & Setup: 

1. Clone the repository: 

git clone https://github.com/yourusername/Social-Drug-Trafficking_Detection.git
cd Social-Drug-Trafficking_Detection

2. Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install dependencies:

pip install -r requirements.txt

4. Run the application:

python app.py


-> Model Workflow:

1. Collect public social media content

2. Process text: cleaning, lemmatization, tokenization

3. Extract features: TF-IDF, embeddings

4. Classify using trained ML models

5. Display results in an interactive dashboard


-> Intended Use

This project is intended for educational and research purposes only.
It should be used to explore AI/NLP techniques for social media analysis — not for unauthorized surveillance or targeting individuals.




