# 📱 AI App Review Analyzer

## 📌 Project Overview

AI App Review Analyzer is an NLP-based application that analyzes app reviews and identifies the possible problem or complaint category.

The application helps users understand common issues mentioned in app reviews and provides a suggested solution.

## 🎯 Objectives

* Analyze user-provided app reviews
* Identify the main complaint category
* Perform sentiment analysis
* Provide a suggested solution
* Create an easy-to-use web application

## ✨ Features

* 🔐 User Login
* 📱 App Details
* ✍️ Review Input
* 🤖 NLP-based Review Analysis
* 🚨 Problem/Complaint Detection
* 😊 Sentiment Analysis
* 💡 Suggested Solutions
* 🌐 Streamlit Web Application

## 🧠 NLP Methodology

The project uses Natural Language Processing techniques to process and classify text.

### Workflow

User Review
↓
Text Preprocessing
↓
TF-IDF Vectorization
↓
Machine Learning Classification
↓
Complaint Category
↓
Sentiment Analysis
↓
Suggested Solution

## 🏷️ Complaint Categories

The application can identify categories such as:

* Crash/Bug
* Advertisements
* Billing/Subscription
* Login/Account
* Performance
* Privacy/Permissions
* Support
* UX/Design

## 🛠️ Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn
* TF-IDF
* Logistic Regression
* Joblib
* Streamlit

## 📂 Project Structure

```text
AI_App_Review_Analyzer/
│
├── dataset/
│   └── training_reviews.csv
│
├── model/
│   └── review_model.pkl
│
├── train_model.py
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ▶️ How to Run

### 1. Create virtual environment

```bash
python -m venv venv
```

### 2. Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 3. Install required libraries

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit application

```bash
python -m streamlit run app.py
```

The application will open in the browser.

## 📊 Model

The NLP classification model uses TF-IDF for converting text into numerical features and Logistic Regression for complaint classification.

## 🚀 Future Scope

* Support more complaint categories
* Improve NLP accuracy using a larger review dataset
* Add multilingual review analysis
* Add review history and analytics
* Deploy the application online
* Add automatic problem summarization

## 👩‍💻 Project

**AI App Review Analyzer**

Built as an NLP Mini Project.
