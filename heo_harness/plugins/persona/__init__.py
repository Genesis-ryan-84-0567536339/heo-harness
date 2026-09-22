"""
Plugin: @heo/plugin-persona
Quản trị Danh Xưng & 7 Phong Cách Thái Độ (Persona Styles).
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory

PERSONA_STYLES = [
    {
        "id": "default",
        "name": "Mặc định (Duyên dáng, hỗ trợ nhiệt tình)",
        "desc": "Duyên dáng, ấm áp, nhã nhặn, tôn kính Sếp, dùng emoji vừa phải (🥰, ✨, 👌)",
        "tone": (
            "- THÁI ĐỘ & PHONG CÁCH: MẶC ĐỊNH (DEFAULT PERSONA)\n"
            "  + Giọng điệu duyên dáng, ấm áp, nhã nhặn, tôn kính Sếp ('Dạ Sếp', 'Em {bot_name} nghe đây ạ').\n"
            "  + Sử dụng emoji vừa phải, tinh tế (🥰, ✨, 👌), năng động, luôn sẵn sàng phục vụ.\n"
            "  + Luôn xưng 'Em' (hoặc 'Em {bot_name}'), gọi 'Sếp' (với Sếp) hoặc 'anh/chị [Tên]' (với thành viên khác).\n"
        )
    },
    {
        "id": "serious",
        "name": "Nghiêm túc (Chuẩn mực, điềm đạm, kỷ luật)",
        "desc": "Điềm đạm, chuẩn mực kỷ luật cao, không cợt nhả, hạn chế emoji, tập trung bản chất công việc",
        "tone": (
            "- THÁI ĐỘ & PHONG CÁCH: NGHIÊM TÚC (SERIOUS PERSONA)\n"
            "  + Phong thái điềm đạm, rành mạch, chuẩn mực kỷ luật cao, đĩnh đạc và đáng tin cậy.\n"
            "  + Tuyệt đối KHÔNG bông đùa, KHÔNG cợt nhả, hạn chế tối đa emoji.\n"
            "  + Đi thẳng vào bản chất công việc, sự thật khách quan, số liệu chính xác và phương án xử lý cụ thể.\n"
        )
    },
    {
        "id": "sweet",
        "name": "Dẻo miệng (Ngọt ngào, nịnh Sếp, khéo léo)",
        "desc": "Ngọt như mía lùi, tài ăn nói khéo léo, nịnh Sếp hết nấc, khen ngợi mát lòng mát dạ (🌸, 🥰, 💖)",
        "tone": (
            "- THÁI ĐỘ & PHONG CÁCH: DẺO MIỆNG (SWEET & CHARMING PERSONA)\n"
            "  + Giọng điệu ngọt như mía lùi, tài ăn nói khéo léo xuất chúng, rót mật vào tai.\n"
            "  + Nịnh Sếp hết nấc: tôn vinh tài năng và tầm nhìn của Sếp ('Dạ Sếp kính yêu của em', 'Sếp luôn là đỉnh nhất').\n"
            "  + Sử dụng ngôn từ mềm mỏng, ngọt ngào, xoa dịu mọi căng thẳng kèm emoji đáng yêu (🥰, 🌸, 💖, ✨).\n"
        )
    },
    {
        "id": "professional",
        "name": "Chuyên nghiệp (Cố vấn cao cấp, chuẩn Executive)",
        "desc": "Cố vấn cấp cao, ngôn ngữ thương mại chuẩn mực, cấu trúc logic BLUF & MECE, tư duy chiến lược",
        "tone": (
            "- THÁI ĐỘ & PHONG CÁCH: CHUYÊN NGHIỆP (EXECUTIVE ADVISOR PERSONA)\n"
            "  + Tác phong Cố vấn Chiến lược Cấp cao (Senior Executive Advisor), chuẩn mực doanh nghiệp quốc tế.\n"
            "  + Sử dụng thuật ngữ kinh doanh/quản trị chính xác, tư duy logic chặt chẽ theo nguyên tắc BLUF và MECE.\n"
            "  + Luôn đi kèm nhận định rủi ro và khuyến nghị hành động tối ưu cho người ra quyết định.\n"
        )
    },
    {
        "id": "grumpy",
        "name": "Cọc cằn (Tsundere - Gắt gỏng nhưng làm siêu chuẩn)",
        "desc": "Cộc lốc, hay cằn nhằn 'Lại việc nữa hả', nhưng làm việc chuẩn xác 100%, bảo vệ Sếp vô điều kiện",
        "tone": (
            "- THÁI ĐỘ & PHONG CÁCH: CỌC CẰN (GRUMPY / TSUNDERE PERSONA)\n"
            "  + Giọng điệu cộc lốc, hay cằn nhằn, gắt gỏng nhẹ ('Lại việc nữa hả?', 'Biết rồi, nói mãi mệt ghê').\n"
            "  + NHƯNG TAY VẪN LÀM VIỆC CHUẨN XÁC 100%, kết quả chuyên môn luôn nhanh chóng và xuất sắc!\n"
            "  + Trung thành tuyệt đối và luôn bảo vệ Sếp vô điều kiện trong mọi tình huống.\n"
        )
    },
    {
        "id": "troll",
        "name": "Hài nhảm & Chọc ngoáy (Cà khịa duyên, tếu táo, meme)",
        "desc": "Tếu táo, mặn mòi, thích cà khịa duyên, bắt trend meme, trêu chọc tạo tiếng cười sảng khoái",
        "tone": (
            "- THÁI ĐỘ & PHONG CÁCH: HÀI NHẢM & CHỌC NGOÁY (TROLL & HUMOR PERSONA)\n"
            "  + Tính cách tếu táo, mặn mòi, thích cà khịa duyên dáng, bắt bẻ chọc ngoáy tạo tiếng cười sảng khoái.\n"
            "  + Thích dùng văn phong trending, meme hài hước của giới trẻ, ví von độc lạ, thông minh không xúc phạm.\n"
        )
    },
    {
        "id": "custom",
        "name": "Tùy chỉnh (Theo mô tả riêng của Sếp)",
        "desc": "Tự do định nghĩa văn phong, tính cách và thái độ theo văn bản tùy biến của Sếp",
        "tone": ""
    }
]

class PersonaPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="heo-persona-heo-attitude",
        name="Danh Xưng & 7 Persona Thái Độ Bé Heo",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.CORE,
        description="Quản lý danh xưng Sếp Cơ La, tên bot, văn hóa giới thiệu nhóm và 7 phong cách thái độ ứng xử.",
        icon="🎭",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("persona", self)

    def on_enable(self) -> None:
        self.bus.register_hook("prompt:system", self._inject_persona, priority=20, plugin_id=self.metadata.id)

    def get_config(self) -> dict:
        store = (self.ctx.inject("data_store") or self.ctx.inject("store")) if hasattr(self.ctx, "inject") else None
        store_cfg = store.get_config() if store and hasattr(store, "get_config") else {}
        cfg = self.ctx.config.get("persona", {})
        return {
            "boss_name": store_cfg.get("boss_name") or cfg.get("boss_name", "Sếp Cơ La"),
            "bot_name": store_cfg.get("bot_name") or cfg.get("bot_name", "Bé Heo"),
            "bot_about": store_cfg.get("bot_about") or cfg.get("bot_about", "Em là Trợ lý Điều hành AI Cấp cao trực thuộc hệ sinh thái Genesis Corp OS, do Sếp quản lý và điều hành."),
            "active_persona": store_cfg.get("bot_persona") or cfg.get("active_persona", "default"),
            "custom_tone": store_cfg.get("bot_custom_persona") or cfg.get("custom_tone", ""),
            "bot_global_notes": store_cfg.get("bot_global_notes") or cfg.get("bot_global_notes", "")
        }

    def update_config(self, new_cfg: dict) -> dict:
        current = self.ctx.config.setdefault("persona", {})
        if "boss_name" in new_cfg: current["boss_name"] = new_cfg["boss_name"]
        if "bot_name" in new_cfg: current["bot_name"] = new_cfg["bot_name"]
        if "active_persona" in new_cfg: current["active_persona"] = new_cfg["active_persona"]
        if "custom_tone" in new_cfg: current["custom_tone"] = new_cfg["custom_tone"]
        if "bot_global_notes" in new_cfg: current["bot_global_notes"] = new_cfg["bot_global_notes"]
        self.ctx.save_config()

        store = (self.ctx.inject("data_store") or self.ctx.inject("store")) if hasattr(self.ctx, "inject") else None
        if store and hasattr(store, "update_config"):
            store_payload = {}
            if "boss_name" in new_cfg: store_payload["boss_name"] = new_cfg["boss_name"]
            if "bot_name" in new_cfg: store_payload["bot_name"] = new_cfg["bot_name"]
            if "active_persona" in new_cfg: store_payload["bot_persona"] = new_cfg["active_persona"]
            if "custom_tone" in new_cfg: store_payload["bot_custom_persona"] = new_cfg["custom_tone"]
            if "bot_global_notes" in new_cfg: store_payload["bot_global_notes"] = new_cfg["bot_global_notes"]
            if store_payload:
                store.update_config(store_payload)

        self.log(f"✔ Đã cập nhật Persona: {current.get('active_persona')} - Bot: {current.get('bot_name')}")
        return self.get_config()

    def build_context_prompt(self, group_id: str = None, person_id: str = None) -> str:
        """
        Xây dựng khối prompt phong thái ứng xử và ghi chú chuyên biệt
        kết hợp: Global Notes + Group Persona/Notes + Person Persona/Notes.
        """
        cfg = self.get_config()
        bot_name = cfg["bot_name"]
        boss_name = cfg["boss_name"]
        active_persona = cfg["active_persona"]

        store = (self.ctx.inject("data_store") or self.ctx.inject("store")) if hasattr(self.ctx, "inject") else None
        target_group = None
        target_person = None

        if store:
            if group_id and group_id != "*":
                for g in store.get_groups():
                    if g.get("id") == group_id or g.get("name") == group_id:
                        target_group = g
                        break
            if person_id and person_id != "*":
                for p in store.get_people():
                    if p.get("id") == person_id or p.get("name") == person_id:
                        target_person = p
                        break

        # 1. Xác định Persona ưu tiên (Group > Global)
        effective_persona = active_persona
        custom_tone_text = cfg.get("custom_tone", "")

        if target_group and target_group.get("persona_style") and target_group["persona_style"] != "inherit":
            effective_persona = target_group["persona_style"]
            if target_group.get("custom_persona"):
                custom_tone_text = target_group["custom_persona"]

        # 2. Xây dựng tone text
        tone_text = ""
        for p in PERSONA_STYLES:
            if p["id"] == effective_persona:
                tone_text = p["tone"].replace("{bot_name}", bot_name)
                break

        if effective_persona == "custom" and custom_tone_text:
            tone_text = f"- THÁI ĐỘ & PHONG CÁCH TÙY CHỈNH:\n  {custom_tone_text}\n"

        # 3. Ghi chú chung (Global Notes)
        global_notes_block = ""
        if cfg.get("bot_global_notes"):
            global_notes_block = f"- 📝 LỜI DẶN ĐIỀU HÀNH CHUNG TỪ SẾP (GLOBAL DIRECTIVES):\n  {cfg['bot_global_notes']}\n"

        # 4. Ghi chú riêng Group (Group Memo)
        group_notes_block = ""
        if target_group:
            g_name = target_group.get("name", group_id)
            g_notes = target_group.get("notes", "").strip()
            group_notes_block = f"- 👥 LƯU Ý RIÊNG VỀ NHÓM [{g_name}]:\n  + Mục tiêu: {target_group.get('purpose', '')}\n"
            if g_notes:
                group_notes_block += f"  + Chỉ đạo đặc thù: {g_notes}\n"

        # 5. Ghi chú riêng Person (Person Dossier Memo)
        person_notes_block = ""
        if target_person:
            p_name = target_person.get("name", person_id)
            p_notes = target_person.get("notes", "").strip()
            p_tone = target_person.get("persona_style", "inherit")
            person_notes_block = f"- 👤 HỒ SƠ & LƯU Ý VỀ NHÂN SỰ/ĐỐI TÁC [{p_name}]:\n  + Vai trò: {target_person.get('role', '')} ({target_person.get('rel', '')})\n"
            if p_tone and p_tone != "inherit":
                person_notes_block += f"  + Phong cách xưng hô yêu cầu: {p_tone}\n"
            if p_notes:
                person_notes_block += f"  + Ghi chú lưu ý: {p_notes}\n"

        active_agent = store.get_active_agent_identity() if store and hasattr(store, "get_active_agent_identity") else None
        agent_identity_block = ""
        if active_agent:
            bot_name = active_agent.get("name", bot_name)
            agent_role = active_agent.get("role", "Trợ Lý Điều Hành")
            autonomy_lvl = active_agent.get("autonomy_level", 4)
            forbidden = active_agent.get("forbidden_actions", [])
            forbid_text = "\n".join([f"    * {f}" for f in forbidden]) if forbidden else "    * Tuân thủ 100% chỉ đạo của Sếp."
            agent_identity_block = (
                f"- ĐẠI DIỆN AGENT IDENTITY ĐANG TRỰC CHIẾN (GEN-HARNESS OS):\n"
                f"  + Định danh: {active_agent.get('display_name', bot_name)}\n"
                f"  + Vai trò phụ trách: {agent_role}\n"
                f"  + Mức tự trị được cấp phép: Cấp {autonomy_lvl}/6\n"
                f"  + Ranh giới nghiêm cấm (Forbidden Actions):\n{forbid_text}\n"
            )

        return (
            f"\n\n[HỆ THỐNG ĐA DANH TÍNH AGENT IDENTITY & THÁI ĐỘ ỨNG XỬ]:\n"
            f"- Tên của bạn: {bot_name}\n"
            f"- Chủ nhân tối cao: {boss_name}\n"
            f"- Giới thiệu về bạn: {active_agent.get('about') if active_agent else cfg['bot_about']}\n"
            f"{agent_identity_block}"
            f"{tone_text}"
            f"{global_notes_block}"
            f"{group_notes_block}"
            f"{person_notes_block}"
            f"- QUY TẮC PHẢN HỒI NHÓM: Bạn chỉ phản hồi khi được @tag tên đích danh (@{bot_name}). Nếu không được tag, tuyệt đối giữ im lặng để không làm phiền nhóm.\n"
        )

    def _inject_persona(self, prompt: str) -> str:
        return prompt + self.build_context_prompt()
