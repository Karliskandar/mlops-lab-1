import os

import requests
import streamlit as st


INFERENCE_URL = os.environ.get(
    "INFERENCE_URL",
    "http://127.0.0.1:8000",
)


st.title("Food-11 classifier")

uploaded = st.file_uploader(
    "Upload a food image",
    type=["jpg", "jpeg", "png"],
)

if uploaded is not None:
    st.image(uploaded, width=300)

    files = {
        "file": (
            uploaded.name,
            uploaded.getvalue(),
            uploaded.type,
        )
    }

    response = requests.post(
        f"{INFERENCE_URL}/predict",
        files=files,
    )

    if response.ok:
        result = response.json()

        st.write(
            f"**Prediction:** "
            f"{result['category']} "
            f"({result['confidence']:.1%})"
        )

    else:
        st.error(
            f"Inference service returned "
            f"{response.status_code}: "
            f"{response.text}"
        )