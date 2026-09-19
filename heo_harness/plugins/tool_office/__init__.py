"""
Plugin: heo-tool-office-reporter
Bộ Công Cụ Báo Cáo Tài Liệu Word (.docx) & Bảng Tính Excel (.xlsx) Tự Động.
Tạo file Microsoft Office OpenXML chuẩn hành chính, không phụ thuộc thư viện ngoài.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory
import zipfile
import os
import time

class OfficeToolPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="heo-tool-office-reporter",
        name="Xuất Báo Cáo Tài Liệu Word & Excel",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.TOOL,
        description="Định dạng văn bản hành chính chuyên nghiệp, xuất file Word và bảng tính tài chính Excel.",
        icon="📊",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("tool_office", self)
        self.output_dir = os.path.abspath("artifacts/reports")
        os.makedirs(self.output_dir, exist_ok=True)

    def on_enable(self) -> None:
        self.log("Đã kích hoạt Office Document Exporter (Word & Excel).")

    def export_word(self, title: str = "Báo Cáo Điều Hành", content: str = "") -> dict:
        return self.safe_execute(self._do_export_word, title, content)

    def export_excel(self, title: str = "Bảng Tính Tài Chính", rows: list = None) -> dict:
        return self.safe_execute(self._do_export_excel, title, rows)

    def _do_export_word(self, title: str, content: str) -> dict:
        safe_title = title.replace(" ", "_").replace("/", "_")
        filename = f"{safe_title}_{int(time.time())}.docx"
        out_path = os.path.join(self.output_dir, filename)

        if not content:
            content = (
                "BÁO CÁO ĐIỀU HÀNH EXECUTIVE INTELLIGENCE OS (HEO-HARNESS)\n"
                "- Tác quyền kiến trúc: Anh Cơ La (genesis.corp.os@gmail.com)\n"
                "- Nền tảng: Khung sườn DSH chuẩn 'Everything is a Plugin'\n"
                "- Lõi suy luận: Google Antigravity CLI gói tháng (0đ API token)\n"
                "- Trạng thái hệ thống: Tường lửa 5 tầng Policy Gate và Circuit Breaker hoạt động 100%."
            )

        paragraphs_xml = ""
        for line in content.split("\n"):
            line = line.strip()
            if line:
                paragraphs_xml += f'<w:p><w:r><w:t>{line}</w:t></w:r></w:p>'

        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="38"/></w:rPr><w:t>{title.upper()}</w:t></w:r></w:p>
    <w:p><w:r><w:rPr><w:i/><w:color w:val="666666"/></w:rPr><w:t>Tác giả: Anh Cơ La (genesis.corp.os@gmail.com) · Tạo lúc: {time.strftime('%Y-%m-%d %H:%M:%S')}</w:t></w:r></w:p>
    <w:p><w:r><w:t>--------------------------------------------------------------------------------</w:t></w:r></w:p>
    {paragraphs_xml}
  </w:body>
</w:document>"""

        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("word/document.xml", doc_xml)

        size_kb = round(os.path.getsize(out_path) / 1024, 1)
        self.log(f"✔ Đã xuất tài liệu Word thành công: {filename} ({size_kb} KB)")
        return {
            "ok": True,
            "filename": filename,
            "path": out_path,
            "download_url": f"/download/reports/{filename}",
            "size_kb": size_kb,
            "size_bytes": os.path.getsize(out_path),
            "evidence": f"artifact:DOC-{int(time.time()*1000)%100000} · truth:FACT",
            "message": f"Đã xuất thành công tài liệu Word '{filename}'!"
        }

    def _do_export_excel(self, title: str, rows: list) -> dict:
        safe_title = title.replace(" ", "_").replace("/", "_")
        filename = f"{safe_title}_{int(time.time())}.xlsx"
        out_path = os.path.join(self.output_dir, filename)

        if not rows:
            rows = [
                ["STT", "HẠNG MỤC HỆ THỐNG", "THÔNG SỐ / TRẠNG THÁI", "GHI CHÚ KIẾN TRÚC"],
                ["1", "Chassis Khung Gầm", "DeepSeek Harness (DSH)", "Everything is a Plugin"],
                ["2", "Core Agent", "Google Antigravity CLI", "Gói tháng cá nhân (0đ token API)"],
                ["3", "Tác Quyền Sáng Lập", "Anh Cơ La (Ryan)", "genesis.corp.os@gmail.com"],
                ["4", "Tường Lửa Thẩm Định", "Policy Gate 5 Tầng", "GLOBAL -> CHANNEL -> GROUP -> PERSON -> ACTION"],
                ["5", "Bộ Lọc Kênh Zalo", "Lọc @tag Bé Heo", "Bảo vệ nhóm riêng tư"],
                ["6", "Doanh Thu Dự Kiến", "500,000,000 VNĐ", "Hệ thống tự động hóa doanh nghiệp"],
                ["7", "Chi Phí Token API", "0 VNĐ", "Tiết kiệm 100% nhờ Antigravity CLI"]
            ]

        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
        wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""
        wb_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Report" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""
        
        sheet_data = ""
        for r_idx, row in enumerate(rows, 1):
            cols_xml = ""
            for c_idx, val in enumerate(row, 1):
                col_letter = chr(64 + c_idx)
                cols_xml += f'<c r="{col_letter}{r_idx}" t="inlineStr"><is><t>{val}</t></is></c>'
            sheet_data += f'<row r="{r_idx}">{cols_xml}</row>'
            
        sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{sheet_data}</sheetData>
</worksheet>"""

        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
            z.writestr("xl/workbook.xml", wb_xml)
            z.writestr("xl/worksheets/sheet1.xml", sheet_xml)

        size_kb = round(os.path.getsize(out_path) / 1024, 1)
        self.log(f"✔ Đã xuất bảng tính Excel thành công: {filename} ({size_kb} KB)")
        return {
            "ok": True,
            "filename": filename,
            "path": out_path,
            "download_url": f"/download/reports/{filename}",
            "size_kb": size_kb,
            "size_bytes": os.path.getsize(out_path),
            "evidence": f"artifact:XLS-{int(time.time()*1000)%100000} · truth:FACT",
            "message": f"Đã xuất thành công bảng tính Excel '{filename}'!"
        }
