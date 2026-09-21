import os
import json
import joblib
import streamlit as st
from openai import OpenAI


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI App Review Analyzer",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "review_model.pkl"
)


# ============================================================
# LOAD LOCAL NLP MODEL
# ============================================================

@st.cache_resource
def load_model():

    if not os.path.exists(MODEL_PATH):
        return None

    try:
        return joblib.load(MODEL_PATH)

    except Exception as e:

        st.error(
            "Unable to load the NLP model."
        )

        st.code(
            str(e)
        )

        return None


model = load_model()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.title(
        "🤖 AI App Review Analyzer"
    )

    st.subheader(
        "Login"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    login_button = st.button(
        "Login"
    )

    if login_button:

        if username.strip() and password.strip():

            st.session_state.logged_in = True

            st.session_state.username = (
                username.strip()
            )

            st.success(
                "Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "Please enter username and password."
            )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "🤖 AI Review Analyzer"
    )

    st.write(
        f"Welcome, {st.session_state.username}"
    )

    st.divider()

    if st.button(
        "Logout"
    ):

        st.session_state.logged_in = False

        st.session_state.username = ""

        st.rerun()


# ============================================================
# MAIN TITLE
# ============================================================

st.title(
    "🤖 AI App Review Analyzer"
)

st.write(
    "Write a review about any application in your own words."
)

st.info(
    "The system dynamically understands your review and "
    "generates the problem, severity, explanation, "
    "solution steps, user action, and developer action."
)


# ============================================================
# APP DETAILS
# ============================================================

st.header(
    "📱 App Details"
)

app_name = st.text_input(
    "Application Name",
    placeholder=(
        "Example: Instagram, Amazon, Spotify, Uber..."
    )
)


# ============================================================
# APPLICATION CATEGORY
# ============================================================
#
# Category is ONLY supporting information.
#
# It is NOT used as a problem-category restriction.
# ============================================================

app_category = st.selectbox(
    "Application Category",
    [
        "Social Media",
        "Shopping",
        "Banking / Finance",
        "Education",
        "Food Delivery",
        "Travel",
        "Entertainment",
        "Productivity",
        "Healthcare",
        "Gaming",
        "Other"
    ]
)


# ============================================================
# REVIEW
# ============================================================

st.header(
    "📝 Write Your Review"
)

review = st.text_area(
    "Describe your experience in your own words",

    placeholder=(
        "Write anything about your application experience..."
    ),

    height=180
)


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_openai_client():

    api_key = None

    # --------------------------------------------------------
    # Try Streamlit secrets first
    # --------------------------------------------------------

    try:

        api_key = st.secrets.get(
            "OPENAI_API_KEY"
        )

    except Exception:

        api_key = None


    # --------------------------------------------------------
    # Try environment variable
    # --------------------------------------------------------

    if not api_key:

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )


    # --------------------------------------------------------
    # No API key
    # --------------------------------------------------------

    if not api_key:

        return None


    return OpenAI(
        api_key=api_key
    )


# ============================================================
# GENERATIVE AI ANALYSIS
# ============================================================

