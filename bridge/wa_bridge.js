#!/usr/bin/env node
/**
 * ==============================================================================
 * HEO-HARNESS WHATSAPP MULTI-DEVICE BRIDGE
 * Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
 * 
 * Sử dụng @whiskeysockets/baileys để duy trì kết nối WebSocket thời gian thực
 * với hệ thống WhatsApp Web Multi-Device của Meta.
 * - Nhận mã QR thật từ sự kiện connection.update và ghi ra data/whatsapp_qr.png
 * - Lắng nghe tin nhắn 2 chiều, lọc @tag nhóm và chuyển tới AGY Engine (/api/chat)
 * - Cung cấp Outbound HTTP Server trên cổng 5052 (/api/send, /api/status, /api/restart, /api/logout)
 * ==============================================================================
 */

const fs = require("fs");
const path = require("path");
const http = require("http");
const axios = require("axios");
const qrcode = require("qrcode");
const pino = require("pino");
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require("@whiskeysockets/baileys");

const BASE_DIR = process.env.BASE_DIR || path.resolve(__dirname, "..");
const DATA_DIR = process.env.DATA_DIR || path.join(BASE_DIR, "data");
const LOG_DIR = process.env.LOG_DIR || path.join(BASE_DIR, "logs");
const AUTH_DIR = path.join(DATA_DIR, "whatsapp_auth");
const QR_PATH = path.join(DATA_DIR, "whatsapp_qr.png");
const AGY_ENGINE_URL = process.env.AGY_ENGINE_URL || "http://127.0.0.1:5088";
const OUTBOUND_PORT = parseInt(process.env.WA_BRIDGE_PORT || "5052", 10);
const STATE_FILE = path.join(DATA_DIR, "heo_state.json");
const BOT_NAME = "Bé Heo";

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
if (!fs.existsSync(AUTH_DIR)) fs.mkdirSync(AUTH_DIR, { recursive: true });

let sock = null;
let isConnected = false;
let userJid = null;
let userPhone = null;
let userLid = null;
let userName = null;
const processedMsgIds = new Set();
const groupNameCache = new Map();

async function getWhatsAppGroupName(gid) {
  if (!gid || !gid.endsWith("@g.us")) return "";
  if (groupNameCache.has(gid)) return groupNameCache.get(gid);
  try {
    if (sock) {
      const meta = await sock.groupMetadata(gid);
      if (meta && meta.subject) {
        groupNameCache.set(gid, meta.subject);
        return meta.subject;
      }
    }
  } catch (e) {}
  return gid.replace("@g.us", "");
}

function isBotMentionedOrReplied(m, text) {
  const myId = sock?.user?.id || userJid || "";
  const myLid = sock?.user?.lid || userLid || "";
  const myPhone = userPhone || (myId ? myId.split(":")[0].split("@")[0] : "84567536339");
  const myLidNum = myLid ? myLid.split(":")[0].split("@")[0] : "171443048472761";

  const contextInfo = m.message?.extendedTextMessage?.contextInfo;
  const mentionedJid = contextInfo?.mentionedJid || [];
  const quotedParticipant = contextInfo?.participant || "";

  // 1. Tag menu WhatsApp (@) chứa JID / LID / Phone của bot
  const inMentions = mentionedJid.some(j => {
    if (!j) return false;
    return (myPhone && j.includes(myPhone)) ||
           (myLidNum && j.includes(myLidNum)) ||
           (myId && j.split(":")[0] === myId.split(":")[0]) ||
           (myLid && j.split(":")[0] === myLid.split(":")[0]);
  });
  if (inMentions) return true;

  // 2. Trả lời (quote / reply) tin nhắn của Bot
  if (quotedParticipant) {
    if ((myPhone && quotedParticipant.includes(myPhone)) ||
        (myLidNum && quotedParticipant.includes(myLidNum)) ||
        (myId && quotedParticipant.split(":")[0] === myId.split(":")[0]) ||
        (myLid && quotedParticipant.split(":")[0] === myLid.split(":")[0])) {
      return true;
    }
  }

  // 3. Tag dạng text trong nội dung tin nhắn (@84567536339 hoặc @171443048472761)
  if (myPhone && text.includes(`@${myPhone}`)) return true;
  if (myLidNum && text.includes(`@${myLidNum}`)) return true;

  // 4. Nhắc đến tên bot (không phân biệt hoa thường)
  const lower = text.toLowerCase();
  const keywords = [
    "bé heo", "be heo", "heo ơi", "heo oi", "@heo", "@bé heo", "@be heo",
    "@heo-agent", "heo-agent", "/heo", "heo bot", "bot heo", "@bot", "bot ơi", "bot oi"
  ];
  if (keywords.some(k => lower.includes(k))) return true;

  // Regex từ khóa đứng độc lập (vd: "heo cho hỏi...", "alo heo...")
  if (/\b(?:heo|bé\s*heo)\b/i.test(lower)) return true;

  return false;
}

