import os

engine_code = '''

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
                conn.execute("""
                INSERT INTO atomic_events (id, event_type, source, sender_id, channel, content, timestamp, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"EVT-MATCH-{int(time.time())}",
                    "ExecutiveArbitrageDecision",
                    "GEN_HARNESS_MATCHMAKER",
                    "genesis.corp.os@gmail.com",
                    "EXECUTIVE_CONSOLE",
                    f"Sếp Ryan đã duyệt hành động {action_type} cho cơ hội mậu dịch {match_id} (Spread: {match['arbitrage_spread_val']:,.0f} ₫)",
                    time.time(),
                    json.dumps({"match_id": match_id, "action": action_type, "notes": notes}, ensure_ascii=False)
                ))
                conn.commit()
            except Exception:
                pass

            return {"ok": True, "match_id": match_id, "new_status": new_status, "executed_at": now}

def get_supply_demand_matchmaker():
    return SupplyDemandMatchmakerEngine.get_instance()
'''

with open('heo_harness/core/commercial_workbench.py', 'a', encoding='utf-8') as f:
    f.write(engine_code)

print('Appended successfully to commercial_workbench.py')
