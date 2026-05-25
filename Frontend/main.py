import json
from typing import Any

import requests
import streamlit as st


DEFAULT_API_URL = "http://127.0.0.1:8000"


def init_state() -> None:
    if "api_url" not in st.session_state:
        st.session_state.api_url = DEFAULT_API_URL
    if "session" not in st.session_state:
        st.session_state.session = requests.Session()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "analyst_chat" not in st.session_state:
        st.session_state.analyst_chat = []


def api_url() -> str:
    return st.session_state.api_url.rstrip("/")


def request_json(method: str, path: str, **kwargs: Any) -> tuple[bool, dict[str, Any]]:
    url = f"{api_url()}{path}"
    try:
        response = st.session_state.session.request(method, url, timeout=60, **kwargs)
    except requests.RequestException as exc:
        return False, {"error": f"Could not reach backend: {exc}"}

    try:
        data = response.json()
    except ValueError:
        data = {"error": response.text or "Backend returned an empty response"}

    if response.ok:
        return True, data

    message = data.get("detail") or data.get("message") or data.get("error")
    return False, {"error": message or f"Request failed with HTTP {response.status_code}", "response": data}


def show_response_error(data: dict[str, Any]) -> None:
    st.error(data.get("error", "Request failed"))
    if "response" in data:
        with st.expander("Response details"):
            st.json(data["response"])


def sign_in_user(user: dict[str, Any] | None) -> None:
    st.session_state.logged_in = True
    st.session_state.user = user or {}


def sign_out() -> None:
    st.session_state.session = requests.Session()
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.analyst_chat = []
    st.success("Signed out.")
    st.rerun()


def render_auth_forms() -> None:
    login_tab, signup_tab = st.tabs(["Login", "Signup"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            ok, data = request_json(
                "POST",
                "/auth/login",
                json={"email": email, "password": password},
            )
            if ok and data.get("success"):
                sign_in_user(data.get("user"))
                st.success("Logged in successfully.")
                st.rerun()
            else:
                show_response_error(data)

    with signup_tab:
        with st.form("signup_form"):
            name = st.text_input("Name", key="signup_name")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_submitted = st.form_submit_button("Create account", use_container_width=True)

        if signup_submitted:
            ok, data = request_json(
                "POST",
                "/auth/signup",
                json={
                    "name": name,
                    "email": signup_email,
                    "password": signup_password,
                },
            )
            if not ok or not data.get("success"):
                show_response_error(data)
                return

            login_ok, login_data = request_json(
                "POST",
                "/auth/login",
                json={"email": signup_email, "password": signup_password},
            )
            if login_ok and login_data.get("success"):
                sign_in_user(login_data.get("user"))
                st.success("Account created and logged in successfully.")
                st.rerun()
            else:
                st.success("Account created. Please log in.")
                show_response_error(login_data)


def render_connection_bar() -> None:
    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 1, 2])
        with col1:
            st.session_state.api_url = st.text_input(
                "Backend API URL",
                value=st.session_state.api_url,
            )
        with col2:
            st.write("")
            st.write("")
            health_clicked = st.button("Health check", use_container_width=True)
        with col3:
            if st.session_state.logged_in:
                user = st.session_state.user or {}
                st.caption("Signed in as")
                st.write(f"**{user.get('name', 'User')}**")
                if user.get("email"):
                    st.caption(user["email"])
                if st.button("Sign out", use_container_width=True):
                    sign_out()
            else:
                st.caption("Account")
                st.write("Login or signup below to continue.")

        if health_clicked:
            ok, data = request_json("GET", "/")
            if ok:
                st.success(data.get("message", "Backend is healthy."))
                with st.expander("Health response"):
                    st.json(data)
            else:
                show_response_error(data)


def render_data_analyst_chat() -> None:
    left, right = st.columns([1, 5])
    with left:
        if st.button("New Chat", use_container_width=True):
            st.session_state.analyst_chat = []
            st.rerun()
    with right:
        st.caption("Ask questions about your retail data.")

    for message in st.session_state.analyst_chat:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and message.get("routes"):
                routes = ", ".join(str(route) for route in message["routes"])
                st.caption(f"Routes: {routes}")

    prompt = st.chat_input("Message the data analyst")
    if not prompt:
        return

    st.session_state.analyst_chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    history = [
        {"role": item["role"], "content": item["content"]}
        for item in st.session_state.analyst_chat[-7:-1]
    ][-6:]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ok, data = request_json(
                "POST",
                "/data-analyst/chat",
                json={"query": prompt, "history": history},
            )

        if ok and data.get("success", True):
            answer = data.get("answer", "")
            routes = data.get("routes") or []
            st.write(answer)
            if routes:
                st.caption(f"Routes: {', '.join(str(route) for route in routes)}")
            st.session_state.analyst_chat.append(
                {"role": "assistant", "content": answer, "routes": routes}
            )
        else:
            error = data.get("error", "The analyst could not answer that request.")
            st.error(error)
            st.session_state.analyst_chat.append(
                {"role": "assistant", "content": error, "routes": []}
            )


