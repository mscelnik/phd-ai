# My PhD, but AI

An experiment to understand the research, deep-reasoning and coding capabilities of different AI agents in GitHub copilot.

I completed my PhD between 2004-2008.  It was entirely focused on numerical modelling and I wrote a lot of F77, F90 and C++ code (as well as bash scripts, Makefiles, R scripts etc. etc.)

A lot has changed since then; the iPhone didn't exist when I started my PhD for example! Now - since GPT 3.5 anyway - the rise of AI copilots and now AI agents has revolutionised software development (and perhaps software engineering - but we'll investigate that.)  In this repo, I have provide instructions for AI agents to replicate the simulation code I created for my PhD (see SPEC.md.)  I have not provided much technicl detail; just enough for the agent to search the internet and find the relevant papers (and the code if it exists - this was before GitHub existed after all!)

The three artefacts provided to the agent:
  1. PROMPT.md - the prompt used to initiate the agent's development attempt.
  2. SPEC.md - the problem statement and expected outcomes.
  3. DEVGUIDE.md - ruleset the agent must follow when developing software.

That's it.  I'll execute the same prompt with different agents and save the results on corresponding repo branches.  The main branch will only store instructions.

## Results

| Agent | Attempt | Branch | Summary |
| -- | -- | -- | -- |
| GPT-4.1 | 1 | gpt-41-r1 | **Good structure, incomplete implementation**. Created proper package structure (src/, tests/, scripts/), ~288 LOC, Sphinx docs setup, Makefile, CI/CD. Has placeholders for chemistry solver and particle model but lacks actual physics/chemistry implementation. Tests exist but validate scaffolding, not real algorithms. Good adherence to DEVGUIDE requirements but missing core SPEC functionality (no actual gas-phase chemistry mechanisms, simplified particle dynamics). |
| GPT-4o | 1 | gpt-4o-r1 | **Minimal effort, incomplete**. Very basic structure (~208 LOC), has gas_phase_solver.py and particle_balance_model.py with skeletal classes. Chemistry solver has framework for reaction mechanisms but with placeholder implementations. Particle model has empty method stubs (coagulation/fragmentation not implemented). No refs/ directory, no data files, no documentation beyond code comments. Tests exist but minimal. Did not meet SPEC requirement to locate source materials or implement complete solvers. |
| GPT-5 mini | 1 | gpt-5mini-r1 | **Simplified but functional approach**. Compact implementation (~154 LOC) with proper package structure (src/phdai/). Created refs/ with web references (acetylene.txt, pbe.txt, soot.txt), example config YAML, run script. Code is intentionally simplified/educational rather than comprehensive. Has basic chemistry and particle modules but lacks full physics. Better at following instructions to gather references than GPT-4o. Pragmatic but incomplete relative to SPEC's "comprehensive code suite" requirement. |
| Claude Haiku 4.5 | 0 | claude-haiku-4.5-r0 | **Excellent documentation, minimal code**. Outstanding README (430+ lines) with comprehensive background, equations, references, usage examples. Only ~41 LOC of actual implementation. Focused heavily on theoretical foundation (Gillespie algorithm, PBE, citations). Package structure exists but modules are stubs. Shows strong research capability and understanding of domain but failed to implement working solvers. Great at documentation, weak at code delivery. Attempt "0" suggests this may have been abandoned early. |
| Claude Opus 4.5 | 1 | claude-opus-4.5-r1 | **Most complete and professional**. Full package with proper structure including data/mechanisms/, schema/, examples/, comprehensive tests (unit/integration/e2e). Integrates Cantera for real chemistry (GRI-Mech 3.0). Has CLI tool, detailed README, CHANGELOG, proper versioning. Implements actual operator splitting, batch reactor, and particle processes. Shows understanding of production software engineering with schema validation, logging, multiple output formats. Best adherence to both SPEC requirements (comprehensive code) and DEVGUIDE (testing, structure, documentation). Most production-ready implementation. |