def generate_analysis(
    app_name,
    app_category,
    review,
    model_prediction,
    model_confidence
):

    client = get_openai_client()

    if client is None:

        return {
            "error": (
                "OPENAI_API_KEY is not configured.\n\n"
                "Configure your OpenAI API key in "
                "Streamlit Secrets or your environment."
            )
        }


    # ========================================================
    # AI SYSTEM INSTRUCTIONS
    # ========================================================
    #
    # IMPORTANT:
    #
    # There is intentionally NO predefined:
    #
    # - problem category list
    # - keyword list
    # - solution dictionary
    # - application-specific rule
    #
    # The user's review is the primary source.
    # ========================================================

    system_prompt = """

You are an AI application review troubleshooting assistant.

Your job is to understand ANY application review written
naturally by a user.

The application can be any application.

The user can describe any experience, issue, request,
failure, unexpected behavior, or other situation.

There is NO fixed problem-category list.

There is NO fixed keyword list.

There is NO fixed solution dictionary.

You must understand the meaning of the user's complete
review and respond dynamically.

IMPORTANT RULES:

1. Read the complete user review before analyzing it.

2. The user's review is the PRIMARY source of information.

3. The application name is context only.

4. The application category is context only.

5. Do NOT assume a problem based only on the application name.

6. Do NOT assume a problem based only on the application category.

7. Do NOT force the review into a predefined problem category.

8. Do NOT use keyword matching as the primary reasoning method.

9. Do NOT use a predefined solution dictionary.

10. Do NOT perform sentiment analysis.

11. Determine whether the review actually describes a problem.

12. If the review does NOT describe a problem, clearly say
    that no specific problem was identified.

13. If the review describes a problem, identify the actual
    problem from the user's words and context.

14. Do not invent facts that the user did not provide.

15. If important information is missing, clearly mention
    what additional information may be required.

16. Severity must depend on the impact described by the user.

17. Give practical troubleshooting steps relevant to the
    actual situation.

18. Do not give identical generic steps for every review.

19. Different problems should receive different
    troubleshooting approaches.

20. Clearly separate USER ACTION from DEVELOPER ACTION.

21. For account, payment, security, or personal-data issues,
    recommend using the application's official support process
    when appropriate.

22. Never claim that a troubleshooting step is guaranteed.

23. The local NLP model prediction is only supporting
    information. Do not blindly follow it.

24. The local NLP model does NOT determine the detailed
    problem.

25. The user's actual review has priority over the local
    model prediction.

Return ONLY valid JSON.

Use exactly this structure:

{
    "problem": "actual problem identified from the review",
    "severity": "Low",
    "why": "reason the problem may be happening",
    "steps": [
        "first practical step",
        "second practical step",
        "third practical step",
        "fourth practical step"
    ],
    "user_action": "what the user should do now",
    "developer_action": "what the developer should investigate"
}

If there is no identifiable problem, use:

"problem": "No specific problem identified from the review"

and use:

"severity": "Low"

The severity must be exactly one of:

Low
Medium
High

Do not add any other JSON fields.

Do not use markdown inside the JSON.
"""


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""

Application Name:
{app_name}

Application Category:
{app_category}

User Review:
{review}

Local NLP Model Prediction:
{model_prediction}

Local NLP Model Confidence:
{model_confidence:.2f}%

IMPORTANT:

The application name and category are supporting context only.

The user's actual review is the primary source.

Understand the review independently.

Do not blindly follow the local NLP model prediction.

Determine the actual meaning of the user's review.

The review may describe any type of application experience.

