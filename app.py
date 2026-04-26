import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from gtts import gTTS

# --- 1. SETUP ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

if "lms_db" not in st.session_state:
    st.session_state.lms_db = {
        "Matematika": "",
        "Bahasa Indonesia": "",
        "IPA": "",
        "Sejarah": ""
    }

# --- 2. CUSTOM UI (ANTI BENTROK TEMA) ---
st.set_page_config(page_title="LMS AksaraKestra", page_icon="🏫", layout="wide")

st.markdown("""
<style>
    /* 1. Latar Belakang Utama */
    .stApp {
        background-color: #F3F4F6 !important;
    }

    /* 2. Paksa WARNA TEKS UTAMA menjadi Gelap agar selalu terbaca */
    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1F2937 !important;
    }

    /* 3. Paksa Warna Judul menjadi Merah Marun */
    h1, h2, h3, h1 span, h2 span, h3 span {
        color: #800000 !important;
    }
    
    /* Subjudul */
    .center-text {
        text-align: center;
        color: #4B5563 !important;
        margin-bottom: 2rem;
    }

    /* 4. Sidebar Tetap Marun & Teks Putih */
    [data-testid="stSidebar"] {
        background-color: #800000 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
        color: white !important;
    }

    /* 5. Layout Card untuk area tengah */
    .block-container {
        background-color: #FFFFFF !important;
        padding: 3rem 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* 6. Styling Input & Text Area */
    div[data-baseweb="select"] > div, .stTextArea textarea, .stTextInput input {
        border-radius: 0.5rem !important;
        border: 1px solid #D1D5DB !important;
        background-color: #F9FAFB !important;
        color: #1F2937 !important;
    }
    
    /* 7. Tombol */
    .stButton > button {
        background-color: #800000 !important;
        color: white !important;
        border-radius: 0.5rem !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #990000 !important;
    }

    /* 8. Box Materi & AI */
    .materi-box {
        background-color: #fdf2f2 !important;
        padding: 25px;
        border-left: 5px solid #800000;
        border-radius: 0.5rem;
        margin-bottom: 20px;
    }
    .ai-box {
        background-color: white !important; 
        padding: 20px; 
        border: 1px solid #800000; 
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>🏫 LMS AKSARAKESTRA</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>Sistem Informasi Pembelajaran Terintegrasi AI</p>", unsafe_allow_html=True)
st.divider()

# Sidebar
st.sidebar.markdown("<h2 style='color: white !important;'>MENU UTAMA</h2>", unsafe_allow_html=True)
role = st.sidebar.radio("Masuk Sebagai:", ["👨‍🏫 Guru (Upload Materi)", "👨‍🎓 Siswa (Belajar)"])
st.sidebar.divider()
st.sidebar.caption("UTS Gen-AI © 2026")

# --- 3. LOGIKA GURU ---
if role == "👨‍🏫 Guru (Upload Materi)":
    st.markdown("<h3>Upload Materi Pelajaran</h3>", unsafe_allow_html=True)
    
    mapel_pilihan = st.selectbox("Pilih Mata Pelajaran:", list(st.session_state.lms_db.keys()))
    
    isi_materi = st.text_area(f"Input Materi {mapel_pilihan}:", 
                            value=st.session_state.lms_db[mapel_pilihan], 
                            height=300,
                            placeholder="Ketikkan materi pelajaran di sini...")
    
    if st.button("🚀 Publikasikan Materi"):
        if isi_materi.strip():
            st.session_state.lms_db[mapel_pilihan] = isi_materi
            st.success(f"✅ Berhasil: Materi {mapel_pilihan} telah diperbarui!")
        else:
            st.warning("⚠️ Mohon isi materi terlebih dahulu sebelum dipublikasikan.")

# --- 4. LOGIKA SISWA ---
else:
    mapel_belajar = st.sidebar.selectbox("Pilih Mata Pelajaran:", list(st.session_state.lms_db.keys()))
    materi_saat_ini = st.session_state.lms_db[mapel_belajar]
    
    if not materi_saat_ini:
        st.info(f"📚 Saat ini belum ada materi untuk **{mapel_belajar}**. Silakan tunggu Guru mengunggah materi.")
    else:
        # TAMPILAN MATERI
        st.markdown(f"<h2>📖 Materi: {mapel_belajar}</h2>", unsafe_allow_html=True)
        st.markdown(f"""<div class="materi-box">{materi_saat_ini}</div>""", unsafe_allow_html=True)
        
        st.divider()
        
        # TAMPILAN AI
        st.markdown("<h3>💬 Tanya Asisten AI (Smart Tutor)</h3>", unsafe_allow_html=True)
        pertanyaan = st.text_input("Ketik pertanyaanmu seputar materi di atas...", placeholder="Contoh: Apa kesimpulan materi ini?")
        
        if st.button("Tanya AI Sekarang"):
            if pertanyaan:
                try:
                    # Auto-select model logic
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    target = next((m for m in models if 'flash' in m), models[0])
                    model_ai = genai.GenerativeModel(target)
                    
                    prompt = f"""
                    Anda adalah tutor untuk mapel {mapel_belajar}. 
                    JAWAB HANYA berdasarkan materi ini:
                    {materi_saat_ini}
                    
                    Jika tidak ada di teks, jawab: 'Maaf, materi tersebut tidak ditemukan dalam catatan Guru.'
                    """
                    
                    with st.spinner("AI sedang memikirkan jawaban..."):
                        response = model_ai.generate_content(f"{prompt}\n\nPertanyaan: {pertanyaan}")
                        jawaban = response.text
                        
                        st.markdown(f"""
                        <div class="ai-box">
                            <b style="color: #800000;">🤖 Jawaban AI:</b><br><br>{jawaban}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # TTS (Audio)
                        tts = gTTS(text=jawaban, lang='id')
                        tts.save("audio.mp3")
                        st.audio("audio.mp3")
                        
                except Exception as e:
                    st.error(f"Koneksi terputus atau terjadi kesalahan: {e}")
            else:
                st.warning("Ketik dulu apa yang mau ditanyakan ya!")