function log(msg) {
  const ts = new Date().toISOString().replace(/T/, " ").replace(/\..+/, "");
  console.log(`[${ts}] [AGY-WhatsApp] ${msg}`);
}

function updateSystemState(connected, phone = "", name = "") {
  try {
    if (fs.existsSync(STATE_FILE)) {
      const data = JSON.parse(fs.readFileSync(STATE_FILE, "utf-8"));
      if (!data.whatsapp) data.whatsapp = {};
      data.whatsapp.connected = connected;
      data.whatsapp.status = connected ? "ONLINE" : "WAITING_FOR_QR";
      if (phone) data.whatsapp.phone_number = "+" + phone;
      if (name) data.whatsapp.bot_name = name;

      // Đồng bộ vào whatsapp_profiles
      if (Array.isArray(data.accounts?.whatsapp_profiles) && data.accounts.whatsapp_profiles.length > 0) {
        data.accounts.whatsapp_profiles[0].phone = phone ? "+" + phone : "Chưa liên kết";
        data.accounts.whatsapp_profiles[0].name = name || "Bé Heo (WhatsApp Gateway)";
        data.accounts.whatsapp_profiles[0].connected = connected;
        data.accounts.whatsapp_profiles[0].status = connected ? "ONLINE" : "WAITING_FOR_QR";
      }

      fs.writeFileSync(STATE_FILE, JSON.stringify(data, null, 2), "utf-8");
      log(`💾 Đã đồng bộ trạng thái WhatsApp (${connected ? 'ONLINE' : 'OFFLINE'}) vào heo_state.json`);
    }
  } catch (err) {
    log(`⚠️ Lỗi cập nhật heo_state.json: ${err.message}`);
  }
}

