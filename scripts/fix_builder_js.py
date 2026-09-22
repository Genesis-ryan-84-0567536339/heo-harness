# -*- coding: utf-8 -*-
import re

html_path = "artifacts/reports/gen_harness_builder.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix broken newlines in JS strings and regex
# 1. rawSpecText.split(' \n ');
content = re.sub(r"rawSpecText\.split\('\s*\n\s*'\)", "rawSpecText.split('\\n')", content)
content = re.sub(r"matched\.join\('\s*\n\s*'\)", "matched.join('\\n')", content)

# 2. let csv = "...\n";
content = re.sub(r'let csv = "(.*?)";', lambda m: 'let csv = "' + m.group(1).replace('\n', '\\n') + '";', content, flags=re.DOTALL)

# 3. join(",") + "\n";
content = re.sub(r'\.join\(","\)\s*\+\s*"\s*\n\s*";', '.join(",") + "\\n";', content)

# 4. split(/[, \n ]+/)
content = re.sub(r'split\(/\[,\s*\n\s*\]\+/\)', "split(/[,\\n]+/)", content)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

wp_path = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_builder.html"
with open(wp_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed JS strings and regex in builder HTML!")
