import streamlit as st
import google.generativeai as genai
import sqlite3
import json
import os
import re

st.set_page_config(page_title="Examen Bacalaureat", page_icon="🎓", layout="wide")

api_key = "AIzaSyCBK18DLTvpe4ZTpxPKhKFqUAi4dQbzJJU"

valid_model_name = "gemini-1.5-flash"
try:
    genai.configure(api_key=api_key)
    found_model = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            valid_model_name = m.name
            found_model = True
            break
    if found_model and "models/" in valid_model_name:
        valid_model_name = valid_model_name.replace("models/", "")
    model = genai.GenerativeModel(valid_model_name)
except Exception as e:
    st.error(f"Error: {e}")

DB_FILE = 'bac_exe.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercitii
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  materia TEXT, subiect TEXT, nr_ex TEXT,
                  enunt TEXT, rezolvare TEXT, tags TEXT, 
                  is_grila INTEGER, optiuni TEXT)''')
    conn.commit()
    conn.close()

def salveaza_exercitiu(data, materia, subiect, nr_ex):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    opts = ""
    is_grila = 0
    if data.get('optiuni'):
        opts = json.dumps(data['optiuni'])
        is_grila = 1
    c.execute("INSERT INTO exercitii (materia, subiect, nr_ex, enunt, rezolvare, tags, is_grila, optiuni) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (materia, subiect, nr_ex, data['enunt'], data['rezolvare'], data['tags'], is_grila, opts))
    conn.commit()
    conn.close()

init_db()

if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None
if 'show_hint' not in st.session_state:
    st.session_state.show_hint = False
if 'show_sol' not in st.session_state:
    st.session_state.show_sol = False

with st.sidebar:
    st.header("Configurare Examen")
    
    materia = st.selectbox("Materia", ["Matematica", "Informatica"])
    
    if materia == "Matematica":
        profil = st.selectbox("Profil", ["M1 (Mate-Info)", "M2 (Stiintele Naturii)", "M3 (Tehnologic)"])
        subiect_selectat = st.selectbox("Subiectul", ["Subiectul I", "Subiectul II", "Subiectul III"])
    else:
        profil = "Intensiv Informatica"
        subiect_selectat = st.selectbox("Subiectul", ["Subiectul I", "Subiectul II", "Subiectul III"])

    nr_ex = "1"
    is_grila_mode = False
    context_specific = ""

    if materia == "Matematica":
        if subiect_selectat == "Subiectul I":
            nr_ex = st.selectbox("Exercitiul", ["Exercitiul 1", "Exercitiul 2", "Exercitiul 3", "Exercitiul 4", "Exercitiul 5"])
            is_grila_mode = True
            context_specific = "Genereaza o problema scurta tip grila."
            
        elif subiect_selectat == "Subiectul II":
            nr_ex = st.selectbox("Exercitiul", ["Exercitiul 1 (Matrice/Sisteme)", "Exercitiul 2 (Polinoame/Legi)"])
            is_grila_mode = False
            context_specific = "Genereaza un context matematic principal, urmat obligatoriu de 3 subpuncte: a), b) si c). NU este grila."
            
        elif subiect_selectat == "Subiectul III":
            nr_ex = st.selectbox("Exercitiul", ["Exercitiul 1 (Derivate/Functii)", "Exercitiul 2 (Integrale)"])
            is_grila_mode = False
            context_specific = "Genereaza o functie principala, urmata obligatoriu de 3 subpuncte: a), b) si c). NU este grila."

    else: 
        if subiect_selectat == "Subiectul I":
            nr_ex = st.selectbox("Exercitiul", ["Exercitiul 1", "Exercitiul 2", "Exercitiul 3", "Exercitiul 4", "Exercitiul 5"])
            is_grila_mode = True
            context_specific = "Problema grila C++ (expresii, grafuri, structuri)."
            
        elif subiect_selectat == "Subiectul II":
            nr_ex_raw = st.selectbox("Exercitiul", ["Exercitiul 1 (Pseudocod)", "Exercitiul 2 (Structuri)", "Exercitiul 3 (Grafuri/Siruri)"])
            nr_ex = nr_ex_raw
            is_grila_mode = False
            
            if "Exercitiul 1" in nr_ex_raw:
                context_specific = "Genereaza un algoritm in pseudocod. Cere 4 subpuncte: a) Afisare, b) Valori intrare, c) Cod C++, d) Algoritm echivalent."
            else:
                context_specific = "Problema structura date / siruri. Fara subpuncte complexe."

        elif subiect_selectat == "Subiectul III":
            nr_ex = st.selectbox("Exercitiul", ["Exercitiul 1 (Subprograme)", "Exercitiul 2 (Tablouri)", "Exercitiul 3 (Fisiere/Eficienta)"])
            is_grila_mode = False
            context_specific = "Cerinta clara de scriere a unui program C++ sau functie."

    dificultate = st.slider("Dificultate", 1, 10, 5)
    
    st.markdown("---")
    
    if st.button("Generate", type="primary"):
        st.session_state.show_hint = False
        st.session_state.show_sol = False
        st.session_state.current_problem = None
        
        with st.spinner('Loading...'):
            try:
                tip = "GRILA" if is_grila_mode else "CLASIC"
                
                prompt = f"""
                Esti profesor de Bacalaureat. Genereaza: {materia}, {profil}, {subiect_selectat}, {nr_ex}.
                Dificultate: {dificultate}/10. Format: {tip}.
                Context: {context_specific}
                
                REGULA CRITICA JSON:
                1. Foloseste DOAR JSON valid.
                2. PENTRU FORMULE LATEX, FOLOSESTE DUBLU BACKSLASH: "f(x) \\\\in \\\\mathbb{{R}}"
                
                Raspunde strict JSON:
                {{
                    "enunt": "Enunt complet (LaTeX escaped \\\\).",
                    "optiuni": {{"A":"..","B":"..","C":"..","D":".."}} (sau null),
                    "raspuns_corect": "...",
                    "hint": "...",
                    "rezolvare": "...",
                    "tags": "..."
                }}
                """
                
                response = model.generate_content(prompt)
                text_clean = response.text.replace("```json", "").replace("```", "").strip()
                
                try:
                    data = json.loads(text_clean)
                except json.JSONDecodeError:
                    text_safe = text_clean.replace("\\", "\\\\") 
                    try:
                        data = json.loads(text_safe)
                    except:
                        st.error("Format error. Please try again.")
                        data = None

                if data:
                    st.session_state.current_problem = data
                    st.session_state.is_grila = is_grila_mode
                
            except Exception as e:
                st.error(f"Error: {e}")

st.title("Examen Bacalaureat")

if st.session_state.current_problem:
    prob = st.session_state.current_problem
    
    st.caption(f" {materia} > {subiect_selectat} > {nr_ex}")
    st.subheader("Enunt:")
    st.markdown(prob.get('enunt', 'Error'))
    
    if st.session_state.get('is_grila', False) and prob.get('optiuni'):
        opts = prob['optiuni']
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"A. {opts.get('A', '-')}")
            st.info(f"C. {opts.get('C', '-')}")
        with c2:
            st.info(f"B. {opts.get('B', '-')}")
            st.info(f"D. {opts.get('D', '-')}")

    st.markdown("---")
    
    b1, b2, b3 = st.columns(3)
    if b1.button("Hint"): st.session_state.show_hint = not st.session_state.show_hint
    if b2.button("Result"): st.session_state.show_sol = not st.session_state.show_sol
    if b3.button("Save"):
        salveaza_exercitiu(prob, materia, subiect_selectat, nr_ex)
        st.toast("Saved!", icon="✅")

    if st.session_state.show_hint: st.warning(f"Hint: {prob.get('hint')}")
    if st.session_state.show_sol: 
        st.success("Rezolvare:")
        st.markdown(prob.get('rezolvare', ''))

else:
    st.info("Selecteaza setarile din stanga si apasa Generate.")
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            nr = conn.cursor().execute("SELECT COUNT(*) FROM exercitii").fetchone()[0]
            st.markdown(f"📊 Probleme salvate local: **{nr}**")
            conn.close()
        except: pass