async function handleIncomingMessage(m) {
  try {
    const msgId = m.key.id;
    if (msgId) {
      if (processedMsgIds.has(msgId)) return;
      processedMsgIds.add(msgId);
      if (processedMsgIds.size > 300) {
        const first = processedMsgIds.values().next().value;
        processedMsgIds.delete(first);
      }
    }

    const remoteJid = m.key.remoteJid || "";
    const isGroup = remoteJid.endsWith("@g.us");
    const senderJid = m.key.participant || remoteJid;
    const pushName = m.pushName || "Thành viên WhatsApp";

    // Trích xuất nội dung văn bản
    let text = "";
    if (m.message?.conversation) {
      text = m.message.conversation;
    } else if (m.message?.extendedTextMessage?.text) {
      text = m.message.extendedTextMessage.text;
    } else if (m.message?.imageMessage?.caption) {
      text = m.message.imageMessage.caption;
    } else if (m.message?.videoMessage?.caption) {
      text = m.message.videoMessage.caption;
    }

    text = (text || "").trim();
    if (!text) return;

    let groupName = "";
    if (isGroup) {
      groupName = await getWhatsAppGroupName(remoteJid);
      const isMentioned = isBotMentionedOrReplied(m, text);

      if (!isMentioned) {
        log(`👁️ [QUAN SÁT NHÓM: ${groupName}] ${pushName}: "${text.substring(0, 60)}" (Im lặng theo SSOT)`);
        // Bắn log trực tiếp vào Core Store để Sếp thấy Heo đang quan sát nhóm
        axios.post(`${AGY_ENGINE_URL}/api/logs/add`, {
          channel: "whatsapp",
          level: "INFO",
          message: `👁️ [QUAN SÁT NHÓM: ${groupName}] ${pushName}: "${text}"`,
          details: `Group: ${groupName} (${remoteJid}) · Sender: ${pushName} [${senderJid}] · Trạng thái: Không được @tag nên Heo giữ im lặng theo quy tắc.`,
          metadata: {
            type: "chat_inbound",
            chat_type: "group",
            channel: "whatsapp",
            group: groupName,
            group_id: remoteJid,
            sender: pushName,
            sender_id: senderJid,
            content: text,
            mentioned: false
          }
        }).catch(() => {});
        return;
      }
    }

    log(`📩 [INBOUND ${isGroup ? `NHÓM: ${groupName}` : '1-1'}] từ ${pushName} [${senderJid}]: "${text.substring(0, 60)}"`);

    // Gửi trạng thái đang soạn tin (typing / composing) lên WhatsApp để người dùng biết Heo đang xử lý
    let typingTimer = null;
    if (sock) {
      try {
        await sock.sendPresenceUpdate('composing', remoteJid);
        typingTimer = setInterval(async () => {
          try {
            if (sock) await sock.sendPresenceUpdate('composing', remoteJid);
          } catch (e) {}
        }, 4000);
      } catch (e) {}
    }

    try {
      // Gửi sang AGY Engine để suy luận
      const resp = await axios.post(`${AGY_ENGINE_URL}/api/chat`, {
        message: text,
        sender_id: senderJid,
        sender_name: pushName,
        group_id: isGroup ? remoteJid : "*",
        group_name: groupName,
        is_group: isGroup,
        channel: "whatsapp"
      }, { timeout: 90000 });

      const reply = resp.data?.reply || resp.data?.answer || resp.data?.content || resp.data?.message;
      if (reply && sock) {
        await sock.sendMessage(remoteJid, { text: reply }, { quoted: m });
        log(`🚀 [OUTBOUND REPLIED -> ${isGroup ? groupName : '1-1'}]: "${reply.substring(0, 60)}..."`);
      }
    } finally {
      if (typingTimer) clearInterval(typingTimer);
      if (sock) {
        try {
          await sock.sendPresenceUpdate('paused', remoteJid);
        } catch (e) {}
      }
    }
  } catch (err) {
    log(`⚠️ Lỗi xử lý tin nhắn WhatsApp: ${err.message}`);
  }
}

