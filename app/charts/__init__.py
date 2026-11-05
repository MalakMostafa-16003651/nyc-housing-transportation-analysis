"""
Registry of all research-question visualizations, in the order the website shows them.
Each pair of research questions lives in its own file (rq1_rq2.py, rq3_rq4.py, ...).
A file that is not finished yet shows a "Chart coming soon" placeholder.
"""

from charts import rq1_rq2, rq3_rq4, rq5_rq6, rq7_rq8, rq9_rq10, rq11_rq12

ALL_CHARTS = [
    (1, rq1_rq2.rq1), (2, rq1_rq2.rq2),
    (3, rq3_rq4.rq3), (4, rq3_rq4.rq4),
    (5, rq5_rq6.rq5), (6, rq5_rq6.rq6),
    (7, rq7_rq8.rq7), (8, rq7_rq8.rq8),
    (9, rq9_rq10.rq9), (10, rq9_rq10.rq10),
    (11, rq11_rq12.rq11), (12, rq11_rq12.rq12),
]