def render_forecast() -> None:
    with st.form("forecast_form"):
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", step=1, value=1)
            profit = st.number_input("Profit", value=0.0)
            returns = st.number_input("Returns", step=1, value=0)
            order_year = st.number_input("Order year", step=1, value=2026)
        with col2:
            order_month = st.number_input("Order month", min_value=1, max_value=12, step=1, value=1)
            order_day = st.number_input("Order day", min_value=1, max_value=31, step=1, value=1)
            profit_margin = st.number_input("Profit margin", value=0.0)
            shipping_days = st.number_input("Shipping days", min_value=0, step=1, value=0)

        submitted = st.form_submit_button("Run forecast")

    if submitted:
        payload = {
            "quantity": int(quantity),
            "profit": float(profit),
            "returns": int(returns),
            "order_year": int(order_year),
            "order_month": int(order_month),
            "order_day": int(order_day),
            "profit_margin": float(profit_margin),
            "shipping_days": int(shipping_days),
        }
        ok, data = request_json("POST", "/ml-expert/forecast", json=payload)
        if ok and data.get("success", True):
            st.metric("Prediction", data.get("prediction", "N/A"))
            st.write(data.get("answer", ""))
        else:
            show_response_error(data)


def render_anomaly_detection() -> None:
    with st.form("anomaly_form"):
        col1, col2 = st.columns(2)
        with col1:
            sales = st.number_input("Sales", value=0.0)
            profit = st.number_input("Profit", value=0.0, key="anomaly_profit")
            quantity = st.number_input("Quantity", step=1, value=1, key="anomaly_quantity")
        with col2:
            profit_margin = st.number_input("Profit margin", value=0.0, key="anomaly_profit_margin")
            shipping_days = st.number_input("Shipping days", min_value=0, step=1, value=0, key="anomaly_shipping_days")

        submitted = st.form_submit_button("Detect anomaly")

    if submitted:
        payload = {
            "sales": float(sales),
            "profit": float(profit),
            "quantity": int(quantity),
            "profit_margin": float(profit_margin),
            "shipping_days": int(shipping_days),
        }
        ok, data = request_json("POST", "/ml-expert/anomaly", json=payload)
        if ok and data.get("success", True):
            st.metric("Anomaly status", data.get("anomaly_status", "N/A"))
            st.write(data.get("answer", ""))
        else:
            show_response_error(data)


def render_document_search() -> None:
    with st.form("document_search_form"):
        query = st.text_area("Query", height=140)
        submitted = st.form_submit_button("Search documents")

    if submitted:
        if not query.strip():
            st.warning("Enter a search query.")
            return

        ok, data = request_json(
            "POST",
            "/document-assistant/search",
            json={"query": query.strip()},
        )
        if ok and data.get("success", True):
            st.subheader("Answer")
            st.write(data.get("answer", ""))
            sources = data.get("sources") or []
            if sources:
                st.subheader("Sources")
                for source in sources:
                    st.write(f"- {source}")
        else:
            show_response_error(data)


def render_document_upload() -> None:
    uploaded_file = st.file_uploader("Upload document", type=["pdf", "txt", "docx", "csv"])
    if st.button("Upload", disabled=uploaded_file is None):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "application/octet-stream",
            )
        }
        with st.spinner("Uploading and ingesting document..."):
            ok, data = request_json(
                "POST",
                "/data-ingestion/upload-documents",
                files=files,
            )

        if ok and data.get("success", True):
            st.success("Upload complete.")
            st.json(data)
        else:
            st.error("Upload failed.")
            st.json(data)


def render_app() -> None:
    tabs = st.tabs(
        [
            "Data Analyst Chat",
            "Forecast",
            "Anomaly Detection",
            "Document Search",
            "Document Upload",
        ]
    )

    with tabs[0]:
        render_data_analyst_chat()
    with tabs[1]:
        render_forecast()
    with tabs[2]:
        render_anomaly_detection()
    with tabs[3]:
        render_document_search()
    with tabs[4]:
        render_document_upload()


def main() -> None:
    st.set_page_config(
        page_title="IntelliRetail AI",
        page_icon="chart",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_state()
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none;
        }

        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 1rem;
            left: 1rem;
            right: 1rem;
            z-index: 999;
            max-width: 1120px;
            margin-left: auto;
            margin-right: auto;
            background: rgb(14, 17, 23);
            padding-top: 0.5rem;
        }

        section.main > div {
            padding-bottom: 6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("IntelliRetail AI Dashboard")
    render_connection_bar()

    if st.session_state.logged_in:
        render_app()
    else:
        st.info("Login or create an account to use the protected app screens.")
        render_auth_forms()


if __name__ == "__main__":
    main()
