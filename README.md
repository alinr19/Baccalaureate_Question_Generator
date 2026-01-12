# Generator de Subiecte Bacalaureat - AI Simulator

Un proiect educational inteligent bazat pe **Google Gemini AI**, conceput pentru a ajuta elevii sa se pregateasca pentru examenul de Bacalaureat (Matematica si Informatica).

Spre deosebire de culegerile traditionale cu intrebari statice, aceasta aplicatie genereaza **exercitii unice** in timp real, respectand strict structura si programa oficiala a examenului.

## Functionalitati Cheie

* **Generare Dinamica:** Problemele sunt create pe loc folosind modele de limbaj (LLM). Nu vei primi niciodata acelasi exercitiu de doua ori.
* **Structura Oficiala:**
    * **Matematica:** Suporta profilele M1, M2, M3. Acopera Subiectul I (Grile), Subiectul II (Algebra) si Subiectul III (Analiza).
    * **Informatica:** Acopera Subiectul I (Grile), Subiectul II (Pseudocod/Structuri) si Subiectul III (Scriere Cod C++).
* **Instrumente Inteligente de Invatare:**
    * **Sistem de Hint-uri:** Primesti un indiciu util fara a vedea raspunsul final.
    * **Rezolvari Complete:** Vizualizezi explicatii pas cu pas sau codul C++ complet.
* **Baza de Date Locala:** Salveaza problemele dificile sau interesante intr-o baza de date locala SQLite (`bac_exe.db`).
* **Interfata Curata:** Interfata prietenoasa, fara elemente inutile, cu controale clare: `Generate`, `Hint`, `Result`, `Save`.

## Tehnologii Utilizate

* **Python 3.10+**
* **Streamlit** (Interfata Frontend)
* **Google Gemini API** (Motorul de Inteligenta Artificiala)
* **SQLite3** (Stocare Date Locala)

## Instructiuni de Rulare

python -m streamlit run app.py

### 1. Instalare

Cloneaza repository-ul:
```bash
git clone [https://github.com/StoianRobertAlin/Baccalaureate_Question_Generator.git](https://github.com/StoianRobertAlin/Baccalaureate_Question_Generator.git)
cd Baccalaureate_Question_Generator
