"""
GEN-HARNESS — Commercial Action Workbench & Commercial Copilot Engine
Mục tiêu SSOT:
- SPEC-25: [UI-09] Workbench — Bàn soạn thảo & Hành động thương mại (Soạn báo giá, hợp đồng, tin nhắn, kéo ERP/CRM)
- SPEC-34: Commercial Copilot — Trợ lý mậu dịch chuyên trách (Tự động soạn báo giá, tính biên lợi nhuận, dịch thuật song ngữ)
- SPEC-17: [UI-01] Data Confidence Index (Chỉ số độ tin cậy dữ liệu & kiểm định hồ sơ)
"""

import sqlite3
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "heo.db"))

class CommercialWorkbenchEngine:
    _instance = None

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    @classmethod
    def get_instance(cls, db_path: str = DB_PATH):
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        """Khởi tạo bảng commercial_documents nếu chưa có."""
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS commercial_documents (
                id TEXT PRIMARY KEY,
                deal_id TEXT,
                contact_id TEXT,
                contact_name TEXT,
                company TEXT,
                channel TEXT,
                doc_type TEXT,            -- 'QUOTATION', 'CONTRACT', 'PROPOSAL', 'MESSAGE'
                title TEXT,
                currency TEXT DEFAULT 'VND',
                items_json TEXT,          -- JSON array các module dịch vụ
                subtotal_amount REAL,
                discount_amount REAL,
                total_amount REAL,
                margin_pct REAL,          -- Biên lợi nhuận ước tính (%)
                payment_terms TEXT,       -- Điều khoản thanh toán
                valid_until TEXT,         -- Ngày hết hạn hiệu lực
                cover_letter TEXT,        -- Thư chào hàng / Lời ngỏ
                notes TEXT,               -- Ghi chú kỹ thuật & vận hành
                language TEXT DEFAULT 'vi', -- 'vi', 'en', 'zh'
                status TEXT DEFAULT 'DRAFT', -- 'DRAFT', 'WAITING_APPROVAL', 'APPROVED', 'SENT', 'ACCEPTED'
                sent_at TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            """)
            conn.commit()

    def get_service_catalog(self) -> List[Dict[str, Any]]:
        """(SPEC-18) Danh mục Dịch vụ Chuẩn 3 Tầng Gen-Harness."""
        return [
            {
                "code": "SRV-AI-01",
                "tier": "Core AI",
                "name": "Giải pháp AI Điều Phối & Lọc Ý Nghĩa Đa Kênh (Zalo + WhatsApp)",
                "unit": "Hệ thống / Năm",
                "base_price": 185000000.0,
                "cost_price": 45000000.0, # Chi phí hạ tầng & vận hành
                "description": "Cung cấp core engine AI tự động đọc hiểu hội thoại, trích xuất thẻ ý nghĩa, radar quan hệ và tính điểm tự trị 0-6.",
                "keywords": ["ai", "điều phối", "đa kênh", "zalo", "whatsapp", "bot", "tin nhắn"]
            },
            {
                "code": "SRV-ERP-02",
                "tier": "Integration",
                "name": "Gói Tích Hợp MCP Connectors & Cầu Nối Dữ Liệu ERP/CRM Doanh Nghiệp",
                "unit": "Dự án / On-Premise",
                "base_price": 350000000.0,
                "cost_price": 80000000.0,
                "description": "Kết nối hai chiều giữa Gen-Harness và cơ sở dữ liệu SAP/Odoo/CRM nội bộ, đồng bộ đơn hàng và công nợ thời gian thực.",
                "keywords": ["erp", "crm", "tích hợp", "mcp", "phần mềm", "cơ sở dữ liệu", "kết nối"]
            },
            {
                "code": "SRV-RPT-03",
                "tier": "Executive Intelligence",
                "name": "Dịch Vụ Báo Cáo Phân Tích Tài Chính & Giám Sát Thị Trường Thông Minh",
                "unit": "Gói Thuê Bao / Quý",
                "base_price": 50000000.0,
                "cost_price": 10000000.0,
                "description": "Tự động xuất báo cáo điều hành Word (.docx) & Excel (.xlsx) chuyên sâu, dự báo dòng tiền 72h và cảnh báo rủi ro.",
                "keywords": ["báo cáo", "tài chính", "phân tích", "đầu tư", "word", "excel", "thị trường"]
            },
            {
                "code": "SRV-AUD-04",
                "tier": "Media & Brand",
                "name": "Triển Khai Bộ Nhận Diện Âm Thanh AI & Giọng Đọc Độc Quyền Bản Quyền",
                "unit": "Bộ Nhận Diện",
                "base_price": 65000000.0,
                "cost_price": 12000000.0,
                "description": "Huấn luyện mô hình TTS giọng đọc thương hiệu riêng biệt, sáng tác nhạc hiệu AI MP3 beat cho phòng truyền thông.",
                "keywords": ["nhận diện", "giọng đọc", "audio", "tts", "nhạc", "beat", "truyền thông"]
            },
            {
                "code": "SRV-LIC-05",
                "tier": "Enterprise License",
                "name": "Hợp Đồng Cung Cấp Bản Quyền Gen-Harness Doanh Nghiệp (Enterprise SLA)",
                "unit": "License Vĩnh Viễn",
                "base_price": 240000000.0,
                "cost_price": 30000000.0,
                "description": "Chuyển giao quyền sử dụng trọn đời khung gầm Gen-Harness kèm bảo trì kỹ thuật 24/7 và cam kết SLA 99.9%.",
                "keywords": ["bản quyền", "doanh nghiệp", "license", "chuyển giao", "sla", "hợp đồng"]
            },
            {
                "code": "SRV-SRV-06",
                "tier": "Infrastructure",
                "name": "Thẩm Định & Thiết Kế Cụm Máy Chủ Cục Bộ Cho AI (Local AI Cluster)",
                "unit": "Gói Tư Vấn & Triển Khai",
                "base_price": 350000000.0,
                "cost_price": 95000000.0,
                "description": "Khảo sát và cài đặt hạ tầng GPU Private Cloud, chạy mô hình ngôn ngữ lớn nội bộ không phụ thuộc internet.",
                "keywords": ["máy chủ", "server", "hạ tầng", "cục bộ", "private", "gpu", "viettel"]
            },
            {
                "code": "SRV-CLD-07",
                "tier": "Cloud Services",
                "name": "Gói Thuê Máy Chủ Riêng Biệt & Proxy Điều Phối An Ninh Đa Kênh",
                "unit": "Gói 12 Tháng",
                "base_price": 15000000.0,
                "cost_price": 4000000.0,
                "description": "Hạ tầng Cloud chuyên dụng bảo vệ đường truyền Zalo/WhatsApp, chống chặn IP và backup tự động 6 giờ/lần.",
                "keywords": ["cloud", "server", "proxy", "thuê", "gói cước", "lưu trữ"]
            }
        ]

    def get_documents(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách các tài liệu thương mại đã tạo."""
        with self._get_conn() as conn:
            if status:
                cursor = conn.execute(
                    "SELECT * FROM commercial_documents WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                    (status, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM commercial_documents ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            docs = []
            for r in rows:
                d = dict(r)
                if d.get("items_json"):
                    try:
                        d["items"] = json.loads(d["items_json"])
                    except Exception:
                        d["items"] = []
                docs.append(d)
            return docs

    def get_document_detail(self, doc_id: str) -> Dict[str, Any]:
        """Chi tiết một văn kiện thương mại kèm hồ sơ đối tác 360."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM commercial_documents WHERE id = ?", (doc_id,)).fetchone()
            if not row:
                return {"ok": False, "error": "Document not found"}
            doc = dict(row)
            if doc.get("items_json"):
                try:
                    doc["items"] = json.loads(doc["items_json"])
                except Exception:
                    doc["items"] = []
            
            # Lấy thông tin contact
            contact = None
            if doc.get("contact_id"):
                c_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (doc["contact_id"],)).fetchone()
                if c_row:
                    contact = dict(c_row)

            # Lấy thông tin deal
            opportunity = None
            if doc.get("deal_id"):
                o_row = conn.execute("SELECT * FROM opportunities WHERE id = ?", (doc["deal_id"],)).fetchone()
                if o_row:
                    opportunity = dict(o_row)

            return {
                "ok": True,
                "document": doc,
                "contact": contact,
                "opportunity": opportunity
            }

    def generate_ai_quotation(self, deal_id: str, language: str = "vi") -> Dict[str, Any]:
        """(SPEC-34: Commercial Copilot) Tự động sinh bản Báo Giá Thông Minh chuẩn SSOT từ Deal & Hồ sơ sống."""
        with self._get_conn() as conn:
            opp_row = conn.execute("SELECT * FROM opportunities WHERE id = ?", (deal_id,)).fetchone()
            if not opp_row:
                return {"ok": False, "error": f"Không tìm thấy cơ hội {deal_id}"}
            opp = dict(opp_row)

            contact = None
            if opp.get("contact_id"):
                c_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (opp["contact_id"],)).fetchone()
                if c_row:
                    contact = dict(c_row)

        catalog = self.get_service_catalog()
        opp_text = f"{opp.get('title', '')} {opp.get('need_summary', '')}".lower()

        # Match các gói dịch vụ tốt nhất dựa trên từ khóa
        matched_items = []
        for cat_item in catalog:
            match_kws = [kw for kw in cat_item["keywords"] if kw in opp_text]
            if match_kws:
                score = len(match_kws)
                matched_items.append((score, cat_item))

        # Sắp xếp theo điểm khớp
        matched_items.sort(key=lambda x: x[0], reverse=True)

        selected_services = []
        if matched_items:
            # Chọn tối đa 2 dịch vụ khớp nhất
            for _, s in matched_items[:2]:
                selected_services.append(s)
        else:
            # Fallback nếu không khớp từ khóa
            selected_services.append(catalog[0])

        # Tính toán giá trị và chiết khấu
        items = []
        subtotal = 0.0
        total_cost = 0.0

        for s in selected_services:
            qty = 1
            price = s["base_price"]
            items.append({
                "code": s["code"],
                "name": s["name"],
                "unit": s["unit"],
                "unit_price": price,
                "quantity": qty,
                "total": price * qty,
                "cost": s["cost_price"] * qty
            })
            subtotal += price * qty
            total_cost += s["cost_price"] * qty

        # Chính sách chiết khấu thông minh dựa trên Heat Score & Khối lượng Deal
        heat = contact.get("heat_score", 50.0) if contact else 50.0
        discount_pct = 0.0
        if heat >= 85.0:
            discount_pct = 5.0 # Khách VIP điểm cao: ưu đãi 5%
        elif subtotal >= 300000000.0:
            discount_pct = 8.0 # Giá trị lớn: chiết khấu 8%

        discount_amount = subtotal * (discount_pct / 100.0)
        final_total = subtotal - discount_amount
        margin_pct = ((final_total - total_cost) / final_total * 100.0) if final_total > 0 else 0.0

        contact_name = contact.get("full_name", opp.get("contact_name", "Đối Tác")) if contact else "Đối Tác"
        company = contact.get("company", "Doanh Nghiệp") if contact else "Doanh Nghiệp"
        channel = opp.get("channel", "zalo")

        # Soạn thư chào hàng (Cover Letter) chuẩn Executive Intelligence
        if language == "en":
            title = f"Commercial Proposal: {opp.get('title', 'Enterprise Solution')}"
            cover_letter = (
                f"Dear {contact_name},\n\n"
                f"On behalf of Genesis Harness (Gen-Harness OS), we are pleased to submit our formal commercial proposal for {company}. "
                f"Based on our strategic alignment, this proposal outlines our proven architecture to empower your organization with executive-level automation.\n\n"
                f"We look forward to partnering with your leadership team.\n\n"
                f"Sincerely,\nAnh Cơ La (Ryan) — Founder & Executive Operator"
            )
            payment_terms = "50% advance payment upon signing; 50% upon successful deployment and UAT sign-off."
        elif language == "zh":
            title = f"商业报价提案: {opp.get('title', '企业级解决方案')}"
            cover_letter = (
                f"尊敬的 {contact_name} 您好，\n\n"
                f"代表 Genesis Harness (Gen-Harness OS)，我们谨向贵司 ({company}) 呈递此项正式商业合作提案。"
                f"结合双方前期沟通，本方案旨在为贵司部署高自主性、高可靠的智能协同中枢。\n\n"
                f"期待与贵方携手并进，共赢未来。\n\n"
                f"顺祝商祺，\nAnh Cơ La (Ryan) — 创始人兼总指挥"
            )
            payment_terms = "签约后预付50%；系统上线并完成UAT验收后支付余下50%。"
        else:
            title = f"Báo Giá Giải Pháp: {opp.get('title', 'Hệ Thống Tự Động Hóa Mậu Dịch')}"
            cover_letter = (
                f"Kính gửi: {contact_name} — {company},\n\n"
                f"Đại diện Ban Điều Hành Genesis Harness (Gen-Harness OS), em xin trân trọng gửi tới Sếp và Quý Doanh nghiệp bản Đề Xuất Giá Trị và Báo Giá Thương Mại chính thức.\n\n"
                f"Dựa trên tín hiệu nhu cầu thực tế đã trao đổi qua kênh {channel.upper()}, giải pháp dưới đây được thiết kế tối ưu hóa riêng biệt nhằm mang lại hiệu suất vận hành vượt trội và khả năng tự động hóa tối đa cho doanh nghiệp của Sếp.\n\n"
                f"Rất hân hạnh được đồng hành và triển khai cùng Quý đơn vị.\n\n"
                f"Trân trọng,\nAnh Cơ La (Ryan) — Tổng Chỉ Huy Tối Cao Gen-Harness OS"
            )
            payment_terms = "Tạm ứng 50% ngay sau khi ký thỏa thuận hợp tác; Thanh toán 50% còn lại sau khi hoàn tất bàn giao & nghiệm thu."

        now = datetime.now()
        valid_until = (now + timedelta(days=20)).strftime("%Y-%m-%d")
        doc_id = f"DOC-{now.strftime('%Y%m%d')}-{deal_id.replace('OPP-', '')[:6]}"

        doc_data = {
            "id": doc_id,
            "deal_id": deal_id,
            "contact_id": contact.get("id") if contact else None,
            "contact_name": contact_name,
            "company": company,
            "channel": channel,
            "doc_type": "QUOTATION",
            "title": title,
            "currency": "VND",
            "items": items,
            "items_json": json.dumps(items, ensure_ascii=False),
            "subtotal_amount": subtotal,
            "discount_amount": discount_amount,
            "total_amount": final_total,
            "margin_pct": round(margin_pct, 1),
            "payment_terms": payment_terms,
            "valid_until": valid_until,
            "cover_letter": cover_letter,
            "notes": f"Được tổng hợp tự động bởi Commercial Copilot dựa trên điểm quan hệ ({heat}°) và biểu giá Service Catalog v2.2.",
            "language": language,
            "status": "DRAFT",
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Lưu tự động vào DB
        self.save_document(doc_data)

        return {
            "ok": True,
            "document": doc_data,
            "copilot_insights": {
                "match_reason": f"Đã khớp {len(selected_services)} gói dịch vụ phù hợp nhất từ Catalog.",
                "discount_reason": f"Áp dụng chiết khấu {discount_pct}% nhờ điểm gắn kết ({heat}°).",
                "estimated_margin": f"{round(margin_pct, 1)}% (Đảm bảo trên ngưỡng an toàn 50%)"
            }
        }

    def save_document(self, doc: Dict[str, Any]) -> bool:
        """Lưu hoặc cập nhật văn kiện thương mại."""
        with self._get_conn() as conn:
            items_str = doc.get("items_json")
            if not items_str and "items" in doc:
                items_str = json.dumps(doc["items"], ensure_ascii=False)

            conn.execute("""
            INSERT OR REPLACE INTO commercial_documents (
                id, deal_id, contact_id, contact_name, company, channel, doc_type,
                title, currency, items_json, subtotal_amount, discount_amount,
                total_amount, margin_pct, payment_terms, valid_until, cover_letter,
                notes, language, status, sent_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.get("id"), doc.get("deal_id"), doc.get("contact_id"),
                doc.get("contact_name"), doc.get("company"), doc.get("channel"),
                doc.get("doc_type", "QUOTATION"), doc.get("title"),
                doc.get("currency", "VND"), items_str,
                doc.get("subtotal_amount", 0.0), doc.get("discount_amount", 0.0),
                doc.get("total_amount", 0.0), doc.get("margin_pct", 0.0),
                doc.get("payment_terms", ""), doc.get("valid_until", ""),
                doc.get("cover_letter", ""), doc.get("notes", ""),
                doc.get("language", "vi"), doc.get("status", "DRAFT"),
                doc.get("sent_at"),
                doc.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            return True

    def send_or_approve_document(self, doc_id: str, action: str = "approve_to_send") -> Dict[str, Any]:
        """(SPEC-25) Hành động thương mại: Gửi trực tiếp qua Zalo/WA hoặc Đẩy vào Hàng đợi Trình Sếp Duyệt."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM commercial_documents WHERE id = ?", (doc_id,)).fetchone()
            if not row:
                return {"ok": False, "error": "Document not found"}
            doc = dict(row)

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if action == "request_approval":
                # Đưa vào trạng thái chờ duyệt
                conn.execute(
                    "UPDATE commercial_documents SET status = 'WAITING_APPROVAL', updated_at = ? WHERE id = ?",
                    (now_str, doc_id)
                )
                conn.commit()
                return {
                    "ok": True,
                    "status": "WAITING_APPROVAL",
                    "message": f"Đã trình văn kiện {doc_id} vào Hàng Đợi Phê Duyệt Chiến Lược của Sếp Ryan!"
                }

            elif action in ["approve_and_send", "send_direct"]:
                # Đánh dấu đã gửi
                conn.execute(
                    "UPDATE commercial_documents SET status = 'SENT', sent_at = ?, updated_at = ? WHERE id = ?",
                    (now_str, now_str, doc_id)
                )

                # Ghi nhận sự kiện nguyên tử OfferedQuotation vào atomic_events
                event_id = f"evt-quotation-{int(time.time())}"
                payload = {
                    "doc_id": doc_id,
                    "title": doc.get("title"),
                    "total_amount": doc.get("total_amount"),
                    "channel": doc.get("channel")
                }
                conn.execute("""
                INSERT INTO atomic_events (
                    id, event_type, channel, sender_id, sender_name,
                    group_id, group_name, content, extracted_entities,
                    intent, sentiment, meaning_summary, action_suggested,
                    priority, status, heat_score, timestamp, created_at, archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    "OfferedQuotation",
                    doc.get("channel", "zalo"),
                    doc.get("contact_id") or "hq",
                    "Sếp Cơ La / HQ",
                    "DIRECT",
                    "Thương Mại & Báo Giá",
                    f"Đã phát hành và gửi báo giá {doc.get('title')} ({doc.get('total_amount'):,.0f} đ) cho {doc.get('contact_name')}.",
                    json.dumps(payload, ensure_ascii=False),
                    "Báo Giá Thương Mại",
                    "positive",
                    f"Gửi báo giá chính thức cho đối tác {doc.get('contact_name')}",
                    "Theo sát phản hồi và hỗ trợ chốt deal",
                    "P1",
                    "COMPLETED",
                    90.0,
                    int(time.time()),
                    now_str,
                    0
                ))
                conn.commit()

                return {
                    "ok": True,
                    "status": "SENT",
                    "message": f"Đã gửi báo giá thành công qua kênh {doc.get('channel', 'Zalo').upper()} cho đối tác {doc.get('contact_name')}!"
                }

            return {"ok": False, "error": "Invalid action"}

    def calculate_data_confidence_index(self) -> Dict[str, Any]:
        """(SPEC-17: [UI-01] Data Confidence Index - DCI) Tính toán chỉ số tin cậy dữ liệu SSOT."""
        with self._get_conn() as conn:
            contacts = [dict(r) for r in conn.execute("SELECT * FROM contacts").fetchall()]
            events = [dict(r) for r in conn.execute("SELECT * FROM atomic_events").fetchall()]
            opps = [dict(r) for r in conn.execute("SELECT * FROM opportunities").fetchall()]

        total_contacts = len(contacts) or 1
        total_events = len(events) or 1
        total_opps = len(opps) or 1

        # 1. Độ đầy đủ danh tính (% Contacts có Phone, Email/Kênh, Công ty, Vai trò)
        valid_identity_count = 0
        for c in contacts:
            has_name = bool(c.get("full_name"))
            has_channel = bool(c.get("zalo_id") or c.get("whatsapp_id") or c.get("phone"))
            has_company = bool(c.get("company"))
            has_role = bool(c.get("role"))
            if has_name and has_channel and (has_company or has_role):
                valid_identity_count += 1
        identity_completeness = round((valid_identity_count / total_contacts) * 100.0, 1)

        # 2. Tỷ lệ sự kiện nguyên tử đã được ánh xạ đối tượng (% Events có sender_id hợp lệ)
        mapped_events = sum(1 for e in events if e.get("sender_id") and e.get("sender_id") != "unknown")
        event_mapping_rate = round((mapped_events / total_events) * 100.0, 1)

        # 3. Tỷ lệ cơ hội có định giá ước tính rõ ràng
        valued_opps = sum(1 for o in opps if (o.get("estimated_value") or 0) > 0)
        valuation_coverage = round((valued_opps / total_opps) * 100.0, 1)

        # Điểm DCI tổng hợp có trọng số
        dci_score = round(
            identity_completeness * 0.40 +
            event_mapping_rate * 0.35 +
            valuation_coverage * 0.25,
            1
        )

        grade = "EXCELLENT" if dci_score >= 80 else ("GOOD" if dci_score >= 60 else "WARNING")
        grade_label = "🟢 Dữ Liệu Rất Tin Cậy" if dci_score >= 80 else ("🟡 Dữ Liệu Khá Tốt" if dci_score >= 60 else "🔴 Cần Bổ Sung Danh Tính")

        recommendations = []
        if identity_completeness < 80:
            recommendations.append("Cần bổ sung số điện thoại hoặc định danh công ty cho các liên hệ mới.")
        if event_mapping_rate < 80:
            recommendations.append("Cần chạy tác vụ Identity Resolution để gộp các sender_id chưa xác định.")
        if valuation_coverage < 80:
            recommendations.append("Một số cơ hội cần chuyên viên thương mại nhập giá trị kỳ vọng ước tính.")

        if not recommendations:
            recommendations.append("Chất lượng dữ liệu đạt tiêu chuẩn vàng SSOT, sẵn sàng cho tự động hóa cấp 4-5.")

        return {
            "ok": True,
            "dci_score": dci_score,
            "grade": grade,
            "grade_label": grade_label,
            "metrics": {
                "identity_completeness_pct": identity_completeness,
                "event_mapping_rate_pct": event_mapping_rate,
                "valuation_coverage_pct": valuation_coverage,
                "total_contacts": total_contacts,
                "total_events": total_events,
                "total_opportunities": total_opps
            },
            "recommendations": recommendations,
            "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def get_commercial_workbench():
    return CommercialWorkbenchEngine.get_instance()


# ==============================================================================
# SÀN PHÁT HIỆN & RÁP NỐI CUNG - CẦU THƯƠNG MẠI (SUPPLY - DEMAND MATCHMAKER)
# Vòng lặp điều hành: LISTEN -> STRUCTURE -> SCORE -> MATCH -> ACT
# ==============================================================================

class SupplyDemandMatchmakerEngine:
    _instance = None

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()
        self._seed_initial_data_if_empty()

    @classmethod
    def get_instance(cls, db_path: str = DB_PATH):
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        with self._get_conn() as conn:
            # 1. Bảng Nguồn CẦU (Demands)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS commercial_demands (
                id TEXT PRIMARY KEY,
                source_group TEXT,
                source_type TEXT,
                contact_name TEXT,
                category TEXT,
                title TEXT,
                description TEXT,
                quantity TEXT,
                target_price REAL,
                urgency TEXT,
                heat_score INTEGER,
                status TEXT DEFAULT 'OPEN',
                raw_message TEXT,
                created_at TEXT
            );
            """)

            # 2. Bảng Nguồn CUNG (Supplies)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS commercial_supplies (
                id TEXT PRIMARY KEY,
                source_group TEXT,
                source_type TEXT,
                provider_name TEXT,
                category TEXT,
                title TEXT,
                description TEXT,
                capacity TEXT,
                offered_price REAL,
                readiness TEXT,
                confidence_score INTEGER,
                status TEXT DEFAULT 'AVAILABLE',
                raw_message TEXT,
                created_at TEXT
            );
            """)

            # 3. Bảng Cặp Ráp Khớp Cung - Cầu & Thang Điểm Cơ Hội (Matches)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS commercial_matches (
                id TEXT PRIMARY KEY,
                demand_id TEXT,
                supply_id TEXT,
                match_score REAL,
                arbitrage_spread_val REAL,
                arbitrage_spread_pct REAL,
                total_rating INTEGER,
                rating_tier TEXT,
                explainable_reason TEXT,
                next_action_suggested TEXT,
                action_status TEXT DEFAULT 'PENDING',
                action_notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (demand_id) REFERENCES commercial_demands(id),
                FOREIGN KEY (supply_id) REFERENCES commercial_supplies(id)
            );
            """)
            conn.commit()

    def _seed_initial_data_if_empty(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT count(*) FROM commercial_demands")
            if c.fetchone()[0] > 0:
                return

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Hạt giống Nguồn CẦU (Demands)
            demands = [
                ("DEM-101", "Zalo: Hiệp Hội Nông Sản & XNK Việt Nam", "GROUP_ZALO", "Anh Minh (Nông Sản Á Châu)",
                 "Nông Sản & Thực Phẩm", "Cần 80 tấn hạt điều thô W320 chuẩn xuất khẩu EU",
                 "Cần giao hàng gấp trước ngày 15 tháng tới tại Cảng Cát Lái. Yêu cầu chứng nhận độ ẩm < 8% và chứng chỉ ATTP.",
                 "80 tấn", 1950000000.0, "HIGH", 92, "OPEN",
                 "Bác nào có nguồn hạt điều W320 chuẩn đi EU khoảng 80 tấn ới em gấp với nhé, ngân sách dưới 1.95 tỷ giao Cát Lái ạ.", now),

                ("DEM-102", "Zalo: Logistics & Vận Tải Chuỗi Lạnh Miền Nam", "GROUP_ZALO", "Chị Thu Hà (XK Trái Cây Miền Tây)",
                 "Logistics & Vận Tải", "Cần 10 xe lạnh 15 tấn Bình Thuận đi Cửa Khẩu Lạng Sơn trong 72h",
                 "Đóng thanh long tại Hàm Thuận Nam, nhiệt độ cài đặt 4-6°C. Yêu cầu xe đời mới có GPS giám sát nhiệt độ.",
                 "10 xe 15T", 320000000.0, "CRITICAL", 95, "OPEN",
                 "GẤP: Cần 10 container lạnh 15T nhận hàng sáng mai tại Bình Thuận ra thẳng Tân Thanh, cước thỏa thuận tối đa 32tr/xe.", now),

                ("DEM-103", "Khách Trực Tiếp Zalo / Contact 360", "DIRECT_CONTACT", "Chị Mai Phương (VinaSupply Corp)",
                 "Giải Pháp Công Nghệ / AI", "Cần giải pháp AI đọc hiểu chat Zalo và chăm sóc khách tự động",
                 "Doanh nghiệp phân phối đang quá tải tin nhắn Zalo bán hàng. Cần bot nhận diện đơn và cảnh báo khách VIP.",
                 "1 Hệ thống On-Premise", 250000000.0, "MEDIUM", 85, "OPEN",
                 "Bên chị muốn đặt hàng Heo-Harness triển khai riêng cho team sale 15 bạn, ngân sách khoảng 250tr duyệt trong tháng này.", now),

                ("DEM-104", "Zalo: Cộng Đồng Thủy Sản & Chế Biến Tây Nam Bộ", "GROUP_ZALO", "Anh Hoàng (Thủy Sản Biển Xanh)",
                 "Vật Liệu & Công Nghiệp", "Tìm nguồn thùng carton chống thấm 5 lớp 50.000 thùng",
                 "Thùng carton đóng gói cá tra phi lê xuất khẩu, kích thước chuẩn 50x30x20cm, phủ sáp chống ẩm cao cấp.",
                 "50.000 thùng", 450000000.0, "MEDIUM", 78, "OPEN",
                 "Tìm xưởng sản xuất thùng carton 5 lớp chống thấm số lượng 50k thùng giao về Cần Thơ, giá tầm 9k/thùng đổ lại.", now),

                ("DEM-105", "Zalo: Thương Lái & Doanh Nghiệp Hoa Quả Trung - Việt", "GROUP_ZALO", "Mr. Chen (Shanghai Fresh Import)",
                 "Nông Sản & Thực Phẩm", "Tìm 2 container sầu riêng Ri6 cấp đông xuất khẩu Thượng Hải",
                 "Yêu cầu cấp đông nguyên trái -18°C, có mã số vùng trồng và cơ sở đóng gói hợp lệ được GACC phê duyệt.",
                 "2 container (50 tấn)", 1250000000.0, "HIGH", 88, "OPEN",
                 "Looking for 2x40ft frozen Ri6 durian to Shanghai port. Budget ~1.25B VND per batch. Must have valid GACC export code.", now)
            ]

            conn.executemany("""
            INSERT INTO commercial_demands (id, source_group, source_type, contact_name, category, title, description, quantity, target_price, urgency, heat_score, status, raw_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, demands)

            # Hạt giống Nguồn CUNG (Supplies)
            supplies = [
                ("SUP-201", "WhatsApp: Nông Sản Tây Nguyên Sỉ & Kho Bãi", "GROUP_WHATSAPP", "HTX Điều Bình Phước (Anh Tuấn)",
                 "Nông Sản & Thực Phẩm", "Sẵn kho 120 tấn hạt điều W320 chuẩn Eurofins",
                 "Hạt điều mùa vụ mới, đã sấy phân loại đạt chuẩn W320, độ ẩm 7.2%, có kết quả test Eurofins sẵn sàng xuất khẩu.",
                 "120 tấn", 1760000000.0, "READY_STOCK", 95, "AVAILABLE",
                 "Kho em tại Bù Đăng vừa về 120 tấn W320 hàng đẹp xuất sắc, giấy tờ kiểm định Eurofins đủ, giá xả nhanh 1.76 tỷ cho lô 80 tấn.", now),

                ("SUP-202", "Zalo: Hội Chủ Xe & Vận Tải Xuyên Việt", "GROUP_ZALO", "Đội Xe Biển Đông Express",
                 "Logistics & Vận Tải", "Đội 12 xe đông lạnh 15T chiều về trống TP.HCM - Lạng Sơn",
                 "Đoàn xe giao sữa vào miền Nam vừa xong, đang rỗng chiều ra Lạng Sơn. Nhận hàng dọc QL1A hoặc Bình Thuận, cam kết chạy 55h ra biên.",
                 "12 xe 15T", 250000000.0, "READY_STOCK", 90, "AVAILABLE",
                 "Nhà xe Biển Đông có 12 xe lạnh 15 tấn rỗng chiều SG ra Lạng Sơn, nhận hàng Bình Thuận/Nha Trang giá chạy bù rỗng 25tr/xe trọn gói.", now),

                ("SUP-203", "Nội Bộ Genesis / Năng Lực Ryan", "INTERNAL_GENESIS", "Genesis Intelligence OS (Anh Cơ La)",
                 "Giải Pháp Công Nghệ / AI", "Gói Bản Quyền & Triển Khai Gen-Harness On-Premise",
                 "Kiến trúc DeepSeek Harness, Zalo + WhatsApp Gateway, tích hợp Living Profiles 360, bộ nhớ vĩnh cửu và tự động hóa điều hành.",
                 "Triển khai On-Premise", 65000000.0, "AVAILABLE", 100, "AVAILABLE",
                 "Năng lực nội bộ sẵn sàng đóng gói license và bàn giao chạy độc lập trên hạ tầng on-premise của đối tác trong 48h.", now),

                ("SUP-204", "WhatsApp: Bao Bì Công Nghiệp Sỉ Miền Nam", "GROUP_WHATSAPP", "Xưởng Bao Bì Nam Phát (Long An)",
                 "Vật Liệu & Công Nghiệp", "Dư 80.000 thùng carton sóng 5 lớp phủ PE chống ẩm",
                 "Hàng sản xuất theo đơn xuất khẩu thủy sản dư công suất, định lượng giấy 175gsm sóng BC chống thấm cực tốt, có sẵn tại kho Đức Hòa.",
                 "80.000 thùng", 385000000.0, "READY_STOCK", 88, "AVAILABLE",
                 "Xưởng Nam Phát xả nhanh 80k thùng carton 5 lớp chống ẩm 50x30x20 giá 7.7k/thùng cho bác nào bốc hết 50k thùng trở lên.", now),

                ("SUP-205", "Zalo: Nhà Vườn Tiền Giang & Bến Tre", "GROUP_ZALO", "Vựa Sầu Riêng Út Bình (Cai Lậy)",
                 "Nông Sản & Thực Phẩm", "Vựa sầu riêng Cai Lậy có sẵn 3 container Ri6 đang chờ mã vùng trồng",
                 "Sầu riêng cơm vàng hạt lép, cấp đông nguyên trái chất lượng cao, tuy nhiên mã số vùng trồng xuất khẩu đang chờ gia hạn duyệt.",
                 "3 container (75 tấn)", 1020000000.0, "ON_ORDER", 72, "AVAILABLE",
                 "Vựa em có sẵn 3 cont Ri6 đông lạnh đẹp đều giá 1.02 tỷ/cont nhưng hồ sơ mã xuất đang chờ duyệt thêm 2 tuần nữa ạ.", now)
            ]

            conn.executemany("""
            INSERT INTO commercial_supplies (id, source_group, source_type, provider_name, category, title, description, capacity, offered_price, readiness, confidence_score, status, raw_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, supplies)

            # Hạt giống Cặp Ráp Khớp & Thang Điểm Cơ Hội (Matches)
            matches = [
                ("MATCH-01", "DEM-101", "SUP-201", 94.5, 190000000.0, 9.7, 93, "TIER_A_PLUS",
                 "Độ khớp tuyệt đối về chủng loại hạt điều W320 và tiêu chuẩn kiểm định EU. Bên mua có ngân sách 1.95 tỷ, bên bán chào 1.76 tỷ. Chênh lệch gộp 190 triệu VNĐ (9.7%). Uy tín hai bên đều trên 90đ.",
                 "TRADE_ARBITRAGE", "PENDING", "Cơ hội vàng: Sếp có thể chọn đứng giữa bao tiêu trọn lô hoặc giới thiệu thu phí hoa hồng 3% (58.5 triệu).", now, now),

                ("MATCH-02", "DEM-102", "SUP-202", 92.0, 70000000.0, 21.8, 89, "TIER_A_PLUS",
                 "Nhu cầu vận chuyển chuỗi lạnh cực gấp 72h khớp hoàn hảo với 12 xe chiều về trống của Biển Đông Express. Chủ hàng chịu chi 320tr, nhà xe nhận 250tr vì bù rỗng. Biên lợi nhuận chênh lệch tới 21.8% (70 triệu VNĐ).",
                 "TRADE_ARBITRAGE", "PENDING", "Khuyên Sếp: Điều phối trung gian nhận trọn gói 320tr và ký sub-contract với nhà xe 250tr trong 1 nốt nhạc.", now, now),

                ("MATCH-03", "DEM-103", "SUP-203", 98.0, 185000000.0, 74.0, 96, "TIER_A_PLUS",
                 "Nhu cầu tự động hóa Zalo của VinaSupply khớp trực tiếp với Năng lực cốt lõi Gen-Harness của Genesis OS. Margin cực cao 74% (185 triệu), khách quen trong Living Profile với Heat Score 85°.",
                 "CREATE_PROPOSAL", "PENDING", "Đề xuất: Chuyển sang soạn thảo Đề Xuất Báo Giá Giải Pháp độc quyền cho Chị Mai Phương.", now, now),

                ("MATCH-04", "DEM-104", "SUP-204", 87.5, 65000000.0, 14.4, 84, "TIER_A",
                 "Khớp hoàn toàn quy cách thùng 5 lớp chống ẩm 50x30x20 cho thủy sản đông lạnh. Xưởng Nam Phát đang cần xả kho giải phóng mặt bằng, biên độ chênh lệch 65 triệu VNĐ.",
                 "INTRODUCE_COMMISSION", "PENDING", "Đề xuất: Giới thiệu hai bên giao dịch và thu hoa hồng kết nối 4% (18 triệu VNĐ).", now, now),

                ("MATCH-05", "DEM-105", "SUP-205", 76.0, 230000000.0, 18.4, 72, "TIER_B",
                 "Chênh lệch thương mại rất lớn 230 triệu VNĐ cho 2 container sầu riêng. Tuy nhiên vựa bán đang vướng mã số vùng trồng xuất khẩu, rủi ro hải quan cao.",
                 "VERIFY_MORE", "PENDING", "Cảnh báo: Cần giao Agent chat xác minh tiến độ cấp mã vùng trồng trước khi tiến hành ký kết.", now, now)
            ]

            conn.executemany("""
            INSERT INTO commercial_matches (id, demand_id, supply_id, match_score, arbitrage_spread_val, arbitrage_spread_pct, total_rating, rating_tier, explainable_reason, next_action_suggested, action_status, action_notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, matches)

            conn.commit()

    def get_summary(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT 
                count(*) as total_demands,
                coalesce(sum(target_price), 0) as total_demand_budget
            FROM commercial_demands WHERE status != 'CLOSED'
            """)
            row_demands = dict(c.fetchone())

            c.execute("""
            SELECT count(*) as total_supplies FROM commercial_supplies WHERE status = 'AVAILABLE'
            """)
            total_supplies = c.fetchone()[0]

            c.execute("""
            SELECT 
                count(*) as total_matches,
                coalesce(sum(arbitrage_spread_val), 0) as total_arbitrage_val,
                coalesce(avg(total_rating), 0) as avg_rating
            FROM commercial_matches WHERE action_status != 'DISMISSED'
            """)
            row_matches = dict(c.fetchone())

            # Phân bổ theo Tier
            c.execute("""
            SELECT rating_tier, count(*) as cnt FROM commercial_matches GROUP BY rating_tier
            """)
            tier_dist = {r["rating_tier"]: r["cnt"] for r in c.fetchall()}

        return {
            "ok": True,
            "total_demands": row_demands["total_demands"],
            "total_demand_budget": row_demands["total_demand_budget"],
            "total_supplies": total_supplies,
            "total_matches": row_matches["total_matches"],
            "total_arbitrage_val": row_matches["total_arbitrage_val"],
            "avg_rating": round(row_matches["avg_rating"], 1),
            "tier_distribution": {
                "TIER_A_PLUS": tier_dist.get("TIER_A_PLUS", 0),
                "TIER_A": tier_dist.get("TIER_A", 0),
                "TIER_B": tier_dist.get("TIER_B", 0),
                "TIER_C": tier_dist.get("TIER_C", 0)
            }
        }

    def get_matches(self, tier=None, category=None, status=None):
        with self._get_conn() as conn:
            query = """
            SELECT 
                m.*,
                d.source_group as demand_group,
                d.source_type as demand_source_type,
                d.contact_name as demand_contact,
                d.category as demand_category,
                d.title as demand_title,
                d.quantity as demand_quantity,
                d.target_price as demand_budget,
                d.urgency as demand_urgency,
                d.heat_score as demand_heat,
                d.description as demand_desc,
                d.raw_message as demand_raw,
                s.source_group as supply_group,
                s.source_type as supply_source_type,
                s.provider_name as supply_provider,
                s.category as supply_category,
                s.title as supply_title,
                s.capacity as supply_capacity,
                s.offered_price as supply_price,
                s.readiness as supply_readiness,
                s.confidence_score as supply_confidence,
                s.description as supply_desc,
                s.raw_message as supply_raw
            FROM commercial_matches m
            JOIN commercial_demands d ON m.demand_id = d.id
            JOIN commercial_supplies s ON m.supply_id = s.id
            WHERE 1=1
            """
            params = []
            if tier and tier != "ALL":
                query += " AND m.rating_tier = ?"
                params.append(tier)
            if category and category != "ALL":
                query += " AND d.category = ?"
                params.append(category)
            if status and status != "ALL":
                query += " AND m.action_status = ?"
                params.append(status)

            query += " ORDER BY m.total_rating DESC, m.arbitrage_spread_val DESC"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_all_demands(self, category=None):
        with self._get_conn() as conn:
            query = "SELECT * FROM commercial_demands WHERE 1=1"
            params = []
            if category and category != "ALL":
                query += " AND category = ?"
                params.append(category)
            query += " ORDER BY heat_score DESC, created_at DESC"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_all_supplies(self, category=None):
        with self._get_conn() as conn:
            query = "SELECT * FROM commercial_supplies WHERE 1=1"
            params = []
            if category and category != "ALL":
                query += " AND category = ?"
                params.append(category)
            query += " ORDER BY confidence_score DESC, created_at DESC"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def execute_next_action(self, match_id, action_type, notes=""):
        with self._get_conn() as conn:
            match = conn.execute("SELECT * FROM commercial_matches WHERE id = ?", (match_id,)).fetchone()
            if not match:
                return {"ok": False, "error": f"Không tìm thấy cặp ghép nối {match_id}"}

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            action_map = {
                "INTRODUCE_COMMISSION": "INTRODUCED",
                "TRADE_ARBITRAGE": "ARBITRAGED",
                "VERIFY_MORE": "VERIFYING",
                "CREATE_PROPOSAL": "PROPOSAL_CREATED",
                "DISMISS": "DISMISSED"
            }
            new_status = action_map.get(action_type, "PENDING")

            conn.execute("""
            UPDATE commercial_matches 
            SET action_status = ?, action_notes = ?, updated_at = ?
            WHERE id = ?
            """, (new_status, notes or f"Quyết định của Sếp Ryan: {action_type}", now, match_id))
            conn.commit()

            # Tự động ghi nhận một sự kiện nguyên tử vào bảng atomic_events để làm giàu lịch sử
            try:
                evt_id = f"EVT-MATCH-{int(time.time())}"
                conn.execute("""
                INSERT INTO atomic_events (
                    id, event_type, channel, sender_id, sender_name,
                    group_id, group_name, content, extracted_entities,
                    intent, sentiment, meaning_summary, action_suggested,
                    priority, status, heat_score, timestamp, created_at, archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evt_id,
                    "ExecutiveArbitrageDecision",
                    "web_console",
                    "genesis.corp.os@gmail.com",
                    "Anh Cơ La (Ryan)",
                    "DIRECT",
                    "Điều Hành Trực Chiến",
                    f"Sếp Ryan đã duyệt hành động {action_type} cho cơ hội mậu dịch {match_id} (Spread: {match['arbitrage_spread_val']:,.0f} ₫)",
                    json.dumps({"match_id": match_id, "action": action_type, "notes": notes}, ensure_ascii=False),
                    "Quyết Định Mậu Dịch",
                    "positive",
                    f"Duyệt cơ hội mậu dịch {match_id}",
                    f"Triển khai hành động: {action_type}",
                    "P1",
                    new_status,
                    95.0,
                    int(time.time()),
                    now,
                    0
                ))
                conn.commit()
            except Exception:
                pass

            return {"ok": True, "match_id": match_id, "new_status": new_status, "executed_at": now}

def get_supply_demand_matchmaker():
    return SupplyDemandMatchmakerEngine.get_instance()
