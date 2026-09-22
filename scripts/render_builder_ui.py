# -*- coding: utf-8 -*-
import json
import os

with open("/home/ryan/heo-harness/data/builder_plan.json", "r", encoding="utf-8") as f:
    plan_data = json.load(f)

plan_json = json.dumps(plan_data, ensure_ascii=False)

tpl_path = os.path.join(os.path.dirname(__file__), "builder_template.html")
with open(tpl_path, "r", encoding="utf-8") as f:
    template = f.read()

final_html = template.replace("__PLAN_JSON__", plan_json)

dest1 = "/home/ryan/heo-harness/artifacts/reports/gen_harness_builder.html"
dest2 = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_builder.html"

with open(dest1, "w", encoding="utf-8") as f:
    f.write(final_html)

if os.path.exists(os.path.dirname(dest2)):
    with open(dest2, "w", encoding="utf-8") as f:
        f.write(final_html)

print("Rendered gen_harness_builder.html cleanly from template!")
