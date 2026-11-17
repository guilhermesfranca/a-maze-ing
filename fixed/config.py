"""Read and validate maze configuration files."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from mazegen import MazeError


@dataclass(frozen=True)
class Config:
    """Validated options required to build and display a maze."""

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int]


def load_config(filename: str) -> Config:
    """Parse KEY=VALUE options and reject missing or malformed values."""
    values: Dict[str, str] = {}
    allowed = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
               "PERFECT", "SEED"}
    with Path(filename).open(encoding="utf-8") as file:
        for number, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise MazeError(f"Linha {number}: esperado KEY=VALUE.")
            key, value = (part.strip() for part in line.split("=", 1))
            if key not in allowed:
                raise MazeError(f"Linha {number}: chave desconhecida {key}.")
            if key in values:
                raise MazeError(f"Linha {number}: chave repetida {key}.")
            if not value:
                raise MazeError(f"Linha {number}: {key} está vazia.")
            values[key] = value
    missing = allowed - {"SEED"} - values.keys()
    if missing:
        raise MazeError("Chaves obrigatórias ausentes: " + ", ".join(
            sorted(missing)))
    if values["PERFECT"].lower() not in ("true", "false"):
        raise MazeError("PERFECT deve ser True ou False.")

    def coordinate(key: str) -> Tuple[int, int]:
        """Parse one coordinate pair."""
        parts = values[key].split(",")
        if len(parts) != 2:
            raise MazeError(f"{key} deve ter o formato x,y.")
        return int(parts[0]), int(parts[1])

    try:
        return Config(
            width=int(values["WIDTH"]), height=int(values["HEIGHT"]),
            entry=coordinate("ENTRY"), exit=coordinate("EXIT"),
            output_file=values["OUTPUT_FILE"],
            perfect=values["PERFECT"].lower() == "true",
            seed=int(values["SEED"]) if "SEED" in values else None,
        )
    except ValueError as exc:
        if isinstance(exc, MazeError):
            raise
        raise MazeError("Dimensões, coordenadas e seed devem ser inteiros.") \
            from exc
