"""
Reaction mechanism handling.

This module handles loading and parsing of chemical reaction mechanisms
from various formats (Cantera YAML, CHEMKIN, etc.).
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cantera as ct

from nanoparticle_simulator.chemistry.species import Species

logger = logging.getLogger(__name__)


@dataclass
class Reaction:
    """
    Representation of a chemical reaction.

    Attributes:
        index: Reaction index in the mechanism
        equation: String representation of the reaction equation
        rate_type: Type of rate expression (Arrhenius, falloff, etc.)
        reversible: Whether the reaction is reversible
        A: Pre-exponential factor
        b: Temperature exponent
        Ea: Activation energy in J/mol
    """

    index: int
    equation: str
    rate_type: str
    reversible: bool = True
    A: float = 0.0
    b: float = 0.0
    Ea: float = 0.0

    def __repr__(self) -> str:
        return f"Reaction({self.index}: {self.equation})"


@dataclass
class Mechanism:
    """
    Chemical reaction mechanism.

    Loads and manages a chemical kinetics mechanism, providing access
    to species and reaction data via Cantera.

    Attributes:
        name: Mechanism name
        source_file: Path to the mechanism file
        species: List of species in the mechanism
        reactions: List of reactions in the mechanism
        n_species: Number of species
        n_reactions: Number of reactions
    """

    name: str
    source_file: Optional[Path] = None
    species: list[Species] = field(default_factory=list)
    reactions: list[Reaction] = field(default_factory=list)
    _ct_solution: Optional[ct.Solution] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Load mechanism if source file is provided."""
        if self.source_file is not None:
            self.load(self.source_file)

    @property
    def n_species(self) -> int:
        """Return number of species."""
        return len(self.species)

    @property
    def n_reactions(self) -> int:
        """Return number of reactions."""
        return len(self.reactions)

    @property
    def ct_solution(self) -> Optional[ct.Solution]:
        """Return the underlying Cantera Solution object."""
        return self._ct_solution

    def load(self, filepath: Path | str) -> None:
        """
        Load mechanism from file.

        Supports Cantera YAML format and built-in mechanisms like 'gri30.yaml'.

        Args:
            filepath: Path to mechanism file or name of built-in mechanism
        """
        filepath = Path(filepath) if not isinstance(filepath, Path) else filepath

        # Check if it's a built-in mechanism
        builtin_mechanisms = ["gri30.yaml", "h2o2.yaml", "air.yaml"]
        is_builtin = filepath.name in builtin_mechanisms

        if not is_builtin and not filepath.exists():
            raise FileNotFoundError(f"Mechanism file not found: {filepath}")

        try:
            if is_builtin:
                self._ct_solution = ct.Solution(filepath.name)
                logger.info(f"Loaded built-in mechanism: {filepath.name}")
            else:
                self._ct_solution = ct.Solution(str(filepath))
                logger.info(f"Loaded mechanism from: {filepath}")

            self.source_file = filepath
            self._extract_species()
            self._extract_reactions()

        except Exception as e:
            logger.error(f"Failed to load mechanism: {e}")
            raise

    def _extract_species(self) -> None:
        """Extract species information from Cantera solution."""
        if self._ct_solution is None:
            return

        self.species = []
        for i, name in enumerate(self._ct_solution.species_names):
            ct_species = self._ct_solution.species(i)
            species = Species(
                name=name,
                mw=ct_species.molecular_weight / 1000.0,  # g/mol -> kg/mol
            )
            self.species.append(species)

    def _extract_reactions(self) -> None:
        """Extract reaction information from Cantera solution."""
        if self._ct_solution is None:
            return

        self.reactions = []
        for i in range(self._ct_solution.n_reactions):
            rxn = self._ct_solution.reaction(i)
            reaction = Reaction(
                index=i,
                equation=rxn.equation,
                rate_type=rxn.reaction_type,
                reversible=rxn.reversible,
            )
            self.reactions.append(reaction)

    def species_index(self, name: str) -> int:
        """
        Get index of a species by name.

        Args:
            name: Species name

        Returns:
            Species index

        Raises:
            ValueError: If species not found
        """
        if self._ct_solution is not None:
            return self._ct_solution.species_index(name)
        for i, s in enumerate(self.species):
            if s.name == name:
                return i
        raise ValueError(f"Species '{name}' not found in mechanism")

    def species_by_name(self, name: str) -> Species:
        """
        Get species by name.

        Args:
            name: Species name

        Returns:
            Species object

        Raises:
            ValueError: If species not found
        """
        idx = self.species_index(name)
        return self.species[idx]

    def __repr__(self) -> str:
        return f"Mechanism({self.name}, " f"species={self.n_species}, reactions={self.n_reactions})"
