from . import reinhard_simple
from . import ward
from . import reinhard


def apply_tone_reproduction(buffer, operator: str | None, Ldmax: float, config: dict):
    if operator is None:
        operator = "reinhard_simple"
    
    if operator == "reinhard":
        key = config.get("key", 0.18)
        return reinhard.apply(buffer, Ldmax, key)

    if operator == "reinhard_simple":
        return reinhard_simple.apply(buffer, Ldmax)

    if operator == "ward":
        return ward.apply(buffer, Ldmax)

    raise ValueError(f"Unknown tone reproduction operator: {operator}")