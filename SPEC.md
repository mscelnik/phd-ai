# Code specification

This is the guide for the AI agent

## Problem statement

I want to recreate the code I wrote for my PhD in Python (originally it was F77, F90 and C++.). I want this to be a comprehensive code suite, covering all aspects of the physical model simulations.  Crucially, unlike my PhD, it should include thorough tests (unit and end-to-end.)

The code development should follow the included DEVGUIDE.md, which is written specifically to facilitate AI agents understanding of my expectations.

## Background information

I completed my PhD at the University of Cambridge, Chem Eng Dept (CoMo group) between 2004-2008.  I wrote several papers and a thesis, all of which are available on the internet (potentially only pre-prints of the papers are available, but they are almost identify to the published articles.)

The thesis title was "On the numerical modelling of soot and carbon nanotubes."

Some of my F90 and C++ PhD code was uploaded to Sourceforge at the time.  I think some may have been migrated to Github by subsequent researchers.

The code was a physical model simulator for nano-particle formation (two models: soot and carbon nanotubes.). It consisted of two solvers connected using an operator splitting algorithm:

    1. A gas phase chemistry solver (reaction sets should be available on the internet, e.g. for C2H2 acetylene combustion.); and
    2. A particle population-balance model - a stochastic Markov-chain Monte-Carlo model.

## Source material

You will have to locate all the relevant source material before creating the code - I don't have any compiled here.  I expect relevant files downloaded into a refs/ directory and a list of all sources included in the repo documentation.

## Expectations

  -  I expect a complete, well structured Python package with run scripts to be created.  It should include suitable object models and simulation code for all aspects of the solver.  Use established design patterns where appropriate.

  -  I want a human-readable input file structure (JSON or YAML, for example.).

  -  Outputs should also be human readable.  For tabular data use Excel or CSV.  Create a suitable folder structure to store different simulation runs (note, outputs should not be commited to the Git repo.)

  -  Use available and established 3rd party packages where possible, e.g. scipy, rather than recreating solvers or algorithms from scratch.  Do not use unknown packages (no malware.)

  - Document everything!  Use Sphinx for complex documentation if required.

  - Provide clear and useable instructions for a human to set up and run the simulations.

  -  Follow the DEVGUIDE at all times.
