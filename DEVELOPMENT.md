# Implementation Guide for Nano-Stochastic Model

## Overview

This document provides guidance for developers working with the nano-stochastic-model package, following the DEVGUIDE standards established in the parent project.

## Code Structure

### Core Modules

#### `src/population_balance.py` (Main)
- **Purpose**: Implements Gillespie's Direct Method for stochastic simulation
- **Key Classes**: `PopulationBalance`, `ParticleProperty`
- **Responsibilities**:
  - Track particle populations
  - Calculate propensity functions
  - Execute stochastic steps
  - Maintain simulation history
- **Testing**: `tests/test_population_balance.py` (40+ tests)

#### `src/particle_system.py` (Physics)
- **Purpose**: Implements physical particle processes
- **Key Classes**: `ParticleSystem`
- **Responsibilities**:
  - Nucleation, growth, coagulation, sintering mechanisms
  - Propensity calculations based on kinetics
  - Temperature and pressure effects
  - Unit conversions (diameter ↔ mass)
- **Testing**: `tests/test_particle_system.py` (50+ tests)

#### `src/utilities.py` (Helpers)
- **Purpose**: Utility functions for common calculations
- **Functions**:
  - Volume fraction calculations
  - Brownian motion physics
  - Collision frequency
  - Unit formatting
- **Testing**: `tests/test_utilities.py` (20+ tests)

#### `src/events.py` (Events)
- **Purpose**: Reaction event dataclass
- **Key Classes**: `ReactionEvent`
- **Usage**: Define reaction mechanisms for simulation

### Example Code

#### `examples/example_basic_simulation.py`
- Creates particles through nucleation
- Simulates surface growth
- Visualizes particle size distribution
- **Runtime**: ~2 seconds

#### `examples/example_gillespie_simulation.py`
- Full stochastic simulation with Gillespie algorithm
- Multiple reaction mechanisms
- Time-evolution tracking
- **Runtime**: ~10-30 seconds

## Development Workflow

### 1. Making Code Changes

**Follow DEVGUIDE standards:**

```bash
# 1. Create tests BEFORE code changes
pytest tests/ -v          # Baseline

# 2. Make code changes
# (edit src/*.py)

# 3. Run tests
pytest tests/ -v          # Should still pass

# 4. Check coverage
pytest --cov=src tests/   # Should be 80%+

# 5. Check naming conventions
python scripts/check_naming_conventions.py

# 6. Syntax check
python -m py_compile src/*.py
```

### 2. Adding New Features

**Example: Add a new reaction mechanism**

1. **Define in `particle_system.py`**:
   ```python
   def custom_reaction_propensity(self, ...):
       """Calculate propensity for custom reaction."""
       return rate

   def perform_custom_reaction(self, ...):
       """Execute custom reaction."""
       # Update particles
   ```

2. **Add unit tests in `tests/test_particle_system.py`**:
   ```python
   def test_custom_reaction_propensity(self):
       """Test custom reaction."""
       ps = ParticleSystem()
       propensity = ps.custom_reaction_propensity(...)
       assert propensity > 0.0
   ```

3. **Run full test suite**:
   ```bash
   pytest tests/ -v
   pytest --cov=src tests/
   ```

4. **Document in README.md** if user-facing

### 3. Fixing Bugs

**Per DEVGUIDE - check ALL layers**

- [ ] Identified where bug occurs (propensity calculation? particle update?)
- [ ] Fixed in physical calculation
- [ ] Added unit test for the fix
- [ ] Added edge case tests (0, negative, extreme values)
- [ ] Ran full test suite: `pytest tests/ -v`
- [ ] Verified no regressions

### 4. Naming Conventions

**Python (snake_case):**
- Functions: `perform_nucleation()`, `calculate_propensity()`
- Variables: `particle_diameter`, `system_volume`, `total_mass`
- Classes: `ParticleSystem`, `PopulationBalance` (PascalCase)
- Constants: `BOLTZMANN_CONSTANT`, `AVOGADRO_NUMBER`

