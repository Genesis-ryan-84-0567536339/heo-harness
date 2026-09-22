file_path = "/home/ryan/heo-harness/artifacts/reports/gen_harness_test_ui.html"
wp_file = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_test_ui.html"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Increase deal distance from 115 to 135 and fan spread
code = code.replace(
    "const spreadOffset = (dIdx - (count - 1) / 2) * 0.85;\n        const finalAngle = baseAngle + spreadOffset;\n        const dealDistance = 115;",
    "const spreadOffset = (dIdx - (count - 1) / 2) * 1.15;\n        const finalAngle = baseAngle + spreadOffset;\n        const dealDistance = 138;"
)

# 2. Increase safe distances in physics
code = code.replace(
    "if (n1.type === 'opportunity' && n2.type === 'opportunity') {\n        minSafeDist = 95;\n      } else if (n1.type === 'opportunity' || n2.type === 'opportunity') {\n        minSafeDist = 115;",
    "if (n1.type === 'opportunity' && n2.type === 'opportunity') {\n        minSafeDist = 135;\n      } else if (n1.type === 'opportunity' || n2.type === 'opportunity') {\n        minSafeDist = 135;"
)

# 3. Truncate long opportunity labels in graph to prevent massive text overlap
code = code.replace(
    "const text = n.label || '';\n      ctx.font = isFocused ? '600 12px",
    "let text = n.label || '';\n      if (n.type === 'opportunity' && text.length > 22 && !isFocused) text = text.slice(0, 20) + '...';\n      ctx.font = isFocused ? '600 12px"
)

# 4. Spread bottom warm positions further apart
code = code.replace(
    "'cnt-CNT-006': { x: cx + 340, y: cy + 190 }, // Anh Minh Kafi\n      'cnt-CNT-008': { x: cx + 210, y: cy + 210 }, // Tập Đoàn Tân Á\n      'cnt-CNT-003': { x: cx + 70,  y: cy + 220 }  // Trần Thu Hà",
    "'cnt-CNT-006': { x: cx + 420, y: cy + 200 }, // Anh Minh Kafi\n      'cnt-CNT-008': { x: cx + 240, y: cy + 240 }, // Tập Đoàn Tân Á\n      'cnt-CNT-003': { x: cx + 30,  y: cy + 260 }  // Trần Thu Hà"
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

with open(wp_file, "w", encoding="utf-8") as f:
    f.write(code)

print("[OK] Đã tinh chỉnh khoảng cách node và nhãn deal chống dính chùm hoàn hảo!")
