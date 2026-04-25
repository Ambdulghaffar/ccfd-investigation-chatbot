# Plan de Développement : Chatbot d'Investigation Anti-Fraude

**Étudiant :** Ambdulghaffar Ahamadi  
**Projet choisi :** Projet 4 - Chatbot d'Investigation : Dialogue LLM  

---

## Introduction
Ce document retrace la chronologie de développement du projet de Chatbot d'Investigation CCFD (Credit Card Fraud Detection). Le projet a suivi une approche agile sur 4 semaines, alternant entre l'ingénierie des données sur Kaggle et le déploiement applicatif via Streamlit. L'objectif principal était de coupler un socle statistique robuste (Machine Learning) à une intelligence cognitive (LLM Llama-3) pour transformer la détection de fraude en investigation interactive.

---

## Semaine 1 : Pipeline de Données Hybride & Context Engineering
**Objectif :** Unifier les sources de données et établir un ancrage probabiliste objectif.

### Tâche 1 : Ingestion et Qualité (Kaggle)
*   Extraction et fusion des datasets *PaySim* (transactions mobiles) et *ULB* (carte bancaire).
*   Vérifications de qualité : suppression des doublons (1081 détectés), vérification des valeurs nulles et des montants négatifs.
*   Division Train/Test (80-20) stratifiée avec verrouillage du *Test Set* pour l'évaluation finale.

### Tâche 2 : Scoring Baseline & Calibration
*   Implémentation du calcul de **Score de Risque Baseline** (0 à 1) calculé AVANT l'appel au LLM.
*   Calibration qualitative des seuils : **LOW** (<0.4), **MEDIUM** (0.4-0.7), et **HIGH** (≥ 0.7).
*   Validation de la cohérence : les fraudes réelles affichent un score moyen de 0.76 contre 0.31 pour les transactions légitimes.

### Tâche 3 : Moteur de Traduction "Context Translator"
*   Développement du *Context Translator* universel transformant les données brutes (V1-V28 pour ULB, balances pour PaySim) en récits narratifs structurés.
*   Injection automatique du score de risque dans le prompt pour guider le raisonnement du modèle.

---

## Semaine 2 : Architecture Cognitive & Classes d'Objets
**Objectif :** Définir les briques logicielles et l'intelligence de l'agent.

### Tâche 1 : Modélisation Orientée Objet (src/)
*   Classe `ChatHistory` : Gestion de la mémoire de travail et cycle de vie des questions.
*   Classe `ContextManager` : Maintien de l'état global et des métadonnées de l'enquête.
*   Intégration de la librairie JSON pour forcer le LLM à produire des réponses structurées (Status, Confiance, Justification).

### Tâche 2 : Intégration API LLM (Groq)
*   Connexion au client *Groq Cloud* pour exploiter le modèle **Llama-3-70B**.
*   Optimisation de la latence via l'infrastructure LPU pour garantir une interactivité fluide.

### Tâche 3 : Développement des "Tools" d'Investigation
*   Simulation d'outils externes (Géolocalisation, Historique, Analyse Marchand).
*   Mécanisme de *Tool Calling* simplifié permettant au bot de "penser" avant de poser une question au client.

---

## Semaine 3 : Moteur "Self-Play", Production & Métriques ML
**Objectif :** Mise à l'épreuve du système et évaluation scientifique massive.

### Tâche 1 : Simulateur de Client Robuste
*   Création d'un simulateur *Rule-Based* répondant aux questions du bot selon la "Vérité Terrain" (is_fraud) pour éviter les hallucinations circulaires.
*   Configuration des profils : Fraudeur agressif/pressé vs Client légitime précis/calme.

### Tâche 2 : Production Massive (30 Investigations)
*   Exécution automatisée de 30 enquêtes complètes (15 fraudes / 15 légitimes) couvrant tous les niveaux de risque.
*   Sauvegarde des transcriptions au format JSON pour analyse approfondie.

### Tâche 3 : Analyse Statistique & Visualisation (Graphviz)
*   Calcul des performances : Rappel exceptionnel de **93%** (détection quasi-totale des fraudes).
*   Génération automatique de la matrice de confusion et des courbes ROC/PR via *Matplotlib/Seaborn*.
*   Modélisation du workflow global via *Graphviz* pour documentation technique.

---

## Semaine 4 : Déploiement Streamlit & Sécurisation Finale
**Objectif :** Transformation du prototype en application Web utilisable par des agents de sécurité.

### Tâche 1 : Développement de l'Interface Web
*   Création de l'application `app.py` avec le framework *Streamlit*.
*   **Mode Live Investigation :** Chatbot interactif avec jauges de risque dynamiques et visualisation des outils utilisés.
*   **Dashboard Analytique :** Vue d'ensemble des 30 investigations passées pour supervision humaine.

### Tâche 2 : Sécurité et "Red Teaming"
*   Durcissement du *System Prompt* pour bloquer les tentatives de *Jailbreak*.
*   Protection contre les injections de prompt : le chatbot refuse de "sortir de son rôle" ou de donner des recettes de cuisine.

### Tâche 3 : Finalisation et Optimisation
*   Correction des bugs de boucle infinie (Perrot Bug).
*   Optimisation du design (Glassmorphism) et rédaction du rapport technique final de 46 pages.