**Example compliance:**
```python
# ✓ Good
def calculate_particle_diameter(num_atoms):
    total_atoms = num_atoms
    particle_volume = volume / density
    return 2 * radius

# ✗ Bad
def calcParticleDiam(n):  # camelCase instead of snake_case
    V = n/d  # Single letter variable
    return 2*R  # Unclear naming
```

## Testing Standards

### Test Organization

```
tests/
├── test_population_balance.py  # Gillespie algorithm tests
├── test_particle_system.py     # Physics mechanism tests
└── test_utilities.py           # Utility function tests
```

### Test Requirements

**Every function needs tests covering:**

1. **Happy path**: Normal usage
   ```python
   def test_nucleation_event(self):
       """Test that nucleation creates a particle."""
       system.perform_nucleation()
       assert len(system.particles) == 1
   ```

2. **Edge cases**: Boundary conditions
   ```python
   def test_empty_system(self):
       """Test operations on empty system."""
       assert system.get_mean_particle_diameter() == 0.0

   def test_single_particle(self):
       """Test coagulation with single particle."""
       system.add_particle(...)
       system.perform_coagulation()
       # Should not crash
   ```

3. **Error conditions**: Invalid inputs
   ```python
   def test_invalid_particle_index(self):
       """Test growth with non-existent particle."""
       rate = system.surface_growth_propensity(1000.0, particle_index=999)
       assert rate == 0.0  # No error, just zero rate
   ```

### Coverage Targets

- **Minimum**: 80% coverage on all modified files
- **Target**: 90%+ coverage
- **Check**: `pytest --cov=src --cov-report=html tests/`

### Test Execution

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_particle_system.py::TestParticleSystem -v

# Run specific test
pytest tests/test_particle_system.py::TestParticleSystem::test_nucleation_event -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
# View: htmlcov/index.html
```

## Physical Constants and Units

### SI Units (Standard)

- **Length**: meters (m)
- **Mass**: kilograms (kg)
- **Temperature**: Kelvin (K)
- **Time**: seconds (s)
- **Pressure**: Pascals (Pa)
- **Energy**: Joules (J)
- **Constants**:
  - Boltzmann: 1.380649e-23 J/K
  - Avogadro: 6.02214076e23 /mol
  - Carbon density: 2200 kg/m³

### Common Conversions

```python
# Diameter
diameter_nm = diameter_m * 1e9  # meters to nanometers

# Temperature
temperature_C = temperature_K - 273.15  # Kelvin to Celsius

# Propensity (reaction rate)
# Units vary by reaction type - see specific functions
```

## Performance Considerations

### Optimization Targets

1. **Particle Count**: ~100-1000 particles typical
   - <100: Fast, near-instantaneous
   - ~1000: Few seconds per simulation
   - >10000: Minutes, consider approximations

2. **Simulation Time**: 1-1000 milliseconds typical
   - Shorter: More noisy, fewer events
   - Longer: Smoother results, slower

3. **Number of Steps**: 1000-100000 steps typical
   - More steps: Better statistics, slower
   - Fewer steps: Faster, coarser results

### Profiling

```python
import time

start = time.time()
pb.simulate(num_steps=1000)
elapsed = time.time() - start

print(f"Time: {elapsed:.2f}s")
print(f"Steps per second: {1000/elapsed:.0f}")
```

## Common Pitfalls

### 1. Particle Index Out of Range

**Problem**:
```python
system.perform_surface_growth(particle_index=999)  # No particle at 999!
```

**Solution**: Check bounds or handle gracefully
```python
def perform_surface_growth(self, particle_index):
    if particle_index >= len(self.particles):
        return  # Silently ignore
```

### 2. Division by Zero in Propensity

**Problem**:
```python
propensity = 1.0 / (num_particles - 1)  # Crashes if num_particles == 1
```

**Solution**: Check before computing
```python
if num_particles < 2:
    return 0.0
