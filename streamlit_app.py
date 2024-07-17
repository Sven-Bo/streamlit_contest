import streamlit as st
from datetime import datetime, timezone, timedelta
import requests

WEBHOOK_URL = st.secrets["WEBHOOK_URL"]
API_KEY = st.secrets["API_KEY"]

CONTEST_END_TIME = datetime(
    2024, 7, 24, 23, 59, 59, tzinfo=timezone(timedelta(hours=2))
)


def verify_email(email):
    response = requests.get(
        f"https://emailverifier.reoon.com/api/v1/verify?email={email}&key={API_KEY}&mode=power"
    )
    if response.status_code == 200:
        email_info = response.json()
        if (
            email_info["status"] == "safe"
            and not email_info["is_disposable"]
            and email_info["is_deliverable"]
        ):
            return True, ""  # Email is safe, not disposable, and deliverable
        elif email_info["is_disposable"]:
            return (
                False,
                "Looks like you've used a temporary email. Please use a permanent one! 🚫",
            )
        elif not email_info["is_deliverable"]:
            return False, "This email doesn't seem deliverable. Double-check, maybe? 📭"
    return False, "We couldn't verify your email. Please try again later. 🤔"


def send_data_via_webhook(data):
    response = requests.post(WEBHOOK_URL, json=data)
    return response.status_code == 200


def check_contest_deadline():
    now = datetime.now(timezone(timedelta(hours=2)))
    if now > CONTEST_END_TIME:
        st.error("Sorry, the contest has ended.")
        st.stop()


st.set_page_config("T-Shirt Contest", page_icon="🏆")

st.title("Win a Streamlit T-Shirt!", anchor=False)
col1, col2 = st.columns((2, 1))
with col1:
    st.write(" ")
    st.subheader(
        "It's Sven from CodingIsFun! Participate in my contest to win an exclusive Streamlit T-shirt.",
        anchor=False,
    )
col2.image("assets/streamlit_tshirt.jpg", width=150)
st.divider()
st.info(
    "Watch the video below and find out **which Streamlit version I used**. "
    "Then, submit your answer to enter the contest!",
    icon="💡",
)
st.video("https://youtu.be/9n4Ch2Dgex0")
st.divider()
st.info(
    "Contest ends on Wednesday, 24th July 2024 EOD CET. The winner will be picked by random choice on Thursday, 25th July and informed via email.",
    icon="💡",
)

with st.form("submission_form"):
    email = st.text_input("Email Address")
    name = st.text_input("First Name")
    streamlit_version = st.selectbox(
        label="Which Streamlit version did I use in the video?",
        options=["1.37.0", "1.36.0", "1.35.0", "1.34.0"],
        index=None,
        placeholder="Choose an option",
    )
    compliance = st.checkbox("I agree to the terms and conditions.")

    with st.expander("Terms and Conditions"):
        st.markdown(
            """
            Please read these terms and conditions carefully before participating in the contest. By entering the contest, you agree to be bound by these terms and conditions:

            - **Eligibility**: Participation is open to individuals who agree to provide their email for the purpose of contest communication. Each participant is allowed only one entry.
            
            - **Contest Period**: The contest will conclude on Wednesday, 24th July 2024 at the end of the day (EOD) CET. Entries submitted after this period will not be considered.
            
            - **Selection of Winner**: The winner will be selected randomly on Thursday, 25th July 2024. The chosen winner will be notified via the provided email address.
            
            - **Data Protection**: Your privacy is important to me. The email address you provide will be used exclusively for the purpose of this contest communication and will not be shared with third parties without your consent.
            
            - **Deletion of Data**: All email addresses collected during this contest will be deleted after the contest has concluded and the winner has been announced and contacted. This is to ensure your data is not held longer than necessary.
            
            Your participation in the contest indicates your acceptance of these terms and conditions.
        """,
            unsafe_allow_html=True,
        )

    submit_button = st.form_submit_button("Submit")

if submit_button:
    check_contest_deadline()
    if not email:
        st.error("Hold up! Need your email before you can dash off", icon="📨")
        st.stop()

    if not name:
        st.error("Oops! Your name's missing. Mind filling that in?", icon="🧑")
        st.stop()

    if not streamlit_version:
        st.error("Please select the Streamlit version from the video.", icon="🎬")
        st.stop()

    if not compliance:
        st.error("Please tick to agree to the terms and conditions!", icon="📜")
        st.stop()

    with st.spinner("Hold tight, validating your email..."):
        is_email_valid, email_error_message = verify_email(email)
        if is_email_valid:
            data = {
                "email": email,
                "name": name,
                "streamlit_version": streamlit_version,
            }
            if send_data_via_webhook(data):
                st.success("Boom! You’re in the running 🎉 Good luck!", icon="🚀")
                st.balloons()
            else:
                st.error(
                    "Something went wonky on our end. Mind giving it another shot?",
                    icon="🤔",
                )
        else:
            st.error(email_error_message, icon="🧐")
