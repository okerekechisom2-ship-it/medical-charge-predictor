import streamlit as st
import pandas as pd
import joblib
import resend


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Medical Charge Predictor",
    page_icon="💚",
    layout="centered"
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
<style>

    /* =========================
       MAIN APP BACKGROUND
       ========================= */

    .stApp {
        background-color: #FFF8F1;
    }

    .block-container {
        max-width: 900px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }


    /* =========================
       HEADINGS
       ========================= */

    h1 {
        color: #3D3028 !important;
        font-size: 42px !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h2 {
        color: #3D3028 !important;
        font-size: 30px !important;
        font-weight: 650 !important;
    }

    h3 {
        color: #3D3028 !important;
        font-size: 24px !important;
        font-weight: 600 !important;
    }


    /* =========================
       NORMAL TEXT
       ========================= */

    p {
        color: #4A3F38 !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
    }


    /* =========================
       LABELS
       ========================= */

    label {
        color: #3D3028 !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }


    /* =========================
       INPUT FIELDS
       ========================= */

    input {
        font-size: 18px !important;
        color: #3D3028 !important;
    }

    div[data-baseweb="select"] {
        font-size: 18px !important;
    }


    /* =========================
       FORM CARD
       ========================= */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #F0DED2;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(61, 48, 40, 0.08);
    }


    /* =========================
       INPUT SPACING
       ========================= */

    .stNumberInput,
    .stSelectbox,
    .stTextInput {
        margin-bottom: 12px;
    }


    /* =========================
       PREDICT BUTTON
       ========================= */

    .stButton > button {
        width: 100%;
        background-color: #D97757;
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 14px 24px;
        font-size: 19px !important;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #B85F43;
        color: white !important;
        border: none;
    }


    /* =========================
       SUCCESS / RESULT BOX
       ========================= */

    div[data-testid="stAlert"] {
        border-radius: 14px;
        font-size: 19px !important;
    }


    /* =========================
       DISCLAIMER
       ========================= */

    .disclaimer {
        background-color: #F5DED2;
        padding: 18px;
        border-radius: 12px;
        margin-top: 20px;
        color: #5A453B;
        font-size: 15px;
        line-height: 1.6;
    }


    /* =========================
       SUBTITLE
       ========================= */

    .subtitle {
        font-size: 20px !important;
        color: #6B5A50 !important;
        margin-top: -10px;
        margin-bottom: 30px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# RESEND API
# ============================================================

resend.api_key = st.secrets["RESEND_API_KEY"]


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model = joblib.load("insurance_model.pkl")


# ============================================================
# PAGE HEADER
# ============================================================

st.title("Medical Charge Predictor")

st.markdown(
    '<p class="subtitle">'
    'Get an estimated medical charge based on the information you provide.'
    '</p>',
    unsafe_allow_html=True
)


# ============================================================
# USER INPUTS
# ============================================================

with st.container(border=True):

    st.subheader("Your Information")

    # Name
    name = st.text_input(
        "Name",
        placeholder="Enter your name"
    )

    # Email
    email = st.text_input(
        "Email Address",
        placeholder="Enter your email address"
    )

    # Age
    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=30
    )

    # Sex
    sex = st.selectbox(
        "Sex",
        ["female", "male"]
    )

    # BMI
    bmi = st.number_input(
        "BMI",
        min_value=10.0,
        max_value=60.0,
        value=25.0
    )

    # Number of children
    children = st.number_input(
        "Number of Children",
        min_value=0,
        max_value=10,
        value=0
    )

    # Smoker
    smoker = st.selectbox(
        "Smoker",
        ["no", "yes"]
    )

    # Region
    region = st.selectbox(
        "Region",
        [
            "northeast",
            "northwest",
            "southeast",
            "southwest"
        ]
    )


# ============================================================
# CONVERT CATEGORICAL VALUES
# ============================================================

# Female = 0
# Male = 1

sex_value = 0 if sex == "female" else 1


# No = 0
# Yes = 1

smoker_value = 0 if smoker == "no" else 1


# ============================================================
# REGION ENCODING
# ============================================================

# Northeast is the reference region.
# Therefore, when northeast is selected,
# all three region columns are 0.

region_northwest = 1 if region == "northwest" else 0
region_southeast = 1 if region == "southeast" else 0
region_southwest = 1 if region == "southwest" else 0


# ============================================================
# CREATE INPUT DATAFRAME
# ============================================================

input_data = pd.DataFrame({
    "age": [age],
    "sex": [sex_value],
    "bmi": [bmi],
    "children": [children],
    "smoker": [smoker_value],
    "region_northwest": [region_northwest],
    "region_southeast": [region_southeast],
    "region_southwest": [region_southwest]
})


# ============================================================
# PREDICTION BUTTON
# ============================================================

st.write("")

if st.button("Predict Medical Charge"):

    # --------------------------------------------------------
    # CHECK NAME AND EMAIL
    # --------------------------------------------------------

    if not name or not email:

        st.warning(
            "Please enter your name and email address."
        )

    else:

        # ----------------------------------------------------
        # MAKE PREDICTION
        # ----------------------------------------------------

        prediction = model.predict(input_data)

        # Prediction from the model is in USD
        predicted_charge_usd = prediction[0]


        # ----------------------------------------------------
        # CONVERT USD TO NAIRA
        # ----------------------------------------------------

        # Fixed exchange rate for now
        exchange_rate = 1370

        predicted_charge_naira = (
            predicted_charge_usd * exchange_rate
        )


        # ----------------------------------------------------
        # DISPLAY RESULT
        # ----------------------------------------------------

        st.success(
            f"Estimated Medical Charge: "
            f"₦{predicted_charge_naira:,.2f}"
        )


        # ----------------------------------------------------
        # SEND EMAIL
        # ----------------------------------------------------

        try:

            resend.Emails.send({

                "from": (
                    "Medical Charge Predictor "
                    "<onboarding@resend.dev>"
                ),

                "to": [email],

                "subject": (
                    "Your Medical Charge Prediction"
                ),

                "html": f"""

                    <h2>Hello {name},</h2>

                    <p>
                        Thank you for using the
                        Medical Charge Predictor.
                    </p>

                    <p>
                        Based on the information you provided,
                        your estimated medical charge is:
                    </p>

                    <h2>
                        ₦{predicted_charge_naira:,.2f}
                    </h2>

                    <p>
                        Please note that this is an estimated
                        prediction generated by a machine
                        learning model and is not a guaranteed
                        medical cost.
                    </p>

                    <p>
                        Thank you for using the
                        Medical Charge Predictor.
                    </p>

                """
            })


            # ------------------------------------------------
            # EMAIL SUCCESS MESSAGE
            # ------------------------------------------------

            st.success(
                "Your prediction has also been sent to your email!"
            )


        # ----------------------------------------------------
        # EMAIL ERROR
        # ----------------------------------------------------

        except Exception as e:

            st.error(
                "The prediction was successful, but we "
                "could not send the email."
            )

            st.caption(
                f"Email error: {e}"
            )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown("""
<div class="disclaimer">

<strong>Please note:</strong><br>

This tool provides an estimated medical charge based on
a machine learning model and the information entered.
It is intended for educational and informational purposes
only and should not be treated as an actual medical bill
or guaranteed healthcare cost.

</div>
""", unsafe_allow_html=True)