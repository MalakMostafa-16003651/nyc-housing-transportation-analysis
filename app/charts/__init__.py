"""
Registry of all 12 charts. The website draws them in this order.
Each member only edits their own memberN.py file.
"""

from charts import member1, member2, member3, member4, member5, member6

ALL_CHARTS = [
    (member, chart_fn)
    for member, module in [
        (1, member1), (2, member2), (3, member3),
        (4, member4), (5, member5), (6, member6),
    ]
    for chart_fn in (module.chart_1, module.chart_2)
]
