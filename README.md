# 🛡️ CCFD Investigation Chatbot — Dialogue LLM pour la Détection de Fraude

> **Projet Master S3 · Sécurité des transactions éléctroniqus et détections de fraudes**  
> Context Engineering + LLM pour la détection de fraude cartes bancaires  
> *Chatbot d'investigation CCFD : dialogue intelligent + contexte dynamique*

---

## 📌 Problématique

Comment créer un LLM conversationnel qui, en dialogue interactif, utilise un **contexte dynamique** pour poser les bonnes questions et converger vers une décision de fraude/légitime ?

---

## 🏗️ Architecture du Projet

```
projet_chatbot_antifraude/
│
├── data/                              # Datasets (générés sur Kaggle - Semaine 1)
│   ├── context_examples_with_risk.csv # 10 transactions exemples (interface)
│   ├── test_ulb_LOCKED_with_risk.csv  # Jeu de test ULB (non modifié)
│   ├── test_paysim_LOCKED_with_risk.csv  # Jeu de test PaySim (non modifié)
│   └── metadata.json                  # Métadonnées des datasets
│
├── src/                               # Backend Python
│   ├── llm_client.py                  # Client Groq API (Llama 3.3 70B)
│   ├── context_manager.py             # Gestion du contexte dynamique
│   ├── chatbot.py                     # Moteur d'investigation (auto + interactif)
│   └── chat_history.py                # Gestion de l'historique de conversation
│
├── results/
│   ├── semaine2/                      # 3 transcriptions de test (Semaine 2)
│   └── semaine3/                      # 30 investigations + métriques (Semaine 3)
│
├── web_app/
│   └── app.py                         # Interface Streamlit complète (Semaine 4)
│
├── notebook96abd24326.ipynb           # Notebook Kaggle (Semaines 1-3)
├── .env.example                       # Modèle pour la configuration
├── requirements.txt                   # Dépendances Python
└── README.md
```

---

## 🔑 Fonctionnalités Clés

### 🧠 Contexte Dynamique
À chaque tour de dialogue, le système accumule et enrichit le contexte :
- **Transaction originale** (montant, source, score de risque calculé)
- **Questions/réponses antérieures** (historique complet envoyé au LLM)
- **Signaux fraude** détectés au fil de la conversation
- **Signaux légitimes** recueillis pour équilibrer l'analyse
- **Confiance** mise à jour à chaque étape (0 → 100%)

### 💬 Tab 1 — Investigation Live (Mode Interactif)
1. Sélectionnez une transaction dans la barre latérale (filtre par source/risque)
2. Cliquez sur **"🚀 Lancer l'Investigation"**
3. L'analyste IA pose des questions ciblées une par une
4. Vous répondez librement en langage naturel
5. Le mini-tableau de bord de gauche se met à jour en temps réel :
   - Jauge de confiance fraude
   - Signaux fraude accumulés (badges rouges)
   - Signaux légitimes accumulés (badges verts)
6. Après **6 questions**, le LLM rend son **verdict final** avec justification

### 📊 Tab 2 — Analyse & Métriques (Semaine 3)
- **6 KPI** : Accuracy, Precision, Recall, F1, Questions moyennes, Confiance moyenne
- **Matrice de confusion** interactive (Plotly)
- **Histogramme** de confiance pour chacune des 30 investigations
- **Donut chart** de répartition des verdicts (VP/FP/VN/FN)
- **Explorateur de transcriptions** : parcourir les 30 dialogues complets de Semaine 3

---

## ⚙️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| LLM | Llama 3.3 70B Versatile (via Groq API) |
| Interface | Streamlit (Python) |
| Visualisations | Plotly |
| Datasets | Credit Card Fraud Detection ULB + PaySim |
| Scoring risque | Calcul de features custom |
| Historique | Liste de messages (format OpenAI-compatible) |

---

## 🚀 Installation & Lancement

### 1. Cloner le repo
```bash
git clone https://github.com/Ambdulghaffar/ccfd-investigation-chatbot.git
cd ccfd-investigation-chatbot
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer la clé API Groq
Créez un fichier `.env` à la racine du projet :
```env
GROQ_API_KEY=gsk_votre_cle_ici
LLM_MODEL=llama-3.3-70b-versatile
MAX_QUESTIONS=6
```
> 🔗 Obtenir une clé gratuite sur [console.groq.com](https://console.groq.com)

### 4. Lancer l'interface
```bash
streamlit run web_app/app.py
```
Puis ouvrir dans le navigateur : **http://localhost:8501**

---

## 📈 Résultats Semaine 3 (30 Investigations)

| Métrique | Valeur |
|----------|--------|
| Accuracy | 50% |
| Precision | 50% |
| **Recall** | **100%** |
| F1 Score | 0.67 |
| Vrais Positifs (fraudes détectées) | 15/15 |
| Faux Positifs (légitimes mal classés) | 15/15 |
| Questions moyennes par investigation | 6 |
| Confiance moyenne | 69% |

> Le recall de 100% signifie que **toutes les fraudes réelles ont été détectées**. Le modèle adopte une stratégie prudente (biais vers FRAUDE).

---

## 📅 Plan du Projet par Semaines

| Semaine | Travail | Status |
|---------|---------|--------|
| **S1** | Chargement et fusion des datasets ULB + PaySim, calcul du score de risque | ✅ |
| **S2** | Développement du moteur chatbot, 3 premières transcriptions test | ✅ |
| **S3** | 30 investigations automatiques, calcul des métriques de convergence | ✅ |
| **S4** | Interface graphique Streamlit (Investigation Live + Dashboard métriques) | ✅ |

---

## 🗂️ Datasets

- **Credit Card Fraud Detection (ULB)** — [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)  
  284 807 transactions réelles anonymisées (PCA), 0.17% de fraudes
  
- **Synthetic Financial Datasets (PaySim)** — [Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1)  
  6 362 620 transactions synthétiques mobiles, 0.13% de fraudes

---

## � Notebook Kaggle (Semaines 1–3)

Le notebook complet (pipeline de données, scoring de risque, moteur chatbot, 30 investigations) est disponible sur Kaggle :

🔗 [Voir le notebook sur Kaggle](https://www.kaggle.com/code/ambdulghaffrar/notebook96abd24326/notebook?scriptVersionId=301265852)

---

## �👤 Auteur

Projet Master S3 · Sécurité des transactions éléctroniques et détection de fraudes  
*Context Engineering + LLM pour la Détection de Fraude Cartes Bancaires*
