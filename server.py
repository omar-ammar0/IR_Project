from flask import Flask, render_template, request, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import wikipediaapi
from nltk.stem import PorterStemmer
import string

app = Flask(__name__, static_url_path='/static')

nltk.download('punkt')
nltk.download('stopwords')

def get_wikipedia_articles(topics, num_articles_per_topic):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='IRProject/1.0'
    )

    all_articles = []
    for topic in topics:
        articles = []
        search_results = wiki_wiki.page(topic)
        if search_results.exists():
            for title in search_results.links.keys():
                page = wiki_wiki.page(title)
                if page.exists():
                    articles.append({
                        'title': title,
                        'text': preprocess_text(page.text),
                        'link': "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
                    })
                if len(articles) >= num_articles_per_topic:
                    break
        all_articles.extend(articles)

    return all_articles

def preprocess_text(input_text):
    text = input_text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    return ' '.join(stemmed_tokens)

def build_tfidf_matrix(documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    return vectorizer, tfidf_matrix

def find_relevant_articles(query, vectorizer, tfidf_matrix, articles, top_n=5):
    query_processed = preprocess_text(query)
    query_tfidf = vectorizer.transform([query_processed])
    cosine_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
    top_indices = np.argsort(cosine_similarities)[-top_n:][::-1]
    return [(articles[i]['title'], articles[i]['link'], cosine_similarities[i]) for i in top_indices]

topics = ['Artificial Intelligence', 'Machine Learning', 'Data Science']
articles = get_wikipedia_articles(topics, 17)
vectorizer, tfidf_matrix = build_tfidf_matrix([article['text'] for article in articles])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    print("Received query:", query)
    results = find_relevant_articles(query, vectorizer, tfidf_matrix, articles, top_n=10)
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)