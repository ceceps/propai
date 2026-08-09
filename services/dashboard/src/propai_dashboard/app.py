"""Agent console.

Talks to the API over HTTP rather than the database directly, so RBAC is
enforced in exactly one place. A dashboard with its own DB session would be a
second, divergent authorization surface.
"""

from __future__ import annotations

import os

import httpx
import streamlit as st

DEFAULT_API_BASE = "http://127.0.0.1:8000"
API_BASE = os.getenv("API_BASE_URL") or os.getenv("PUBLIC_BASE_URL") or DEFAULT_API_BASE

st.set_page_config(page_title="PropAI — Prolov", page_icon="🏠", layout="wide")


def api(path: str, token: str | None = None, **kwargs) -> httpx.Response:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.request(
        kwargs.pop("method", "GET"),
        f"{API_BASE}{path}",
        headers=headers,
        timeout=15.0,
        **kwargs,
    )


def login_form() -> None:
    st.subheader("Masuk / Sign in")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Sign in"):
            try:
                r = api("/auth/login", method="POST", json={"email": email, "password": password})
            except httpx.HTTPError as exc:
                st.error(f"Cannot reach API at {API_BASE}: {exc}")
                return
            if r.status_code == 200:
                st.session_state.update(auth=r.json())
                st.rerun()
            else:
                st.error("Incorrect email or password")


def listings_view(auth: dict) -> None:
    st.caption(f"{auth['full_name']} · {auth['role']}")
    if st.button("Sign out"):
        st.session_state.pop("auth")
        st.rerun()

    r = api("/properties", token=auth["access_token"])
    if r.status_code != 200:
        st.error(f"Could not load listings ({r.status_code})")
        return

    rows = r.json()
    st.metric("Listings visible to you", len(rows))
    for p in rows:
        with st.expander(f"{p['title']} — Rp {int(float(p['price'])):,}".replace(",", ".")):
            st.write(p["description"] or "_No description_")
            st.json(p["specs"], expanded=False)


st.title("PropAI")
st.caption("Prolov · Jawa Barat")

if "auth" not in st.session_state:
    login_form()
else:
    listings_view(st.session_state["auth"])
