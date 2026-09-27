
import os
import json
import re
import time
import random
import streamlit as st
from dotenv import load_dotenv
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI App Review Analyzer",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.8-flash"

client = genai.Client(api_key=api_key) if api_key else None


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "rating" not in st.session_state:
    st.session_state.rating = None


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.title("🤖 AI App Review Analyzer")
    st.subheader("Login to Continue")

    with st.form("login_form"):

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        email = st.text_input(
            "Gmail",
            placeholder="Enter your Gmail address"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

        if submitted:

            if not username.strip():
                st.error("Please enter your username.")

            elif not re.fullmatch(
                r"[A-Za-z0-9._%+-]+@gmail\.com",
                email.strip(),
                re.IGNORECASE
            ):
                st.error("Please enter a valid Gmail address.")

            elif not password.strip():
                st.error("Please enter your password.")

            else:
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.rerun()


# ============================================================
# GEMINI API WITH RETRY
# ============================================================

def generate_with_retry(prompt):

    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Please configure it in your .env file."
        )

    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text.strip()

        except Exception as e:

            error_text = str(e).lower()

            retryable = any(
                code in error_text
                for code in [
                    "503",
                    "429",
                    "500",
                    "502",
                    "504",
                    "unavailable",
                    "resource_exhausted",
                    "internal",
                    "deadline_exceeded"
                ]
            )

            if not retryable:
                raise

            if attempt == max_retries - 1:
                raise RuntimeError(
                    "Gemini is currently busy or unavailable. "
                    "Please wait a little and try again."
                ) from e

            wait_time = 3 * (2 ** attempt) + random.uniform(0, 1)

            st.warning(
                f"Gemini is busy. Retrying in {wait_time:.1f} seconds..."
            )

            time.sleep(wait_time)


# ============================================================
# REVIEW ANALYSIS
# ============================================================

def analyze_review(app_name, category, review):

    prompt = f"""
You are an AI App Review Analyzer.

Analyze the following app review carefully.

APP NAME: {app_name}
APP CATEGORY: {category}
USER REVIEW: {review}

INSTRUCTIONS:

1. Identify the exact problem from the user's review.
2. Give practical, real-world solutions specific to the app and issue.
3. Every step must tell the user exactly what to do and where to do it.
4. Avoid generic steps like restarting, reinstalling, or checking
   permissions unless they are relevant to the specific problem.
5. Never recommend actions that could delete user data or overwrite
   backups without explaining the risk and checking safer alternatives.
6. Do not repeat the user's complaint as a solution.
7. Do not invent app settings, features, or technical details.
8. If the exact cause is unknown, explain what the user should check first.
9. Provide 4-6 clear, actionable steps whenever appropriate.
10. Separate user actions from developer actions.
11. Make sure the solution directly addresses the reported problem.
12. If the review is positive, return "No Problem" and do not invent a solution.

Return ONLY valid JSON in this exact structure:

{{
    "problem": "Actual problem or No Problem",
    "category": "Problem category",
    "severity": "Low, Medium, High, or None",
    "why": "Brief explanation",
    "steps": [
        "Step 1",
        "Step 2",
        "Step 3"
    ],
    "user_action": "What the user should do",
    "developer_action": "What the developer should do"
}}
"""

    response_text = generate_with_retry(prompt)

    # Remove Markdown code fences if present
    response_text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response_text.strip(),
        flags=re.IGNORECASE
    )

    result = json.loads(response_text)

    required_keys = [
        "problem",
        "category",
        "severity",
        "why",
        "steps",
        "user_action",
        "developer_action"
    ]

    for key in required_keys:
        if key not in result:
            raise ValueError(f"Missing field in AI response: {key}")

    return result


# ============================================================
# MAIN APPLICATION
# ============================================================