Do not assume that the review belongs to a predefined
problem category.
"""


    # ========================================================
    # OPENAI REQUEST
    # ========================================================

    try:

        response = client.responses.create(

            model="gpt-5.6-luna",

            instructions=system_prompt,

            input=user_prompt
        )


        output = response.output_text.strip()


        # ====================================================
        # REMOVE OPTIONAL MARKDOWN CODE FENCE
        # ====================================================

        if output.startswith(
            "```json"
        ):

            output = output[7:]

        elif output.startswith(
            "```"
        ):

            output = output[3:]


        if output.endswith(
            "```"
        ):

            output = output[:-3]


        output = output.strip()


        # ====================================================
        # PARSE JSON
        # ====================================================

        result = json.loads(
            output
        )

        return result


    except json.JSONDecodeError:

        return {
            "error": (
                "The AI returned an invalid JSON response.\n\n"
                "Please try the review again."
            )
        }


    except Exception as e:

        return {
            "error": (
                "AI analysis failed.\n\n"
                f"{str(e)}"
            )
        }


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🔍 Analyze Review",
    type="primary"
):

    # ========================================================
    # VALIDATION
    # ========================================================

    if not app_name.strip():

        st.warning(
            "Please enter the application name."
        )

        st.stop()


    if not review.strip():

        st.warning(
            "Please write your application review."
        )

        st.stop()


    # ========================================================
    # MODEL CHECK
    # ========================================================

    if model is None:

        st.error(
            "NLP model not found."
        )

        st.code(
            MODEL_PATH
        )

        st.info(
            "Make sure this file exists:\n"
            "model/review_model.pkl"
        )

        st.stop()


    # ========================================================
    # LOCAL NLP PREDICTION
    # ========================================================

    try:

        prediction = model.predict(
            [review]
        )[0]


        probabilities = model.predict_proba(
            [review]
        )[0]


        confidence = (
            max(probabilities) * 100
        )


    except Exception as e:

        st.error(
            "Local NLP model error."
        )

        st.code(
            str(e)
        )

        st.stop()


    # ========================================================
    # GENERATIVE AI ANALYSIS
    # ========================================================

    with st.spinner(
        "🧠 Understanding your review..."
    ):

        result = generate_analysis(

            app_name=app_name,

            app_category=app_category,

            review=review,

            model_prediction=prediction,

            model_confidence=confidence
        )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    if "error" in result:

        st.error(
            result["error"]
        )

        st.stop()


    # ========================================================
    # ANALYSIS RESULT
    # ========================================================

    st.divider()

    st.header(
        "🔎 Analysis Result"
    )


    # ========================================================
    # 1. PROBLEM
    # ========================================================

    st.subheader(
        "1️⃣ Problem Identified"
    )

    problem = result.get(
        "problem",
        "No specific problem identified from the review."
    )

    st.write(
        problem
    )


    # ========================================================
    # 2. SEVERITY
    # ========================================================

    st.subheader(
        "2️⃣ Severity"
    )

    severity = result.get(
        "severity",
        "Low"
    )


    if severity == "High":

        st.error(
            "🔴 High"
        )

    elif severity == "Medium":

        st.warning(
            "🟠 Medium"
        )

    elif severity == "Low":

        st.success(
            "🟢 Low"
        )

    else:

        st.info(
            severity
        )


    # ========================================================
    # 3. WHY
    # ========================================================

    st.subheader(
        "3️⃣ Why This Problem May Be Happening"
    )

    why = result.get(
        "why",
        "No explanation available."
    )

    st.write(
        why
    )


    # ========================================================
    # 4. SOLUTION STEPS
    # ========================================================

    st.subheader(
        "4️⃣ Step-by-Step Solution"
    )

    steps = result.get(
        "steps",
        []
    )


    if isinstance(
        steps,
        list
    ):

        for index, step in enumerate(
            steps,
            start=1
        ):

            st.write(
                f"**Step {index}:** {step}"
            )

    else:

        st.write(
            steps
        )


    # ========================================================
    # 5. USER ACTION
    # ========================================================

    st.subheader(
        "5️⃣ What You Should Do Now"
    )

    user_action = result.get(
        "user_action",
        "No user action available."
    )

    st.write(
        user_action
    )


    # ========================================================
    # 6. DEVELOPER ACTION
    # ========================================================

    st.subheader(
        "6️⃣ What the Developer Should Check"
    )

    developer_action = result.get(
        "developer_action",
        "No developer action available."
    )

    st.write(
        developer_action
    )


    # ========================================================
    # LOCAL NLP INFORMATION
    # ========================================================

    with st.expander(
        "🧠 Local NLP Model Information"
    ):

        st.write(
            "Prediction:",
            prediction
        )

        st.write(
            "Confidence:",
            f"{confidence:.2f}%"
        )

        st.caption(
            "The local NLP model provides only a broad "
            "normal/problem classification. The detailed "
            "problem understanding is generated dynamically "
            "from the user's review."
        )


    # ========================================================
    # FEEDBACK
    # ========================================================

    st.divider()

    st.subheader(
        "⭐ Was this analysis useful?"
    )

    rating = st.radio(
        "Give your feedback",

        [
            "⭐",
            "⭐⭐",
            "⭐⭐⭐",
            "⭐⭐⭐⭐",
            "⭐⭐⭐⭐⭐"
        ],

        horizontal=True
    )


    if st.button(
        "Submit Feedback"
    ):

        st.success(
            f"Thank you for your feedback: {rating}"
        )