async function connectToWhatsApp() {
  log("🔄 Đang khởi tạo kết nối WhatsApp Multi-Device Socket...");
  try {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version } = await fetchLatestBaileysVersion().catch(() => ({ version: [2, 3000, 1015901307] }));

    sock = makeWASocket({
      version,
      logger: pino({ level: "silent" }),
      auth: state,
      printQRInTerminal: false,
      browser: ["Heo Executive OS", "Chrome", "1.0.0"],
      syncFullHistory: false,
      connectTimeoutMs: 60000,
      keepAliveIntervalMs: 25000
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        log(`📡 Nhận mã QR WhatsApp Multi-Device THẬT từ Meta (Token size: ${qr.length})`);
        try {
          await qrcode.toFile(QR_PATH, qr, {
            color: { dark: "#052e16", light: "#ffffff" },
            width: 399,
            margin: 2
          });
          log(`✅ Đã xuất mã QR thật ra file: ${QR_PATH}`);
          updateSystemState(false);
        } catch (qrErr) {
          log(`⚠️ Lỗi lưu file QR: ${qrErr.message}`);
        }
      }

      if (connection === "close") {
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
        isConnected = false;
        log(`⚠️ Mất kết nối WhatsApp (Status Code: ${statusCode}). Tự động kết nối lại: ${shouldReconnect}`);

        if (statusCode === DisconnectReason.loggedOut) {
          log("❌ Phiên làm việc WhatsApp đã bị đăng xuất trên điện thoại. Làm mới dữ liệu...");
          try {
            fs.rmSync(AUTH_DIR, { recursive: true, force: true });
            if (fs.existsSync(QR_PATH)) fs.unlinkSync(QR_PATH);
          } catch (_) {}
          updateSystemState(false);
          setTimeout(connectToWhatsApp, 3000);
        } else if (shouldReconnect) {
          setTimeout(connectToWhatsApp, 3000);
        }
      } else if (connection === "open") {
        isConnected = true;
        userJid = sock.user?.id || "";
        userPhone = userJid.split(":")[0].split("@")[0];
        userLid = sock.user?.lid ? sock.user.lid.split(":")[0].split("@")[0] : "";
        userName = sock.user?.name || "Bé Heo (WhatsApp)";
        log(`🎉 KẾT NỐI THÀNH CÔNG WHATSAPP MULTI-DEVICE! Số ĐT: +${userPhone} (${userName})`);

        // Xóa QR khi đã liên kết xong
        if (fs.existsSync(QR_PATH)) {
          try { fs.unlinkSync(QR_PATH); } catch (_) {}
        }

        updateSystemState(true, userPhone, userName);
        setTimeout(syncAllWhatsAppGroups, 1000);
      }
    });

    sock.ev.on("messages.upsert", async ({ messages, type }) => {
      if (type !== "notify") return;
      for (const m of messages) {
        if (m.key.fromMe) continue;
        await handleIncomingMessage(m);
      }
    });

    sock.ev.on("group-participants.update", async (update) => {
      const gid = update.id;
      const action = update.action;
      const participants = update.participants || [];

      const isBotTargeted = participants.some(p => {
        const raw = p.split("@")[0].split(":")[0];
        return (userPhone && raw === userPhone) || (userLid && raw === userLid);
      });

      if (action === "add") {
        if (isBotTargeted) {
          try {
            let meta = null;
            try { meta = await sock.groupMetadata(gid); } catch (e) {}
            const name = meta?.subject || groupNameCache.get(gid) || "Nhóm WhatsApp Mới";
            groupNameCache.set(gid, name);

            log(`🎉 [AGY-WhatsApp] Bé Heo vừa được thêm vào nhóm: "${name}" (${gid})!`);

            await axios.post(`${AGY_ENGINE_URL}/api/logs/add`, {
              channel: "whatsapp",
              level: "SUCCESS",
              chat_type: "group",
              message: `🎉 [WHATSAPP] Bé Heo vừa được thêm vào nhóm: "${name}"! Tự động kích hoạt quan sát & nhận diện nhóm.`,
              details: `Group ID: ${gid} · Thành viên: ${meta?.participants?.length || 'N/A'}`,
              metadata: { event: "group_join", chat_type: "group", channel: "whatsapp", group_id: gid, group_name: name }
            }).catch(() => {});

            debouncedSyncWhatsAppGroups(500);
          } catch (e) {
            log(`⚠️ Lỗi xử lý khi được add vào nhóm: ${e.message}`);
          }
        } else {
          debouncedSyncWhatsAppGroups(3000);
        }
      } else if (action === "remove") {
        if (isBotTargeted) {
          const name = groupNameCache.get(gid) || gid;
          log(`⚠️ [AGY-WhatsApp] Bé Heo đã rời hoặc bị mời ra khỏi nhóm: "${name}" (${gid})`);

          await axios.post(`${AGY_ENGINE_URL}/api/logs/add`, {
            channel: "whatsapp",
            level: "WARN",
            chat_type: "group",
            message: `⚠️ [WHATSAPP] Bé Heo đã rời khỏi nhóm: "${name}". Đã chuyển trạng thái sang "Đã rời nhóm".`,
            details: `Group ID: ${gid}`,
            metadata: { event: "group_leave", chat_type: "group", channel: "whatsapp", group_id: gid, group_name: name, status: "left" }
          }).catch(() => {});

          await axios.post(`${AGY_ENGINE_URL}/api/groups/sync`, {
            channel: "whatsapp",
            groups: [{ id: gid, status: "left", name: name }]
          }).catch(() => {});
        } else {
          debouncedSyncWhatsAppGroups(3000);
        }
      }
    });

    sock.ev.on("groups.upsert", async (groups) => {
      for (const g of groups) {
        if (g.id && g.subject) {
          groupNameCache.set(g.id, g.subject);
        }
      }
      debouncedSyncWhatsAppGroups(3000);
    });

    sock.ev.on("groups.update", async (updates) => {
      for (const u of updates) {
        if (u.id && u.subject) {
          groupNameCache.set(u.id, u.subject);
        }
      }
      debouncedSyncWhatsAppGroups(3000);
    });

  } catch (initErr) {
    log(`❌ Lỗi khởi tạo Baileys Socket: ${initErr.message}`);
    setTimeout(connectToWhatsApp, 5000);
  }
}

