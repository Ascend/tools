import os
cur_path = os.path.dirname(os.path.realpath(__file__))
exec(open(os.path.join(cur_path, "ais_bench/infer/__main__.py")).read())