import streamlit as st, requests, base64

IMAGE_API_URL = "http://127.0.0.1:8000/image_to_text"
TTS_API_URL = "http://127.0.0.1:7999/text_to_speech"

st.set_page_config(page_title="Image → Audio", layout="centered")
st.title("Image to Audio Converter")
st.markdown('### Please upload your image, press the "generate" button and an audio description of the field will be generated, alongside a written description.')

st.markdown("<style>.result-caption{font-size:1.25rem;line-height:1.6;}.block-container{padding-top:2rem;padding-bottom:3rem;}</style>", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("caption",""); ss.setdefault("audio_b64",""); ss.setdefault("current_file_sig",None); ss.setdefault("is_generating",False)

left, right = st.columns([1,1])
with left:
    uploaded_file = st.file_uploader("", type=["jpg","jpeg","png","webp"])
    new_sig = (uploaded_file.name, uploaded_file.size) if uploaded_file else None
    if new_sig != ss.current_file_sig: ss.current_file_sig = new_sig; ss.caption=""; ss.audio_b64=""; ss.is_generating=False

    generate = st.button("Generate Caption & Audio", type="primary", disabled=(uploaded_file is None))
    if generate and uploaded_file is not None:
        try:
            ss.is_generating = True
            with st.spinner("Captioning image…"):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), getattr(uploaded_file, "type", "application/octet-stream"))}
                cap_resp = requests.post(IMAGE_API_URL, files=files, timeout=120); cap_resp.raise_for_status()
                caption = (cap_resp.json().get("text") or "").strip()
                if not caption: st.error("Captioning returned empty text. Try another image.")
                ss.caption = caption
            if ss.caption:
                with st.spinner("Generating speech…"):
                    tts_resp = requests.post(TTS_API_URL, json={"text": ss.caption}, timeout=120); tts_resp.raise_for_status()
                    ss.audio_b64 = base64.b64encode(tts_resp.content).decode("utf-8")
        except requests.exceptions.Timeout: st.error("The request timed out. Try a smaller image or try again.")
        except requests.exceptions.RequestException as e: st.error(f"Network or server error: {e}")
        except Exception as e: st.error(f"Something went wrong: {e}")
        finally: ss.is_generating = False

    if ss.caption:
        st.subheader("Caption")
        st.markdown(f"<div class='result-caption'>{ss.caption}</div>", unsafe_allow_html=True)

    if ss.audio_b64 and not ss.is_generating and ss.current_file_sig is not None:
        st.markdown(f"<audio controls autoplay><source src='data:audio/wav;base64,{ss.audio_b64}' type='audio/wav'>Your browser does not support the audio element.</audio>", unsafe_allow_html=True)

with right:
    if uploaded_file is not None: st.image(uploaded_file, caption="Preview", width=320)