let syncDebounceTimer = null;
function debouncedSyncWhatsAppGroups(delay = 2000) {
  if (syncDebounceTimer) clearTimeout(syncDebounceTimer);
  syncDebounceTimer = setTimeout(() => {
    syncAllWhatsAppGroups().catch(() => {});
  }, delay);
}

let lastWhatsAppSyncTime = 0;
let lastCachedWhatsAppGroups = [];

async function syncAllWhatsAppGroups(force = false) {
  if (!sock || !isConnected) return lastCachedWhatsAppGroups;
  const now = Date.now();
  if (!force && (now - lastWhatsAppSyncTime) < 15000 && lastCachedWhatsAppGroups.length > 0) {
    return lastCachedWhatsAppGroups;
  }
  lastWhatsAppSyncTime = now;
  try {
    const groups = await sock.groupFetchAllParticipating();
    const groupList = [];
    for (const [gid, g] of Object.entries(groups)) {
      const name = g.subject || "Nhóm WhatsApp";
      groupNameCache.set(gid, name);
      const members = (g.participants || []).map(p => {
        const rawId = p.id || "";
        const phone = rawId.split("@")[0].split(":")[0];
        const isBot = (userPhone && phone === userPhone) || (userLid && rawId.includes(userLid));
        return {
          id: rawId,
          name: isBot ? "Bé Heo (Bot)" : (phone.length > 8 ? `+${phone}` : phone),
          phone: phone,
          role: p.admin ? (p.admin === "superadmin" ? "Trưởng nhóm" : "Phó nhóm") : "Thành viên",
          is_boss: false
        };
      });
      groupList.push({
        id: gid,
        name: name,
        channel: "whatsapp",
        purpose: "Nhóm làm việc WhatsApp Multi-Device",
        total_members: members.length,
        members: members,
        creator_id: g.owner || "",
        status: "active",
        created_at: g.creation ? new Date(g.creation * 1000).toISOString().split("T")[0] : new Date().toISOString().split("T")[0]
      });
    }

    lastCachedWhatsAppGroups = groupList;

    try {
      fs.writeFileSync(path.join(DATA_DIR, "whatsapp_active_groups.json"), JSON.stringify(groupList, null, 2), "utf-8");
    } catch (_) {}

    await axios.post(`${AGY_ENGINE_URL}/api/groups/sync`, {
      channel: "whatsapp",
      groups: groupList
    }, { timeout: 10000 }).catch(() => {});

    log(`📋 [AGY-WhatsApp] Đã đồng bộ ${groupList.length} nhóm WhatsApp thực tế sang Heo OS!`);
    return groupList;
  } catch (err) {
    log(`⚠️ [AGY-WhatsApp] Lỗi đồng bộ nhóm WhatsApp: ${err.message}`);
    return lastCachedWhatsAppGroups;
  }
}

