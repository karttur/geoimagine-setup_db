"""
Setup Karttur Geo Imagine postgres database framework

Author
______
Thomas Gumbricht
"""

from .version import __version__, VERSION
from geoimagine.setup_db.setup_db_class import PGsession