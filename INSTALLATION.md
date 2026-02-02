# Installation & Verification Checklist

## Pre-Installation Requirements

- [ ] Python 3.8+ installed and in PATH
  - Test: `python --version`
- [ ] pip installed and working
  - Test: `pip --version`
- [ ] ~200MB disk space available
- [ ] Internet connection (for dependency download)

## Installation Steps

### Step 1: Navigate to Project Directory
```bash
cd c:\Data\repos\_NO_GIT\phd-ai\nano-stochastic-model
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify**: Prompt should show `(venv)` at start

### Step 3: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected output**: Successfully installed 5 packages
- numpy
- scipy
- matplotlib
- pytest
- pytest-cov

### Step 5: Install Package
```bash
pip install -e .
```

**Expected**: "Successfully installed nano-stochastic-model"

## Verification Tests

### Test 1: Python Import
```bash
python -c "import src; print('✓ Import successful')"
```

**Expected**: `✓ Import successful`

### Test 2: Run Unit Tests
```bash
pytest tests/ -v
```

**Expected**: All 110+ tests pass (indicated by green ✓)

**Example output:**
```
tests/test_population_balance.py::TestPopulationBalance::test_initialization PASSED
tests/test_population_balance.py::TestPopulationBalance::test_particle_initialization PASSED
...
============ 110 passed in 2.34s ============
```

### Test 3: Check Coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected**: Coverage ≥ 85%

**Example output:**
```
src/population_balance.py     420  65    85%
src/particle_system.py        450  72    84%
src/utilities.py              150  18    88%
src/events.py                  20   0   100%
TOTAL                        1040  155   85%
```

### Test 4: Run Example 1
```bash
cd examples
python example_basic_simulation.py
```

**Expected**:
- Completes in ~2 seconds
- Creates file `example1_particles.png`
- Displays particle statistics

**Sample output:**
```
======================================================================
Example 1: Basic Nano-Particle System Simulation
======================================================================

Creating particle system...
  Temperature: 1500 K
  Pressure: 101325 Pa
  Volume: 1e-06 m³

Simulating nucleation events...
  Created 20 particles

Particle system statistics:
  Number of particles: 20
  Mean diameter: 2.34 nm
  Total volume: 6.72e-23 m³

Generating visualization...
  Saved plot to: example1_particles.png
```

### Test 5: Run Example 2
```bash
python example_gillespie_simulation.py
```

**Expected**:
- Completes in 10-30 seconds
- Creates file `example2_gillespie_simulation.png`
- Shows time-evolution of particle population

**Sample output:**
```
======================================================================
Example 2: Stochastic Population Balance Simulation
======================================================================

Creating population balance model...
  Initialized with 10 particles

Running Gillespie simulation...
  Simulation completed
  Final time: 1.000000e-03 s

Final system state:
  Particles: 45
  Mean diameter: 3.21 nm
  Total mass: 1.87e-19 kg

Generating visualization...
  Saved plot to: example2_gillespie_simulation.png
```

## Troubleshooting

### Issue: "Python not found"
**Solution**:
1. Install Python from https://www.python.org/
2. Check "Add Python to PATH" during installation
3. Restart terminal after installation
4. Verify: `python --version`

### Issue: "venv activation doesn't work"
**Windows Solution**:
```bash
venv\Scripts\activate
# If that fails, try:
python -m venv venv
```

**Linux/Mac Solution**:
```bash
source venv/bin/activate
# If that fails, try:
python3 -m venv venv
```

### Issue: "pip install fails"
**Solution**:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Issue: "Tests fail to import src"
**Solution**:
```bash
pip install -e .  # Install package in development mode
pytest tests/ -v  # Run tests again
```

### Issue: "matplotlib can't display plots"
**Expected**: Plots are saved to disk, not displayed
- Files: `examples/example1_particles.png`, `examples/example2_gillespie_simulation.png`
- Open with: Image viewer or web browser

### Issue: "Simulation runs very slowly"
**Normal**: First run may be slow (dependencies loading)
- Example 1: Should take ~2 seconds
- Example 2: Should take ~10-30 seconds
- If much slower: Check CPU usage, available RAM

## Quick Command Reference

```bash
# Activate venv
venv\Scripts\activate              # Windows
source venv/bin/activate           # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src

# Run specific test
pytest tests/test_particle_system.py -v

# Run examples
cd examples
python example_basic_simulation.py
python example_gillespie_simulation.py

# Check Python version
python --version

# Deactivate venv
deactivate

# Check what's installed
pip list
```

## Project Structure Verification

After installation, verify these files exist:

```
nano-stochastic-model/
├── src/
│   ├── __init__.py              ✓
│   ├── population_balance.py    ✓
│   ├── particle_system.py       ✓
│   ├── events.py                ✓
│   └── utilities.py             ✓
├── tests/
│   ├── test_population_balance.py  ✓
│   ├── test_particle_system.py     ✓
│   └── test_utilities.py           ✓
├── examples/
│   ├── example_basic_simulation.py     ✓
│   └── example_gillespie_simulation.py ✓
├── README.md                    ✓
├── QUICKSTART.md                ✓
├── requirements.txt             ✓
└── setup.py                     ✓
```

## Post-Installation

### Next Steps

1. **Read Documentation**
   - `README.md` - Full user guide
   - `QUICKSTART.md` - Getting started
   - `DEVELOPMENT.md` - Developer guide

2. **Run Examples**
   - `examples/example_basic_simulation.py`
   - `examples/example_gillespie_simulation.py`

3. **Try Basic Usage**
   ```python
   from src.particle_system import ParticleSystem
   system = ParticleSystem(temperature=1500.0)
   system.perform_nucleation()
   print(system.get_system_state())
   ```

4. **Extend the Code**
   - Add new reaction mechanisms
   - Implement custom propensity functions
   - Create your own simulations

### Keep Virtual Environment Activated

Always activate the virtual environment before working:

**Windows**: `venv\Scripts\activate`
**Linux/Mac**: `source venv/bin/activate`

Prompt should show: `(venv) PS >` or `(venv) $`

## Success Criteria

✅ Installation is successful if:

1. [ ] Virtual environment created and activated
2. [ ] All dependencies installed: `pip list` shows numpy, scipy, matplotlib, pytest
3. [ ] All 110+ tests pass: `pytest tests/ -v`
4. [ ] Coverage ≥ 85%: `pytest --cov=src tests/`
5. [ ] Example 1 runs and creates PNG: `python example_basic_simulation.py`
6. [ ] Example 2 runs and creates PNG: `python example_gillespie_simulation.py`
7. [ ] Can import and use: `python -c "from src.particle_system import ParticleSystem"`

If all items are checked ✓, installation is **COMPLETE** and ready to use!

---

## Support Resources

- 📖 **README.md** - Full documentation and theory
- ⚡ **QUICKSTART.md** - 5-minute getting started
- 🔧 **DEVELOPMENT.md** - Developer guide
- 📚 **examples/** - Working code examples
- 🧪 **tests/** - Test code (shows usage patterns)

## Project Information

- **Project**: Nano-Particulate Stochastic Model
- **Based On**: Dr. Matthew Celnik's PhD Thesis (2008)
- **Version**: 0.1.0
- **License**: MIT
- **Status**: Complete and ready to use

---

**Installation Guide Version**: 1.0
**Last Updated**: February 2, 2026
