"""Bayesian Knowledge Tracing: one update step per observed answer."""

from app.domain.graph.graph import BktParams


def update(p_known: float, correct: bool, params: BktParams) -> float:
    """Posterior that the competency is known after one answer, then the learning transition."""
    if correct:
        evidence_known = p_known * (1 - params.p_slip)
        evidence_unknown = (1 - p_known) * params.p_guess
    else:
        evidence_known = p_known * params.p_slip
        evidence_unknown = (1 - p_known) * (1 - params.p_guess)
    posterior = evidence_known / (evidence_known + evidence_unknown)
    return posterior + (1 - posterior) * params.p_learn