// Khởi tạo Outbound HTTP Server trên cổng 5052
function startOutboundServer() {
  const server = http.createServer(async (req, res) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");

    if (req.method === "OPTIONS") {
      res.writeHead(204);
      res.end();
      return;
    }

    if (req.method === "GET" && req.url === "/api/status") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({
        connected: isConnected,
        phone: userPhone,
        name: userName,
        qr_available: fs.existsSync(QR_PATH)
      }));
      return;
    }

    if (req.method === "GET" && req.url === "/api/groups") {
      try {
        const groups = await syncAllWhatsAppGroups();
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: true, count: groups.length, groups }));
      } catch (e) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: e.message }));
      }
      return;
    }

    if (req.method === "POST" && req.url === "/api/groups/sync") {
      try {
        const groups = await syncAllWhatsAppGroups();
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: true, count: groups.length, groups }));
      } catch (e) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: e.message }));
      }
      return;
    }

    if (req.method === "POST" && req.url === "/api/group/leave") {
      let body = "";
      req.on("data", chunk => body += chunk);
      req.on("end", async () => {
        try {
          const payload = JSON.parse(body);
          const gid = payload.groupId || payload.group_id || "";
          if (gid && sock) {
            await sock.groupLeave(gid);
            log(`👋 [AGY-WhatsApp] Đã thực hiện lệnh rời nhóm: ${gid}`);
          }
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: true, left: gid }));
        } catch (e) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: false, error: e.message }));
        }
      });
      return;
    }

    if (req.method === "POST" && req.url === "/api/send") {
      let body = "";
      req.on("data", chunk => body += chunk);
      req.on("end", async () => {
        try {
          const payload = JSON.parse(body);
          const target = payload.target_id || payload.to || "";
          const content = payload.content || payload.message || "";

          if (!target || !content) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ ok: false, error: "Thiếu target_id hoặc content" }));
            return;
          }

          if (!isConnected || !sock) {
            res.writeHead(503, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ ok: false, error: "WhatsApp Bridge chưa kết nối (WAITING_FOR_QR)" }));
            return;
          }

          let jid = target;
          if (!jid.includes("@")) {
            let cleanPhone = jid.replace(/\D/g, "");
            if (cleanPhone.startsWith("0")) cleanPhone = "84" + cleanPhone.substring(1);
            jid = `${cleanPhone}@s.whatsapp.net`;
          }

          await sock.sendMessage(jid, { text: content });
          log(`✔ [Outbound Sent] Đã gửi tới ${jid}: "${content.substring(0, 50)}..."`);
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: true, target: jid }));
        } catch (sendErr) {
          log(`❌ [Outbound Error]: ${sendErr.message}`);
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: false, error: sendErr.message }));
        }
      });
      return;
    }

    if (req.method === "POST" && req.url === "/api/restart") {
      log("🔄 Nhận lệnh khởi động lại socket WhatsApp theo yêu cầu...");
      try {
        if (sock) sock.end();
      } catch (_) {}
      setTimeout(connectToWhatsApp, 1000);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ ok: true, message: "Restarting WhatsApp socket..." }));
      return;
    }

    if (req.method === "POST" && req.url === "/api/logout") {
      log("🚪 Nhận lệnh đăng xuất tài khoản WhatsApp...");
      try {
        if (sock) await sock.logout();
        fs.rmSync(AUTH_DIR, { recursive: true, force: true });
        if (fs.existsSync(QR_PATH)) fs.unlinkSync(QR_PATH);
      } catch (_) {}
      isConnected = false;
      updateSystemState(false);
      setTimeout(connectToWhatsApp, 2000);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ ok: true, message: "Đã đăng xuất WhatsApp thành công" }));
      return;
    }

    res.writeHead(404);
    res.end();
  });

  server.on("error", (err) => {
    if (err.code === "EADDRINUSE") {
      log(`⚠️ Cổng ${OUTBOUND_PORT} đang bận (EADDRINUSE). Đang chờ giải phóng...`);
      setTimeout(() => process.exit(1), 2000);
    } else {
      log(`⚠️ Lỗi HTTP Server cổng ${OUTBOUND_PORT}: ${err.message}`);
    }
  });

  server.listen(OUTBOUND_PORT, "127.0.0.1", () => {
    log(`🚀 WhatsApp Outbound HTTP Server đang lắng nghe tại http://127.0.0.1:${OUTBOUND_PORT} (/api/send, /api/status)`);
  });
}

// Bắt đầu thực thi
startOutboundServer();
connectToWhatsApp();
