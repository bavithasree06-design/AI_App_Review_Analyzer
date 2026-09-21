import os
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "review_model.pkl"
)


# ============================================================
# NORMAL EXPERIENCE DATA
# ============================================================
#
# The local model only learns:
#
# normal  -> user describes a normal/positive experience
# problem -> user describes something that is not working
#
# It does NOT learn specific problem categories.
#
# Detailed problem understanding is handled dynamically
# by the generative AI in app.py.
# ============================================================

normal_examples = [

    "the application is working properly",
    "everything is working as expected",
    "the app works normally",
    "I am able to use the application without any issue",
    "the application is easy to use",
    "everything is fine",
    "the service is working correctly",
    "I have no problem using this application",
    "the application works well",
    "I am satisfied with the application",

    "the app is working",
    "everything works",
    "the application works correctly",
    "I can use the application normally",
    "there are no issues",
    "I did not face any problem",
    "the service works fine",
    "the application is functioning normally",
    "I can use all the features normally",
    "the app is fine"
]


# ============================================================
# GENERAL PROBLEM EXPERIENCE DATA
# ============================================================
#
# These examples intentionally remain general.
#
# There are NO fixed categories such as:
# login, payment, delivery, ads, crash, etc.
#
# The purpose is only to teach the model the broad concept
# of a problem being present.
# ============================================================

problem_examples = [

    "the application is not working properly",
    "something is wrong with the application",
    "I am facing an issue while using the application",
    "the application is behaving unexpectedly",
    "something stopped working",
    "I am unable to use the application",
    "the application is giving me trouble",
    "I am facing a problem",
    "something is not working correctly",
    "the application is not responding as expected",

    "I cannot use the application properly",
    "the application is causing a problem",
    "I am having trouble using the application",
    "the application is not functioning correctly",
    "something went wrong",
    "I am facing an unexpected issue",
    "the application stopped working",
    "the application does not work as expected",
    "I cannot continue using the application",
    "there is an issue with the application",

    "I am having a problem while using the service",
    "the service is not working correctly",
    "the application is behaving incorrectly",
    "the application is causing difficulties",
    "I am unable to complete what I was trying to do",
    "the application failed to perform correctly",
    "something is preventing me from using the application",
    "the application is not functioning as expected",
    "I need help with an application problem",
    "I need assistance with an issue"
]


# ============================================================
# FINAL TRAINING DATA
# ============================================================

reviews = (
    normal_examples
    +
    problem_examples
)

labels = (
    ["normal"] * len(normal_examples)
    +
    ["problem"] * len(problem_examples)
)


# ============================================================
# CREATE NLP PIPELINE
# ============================================================

model = Pipeline([

    (
        "tfidf",

        TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",

            # Learn words and short phrases
            ngram_range=(1, 2),

            # Better weighting for repeated patterns
            sublinear_tf=True,

            min_df=1
        )
    ),

    (
        "classifier",

        LogisticRegression(
            max_iter=3000,
            random_state=42
        )
    )
])


# ============================================================
# TRAIN MODEL
# ============================================================

print()
print("=" * 60)
print("        AI APP REVIEW NLP MODEL TRAINING")
print("=" * 60)

print()
print("Training examples:", len(reviews))

print()
print("Normal examples:", len(normal_examples))
print("Problem examples:", len(problem_examples))

print()
print("Training NLP model...")

model.fit(
    reviews,
    labels
)


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)


# ============================================================
# TEST MODEL
# ============================================================
#
# These are only basic tests to verify that the model works.
# They do NOT define the problems that the application can
# understand.
# ============================================================

test_reviews = [

    "the application is working perfectly",

    "something is wrong with the application",

    "I am unable to use the application",

    "everything works fine",

    "the application is not working correctly",

    "I am happy with the application"
]


print()
print("=" * 60)
print("             MODEL TEST")
print("=" * 60)


for review in test_reviews:

    prediction = model.predict(
        [review]
    )[0]

    probabilities = model.predict_proba(
        [review]
    )[0]

    confidence = max(
        probabilities
    ) * 100

    print()
    print("Review:")
    print(review)

    print("Prediction:")
    print(prediction)

    print("Confidence:")
    print(
        round(confidence, 2),
        "%"
    )


# ============================================================
# COMPLETION
# ============================================================

print()
print("=" * 60)
print("       MODEL SAVED SUCCESSFULLY")
print("=" * 60)

print()
print("Model location:")
print(MODEL_PATH)

print()
print("Training completed successfully!")
