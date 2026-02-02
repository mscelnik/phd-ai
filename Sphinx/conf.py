import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
project = 'PhD AI Simulation Suite'
author = 'CoMo Group'
release = '1.0'
extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
