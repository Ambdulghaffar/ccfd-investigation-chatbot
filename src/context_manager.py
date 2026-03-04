# src/context_manager.py

import time


class InvestigationState:
    """
    Gère l'état dynamique d'une investigation anti-fraude.
    Accumule les signaux, la confiance et le statut au fil du dialogue.
    """

    def __init__(self, transaction: dict):
        # --- Infos transaction ---
        self.transaction = transaction
        self.transaction_id = transaction.get("transaction_id", "INCONNU")
        self.amount = float(transaction.get("amount", 0))
        self.risk_score = float(transaction.get("risk_score", 0.5))
        self.risk_level = transaction.get("risk_level", "MEDIUM")
        self.source = transaction.get("source", "inconnu")
        self.is_fraud_truth = int(transaction.get("is_fraud", -1))
        self.context_text = transaction.get("context", "")

        # --- État investigation ---
        self.confidence: int = max(20, int(self.risk_score * 50))
        self.status: str = "INVESTIGATING"
        self.signals_fraud: list[str] = []
        self.signals_legit: list[str] = []
        self.nb_questions: int = 0
        self.start_time: float = time.time()

    # ------------------------------------------------------------------
    # Mise à jour depuis la réponse LLM
    # ------------------------------------------------------------------
    def update_from_llm(self, confidence: int, status: str,
                        new_signals_fraud: list, new_signals_legit: list):
        """Met à jour l'état à partir des données parsées du JSON LLM."""
        self.confidence = confidence
        self.status = status
        for s in new_signals_fraud:
            if s and s not in self.signals_fraud:
                self.signals_fraud.append(s)
        for s in new_signals_legit:
            if s and s not in self.signals_legit:
                self.signals_legit.append(s)

    # ------------------------------------------------------------------
    # Résumé texte injecté dans le contexte LLM
    # ------------------------------------------------------------------
    def get_summary(self) -> str:
        fraud_list = (
            "\n".join(f"  • {s}" for s in self.signals_fraud)
            if self.signals_fraud else "  • Aucun"
        )
        legit_list = (
            "\n".join(f"  • {s}" for s in self.signals_legit)
            if self.signals_legit else "  • Aucun"
        )
        return (
            f"\n=== ÉTAT INVESTIGATION ===\n"
            f"Transaction : {self.transaction_id}\n"
            f"Risque Initial : {self.risk_score:.3f} ({self.risk_level})\n"
            f"Questions : {self.nb_questions}\n"
            f"Confiance : {self.confidence}%\n"
            f"Statut : {self.status}\n\n"
            f"Signaux Fraude ({len(self.signals_fraud)}) :\n{fraud_list}\n\n"
            f"Signaux Légitime ({len(self.signals_legit)}) :\n{legit_list}\n"
        )

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------
    def get_duration(self) -> float:
        return time.time() - self.start_time

    @property
    def fraud_score(self) -> int:
        """Score fraude global (0-100) combinant risque initial + confiance LLM."""
        base = int(self.risk_score * 60)
        llm_contrib = int(self.confidence * 0.4)
        boost = min(20, len(self.signals_fraud) * 5)
        malus = min(15, len(self.signals_legit) * 5)
        return min(100, max(0, base + llm_contrib + boost - malus))