propensity = 1.0 / (num_particles - 1)
```

### 3. Negative Values in Logarithm

**Problem**:
```python
rate = np.log(propensity)  # Crashes if propensity <= 0
```

**Solution**: Clamp before computing
```python
propensity = max(propensity, 1e-10)
rate = np.log(propensity)
```

### 4. Forgetting to Update Particle Properties

**Problem**:
```python
# Growth only updates diameter, not mass
particle["diameter"] *= 1.02  # Missing mass update!
```

**Solution**: Update all dependent properties
```python
particle["diameter"] *= 1.02
particle["mass"] = self._diameter_to_mass(particle["diameter"])
particle["radius"] = particle["diameter"] / 2.0
```

## Documentation Standards

### Docstrings (NumPy Format)

```python
def calculate_propensity(temperature, particle_diameter, concentration):
    """
    Calculate reaction propensity using temperature-dependent kinetics.

    Parameters
    ----------
    temperature : float
        System temperature in Kelvin (100-5000)
    particle_diameter : float
        Particle diameter in meters (1e-12 to 1e-6)
    concentration : float
        Precursor concentration in mol/m³ (0+)

    Returns
    -------
    float
        Propensity (reaction rate, unit depends on reaction type)

    Notes
    -----
    Uses Arrhenius law: rate = A * exp(-Ea / k_B * T)

    See Also
    --------
    surface_growth_propensity : Growth rate calculation
    coagulation_propensity : Collision rate calculation

    Examples
    --------
    >>> prop = calculate_propensity(1500.0, 5e-9, 1000.0)
    >>> prop > 0
    True
    """
```

### Comment Guidelines

```python
# Good: Explains WHY
# Collision frequency scales with sqrt(T) due to Brownian motion
velocity = np.sqrt(diffusion * boltzmann * temperature / particle_mass)

# Bad: Explains WHAT (redundant with code)
# Calculate velocity
velocity = np.sqrt(diffusion * boltzmann * temperature / particle_mass)
```

## Version Management

### Schema Versioning (Per DEVGUIDE)

**Current**: 0.1.0

- **MAJOR (0.1.0 → 1.0.0)**: Input parameter structure changes
  - Adding/removing/renaming propensity parameters
  - Changing particle property definitions
  - Action: Add migration logic, MAJOR version bump

- **MINOR (0.1.0 → 0.2.0)**: New output/calculations, no input change
  - New particle properties tracked
  - New statistic calculations
  - Action: Simple version bump, no migration needed

- **PATCH (0.1.0 → 0.1.1)**: Bug fixes only
  - Fixing incorrect calculation
  - Fixing edge case handling
  - Action: No version bump needed (unless critical)

## CI/CD and Validation

### Pre-Commit Checklist

```bash
# 1. Run tests
pytest tests/ -v

# 2. Check coverage
pytest --cov=src tests/ --cov-report=term-missing

# 3. Verify syntax
python -m py_compile src/*.py tests/*.py

# 4. Check naming
python scripts/check_naming_conventions.py

# 5. Code quality (optional)
flake8 src/ tests/
black src/ tests/ --check
```

### Continuous Integration

For CI/CD pipelines, use:

```yaml
# Example GitHub Actions workflow
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - run: pip install -r requirements.txt
    - run: pytest tests/ --cov=src
```

## Release Process

### Release Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage 80%+: `pytest --cov=src tests/`
- [ ] Version bumped in `src/__init__.py`
- [ ] CHANGELOG.md updated
- [ ] Documentation updated (README, examples)
- [ ] Tagged in git: `git tag v0.2.0`

## Resources

- **README.md**: User-facing documentation and theory
- **QUICKSTART.md**: Getting started guide
- **Original Thesis**: Celnik (2008) - contact Cambridge University Library
- **Key Papers**: See README References section
- **Example Code**: `examples/` directory

---

**Last Updated**: February 2026
**For**: Developers and Contributors
