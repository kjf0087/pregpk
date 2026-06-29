import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from pkdb.utilities import analysis_utils
analysis_utils.all_study_summaries("results")
input()