def main_app():

    st.title("🤖 AI App Review Analyzer")

    st.write(
        "Analyze app reviews, identify problems, "
        "and get practical solutions using AI."
    )

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.title("👤 User Profile")

        st.write(
            f"Welcome, **{st.session_state.username}**!"
        )

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):

            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.analysis_result = None
            st.session_state.rating = None

            st.rerun()

    # --------------------------------------------------------
    # APP DETAILS
    # --------------------------------------------------------

    st.subheader("📱 App Details")

    col1, col2 = st.columns(2)

    with col1:

        app_name = st.text_input(
            "App Name",
            placeholder="Example: WhatsApp"
        )

    with col2:

        app_category = st.selectbox(
            "App Category",
            [
                "Communication",
                "Shopping",
                "Food & Delivery",
                "Social Media",
                "Entertainment",
                "Education",
                "Healthcare",
                "Banking & Finance",
                "Travel",
                "Productivity",
                "Other"
            ]
        )

    # --------------------------------------------------------
    # REVIEW INPUT
    # --------------------------------------------------------

    st.subheader("💬 Enter User Review")

    review = st.text_area(
        "User Review",
        placeholder="Enter the app review here...",
        height=150
    )

    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    if st.button(
        "🔍 Analyze Review",
        use_container_width=True,
        type="primary"
    ):

        if not app_name.strip():
            st.error("Please enter the app name.")

        elif not review.strip():
            st.error("Please enter a user review.")

        else:

            try:

                with st.spinner("Analyzing review with AI..."):

                    result = analyze_review(
                        app_name,
                        app_category,
                        review
                    )

                st.session_state.analysis_result = {
                    "app_name": app_name,
                    "app_category": app_category,
                    "review": review,
                    "result": result
                }

                st.session_state.rating = None

            except Exception as e:

                st.error(f"Analysis failed: {e}")

    # --------------------------------------------------------
    # DISPLAY ANALYSIS REPORT
    # --------------------------------------------------------

    report = st.session_state.analysis_result

    if report:

        result = report["result"]

        st.divider()

        st.header("📊 Review Analysis Report")

        # App details
        st.subheader("📱 App Details")

        st.write(f"**App Name:** {report['app_name']}")
        st.write(f"**App Category:** {report['app_category']}")

        # Review
        st.subheader("💬 User Review")

        st.info(report["review"])

        # Problem statement
        st.subheader("🚨 Problem Statement")

        st.write(result["problem"])

        # Category
        st.subheader("🏷️ Problem Category")

        st.write(result["category"])

        # Severity
        st.subheader("⚠️ Severity")

        severity = result["severity"]

        if severity.lower() == "high":
            st.error(f"🔴 {severity}")

        elif severity.lower() == "medium":
            st.warning(f"🟠 {severity}")

        elif severity.lower() == "low":
            st.info(f"🟢 {severity}")

        else:
            st.success(f"✅ {severity}")

        # Why
        st.subheader("🔎 Why Does This Problem Occur?")

        st.write(result["why"])

        # Practical solution
        st.subheader("🛠️ Step-by-Step Solution")

        steps = result["steps"]

        if isinstance(steps, list):

            for index, step in enumerate(steps, start=1):
                st.write(f"**Step {index}:** {step}")

        else:
            st.write(steps)

        # User action
        st.subheader("👤 User Action")

        st.write(result["user_action"])

        # Developer action
        st.subheader("👨‍💻 Developer Action")

        st.write(result["developer_action"])

        # ----------------------------------------------------
        # STAR RATING
        # ----------------------------------------------------

        st.divider()

        st.subheader("⭐ Rate Your Experience")

        rating = st.feedback(
            "stars",
            key="experience_star_rating"
        )

        if rating is not None:

            rating_value = rating + 1

            st.session_state.rating = rating_value

            st.success(
                f"Thank you for your rating! {'⭐' * rating_value}"
            )

        # ----------------------------------------------------
        # DOWNLOAD REPORT
        # ----------------------------------------------------

        st.divider()

        st.subheader("📥 Download Report")

        download_data = {
            "app_name": report["app_name"],
            "app_category": report["app_category"],
            "user_review": report["review"],
            "analysis": result,
            "rating": st.session_state.rating
        }

        json_data = json.dumps(
            download_data,
            indent=4,
            ensure_ascii=False
        )

        st.download_button(
            label="📥 Download JSON Report",
            data=json_data,
            file_name="review_analysis_report.json",
            mime="application/json",
            use_container_width=True
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if not st.session_state.logged_in:

    login_page()

else:

    main_app()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI App Review Analyzer | NLP Mini Project"
)