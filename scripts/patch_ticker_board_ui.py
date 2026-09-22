import re

with open("heo_harness/plugins/ui_dashboard/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Thay thế khối code renderMatchmakerMatchesList và các hàm liên quan
old_start = "// -----------------------------------------------------------------------------\n// TAB 1: CẦU NỐI GHÉP CẶP & THANG ĐIỂM (MATCHMAKER BRIDGE VIEW)\n// -----------------------------------------------------------------------------"
old_end = "// -----------------------------------------------------------------------------\n// QUYẾT ĐỊNH NEXT ACTION CỦA SẾP RYAN\n// -----------------------------------------------------------------------------"

pattern = r"// -+\s*\n// TAB 1: CẦU NỐI GHÉP CẶP[\s\S]*?(?=// -+\s*\n// QUYẾT ĐỊNH NEXT ACTION)"

new_ticker_code = '''// -----------------------------------------------------------------------------
// TAB 1: BẢNG ĐIỆN MẬU DỊCH & GHÉP NỐI CUNG - CẦU (TRADING TICKER BOARD)
// Rút gọn thành từng dòng như bảng điện chứng khoán - Bấm dòng nào bung dòng đó
// -----------------------------------------------------------------------------

matchmakerState.expandedMatchId = null;

function toggleMatchDetail(matchId) {
  if (matchmakerState.expandedMatchId === matchId) {
    matchmakerState.expandedMatchId = null;
  } else {
    matchmakerState.expandedMatchId = matchId;
  }
  renderMatchmakerActiveTab();
}

function renderMatchmakerMatchesList(container) {
  const matches = matchmakerState.matches;
  if (!matches || matches.length === 0) {
    container.innerHTML = `
      <div class="card" style="padding:40px;text-align:center;color:#94a3b8">
        <i class="ph ph-magnifying-glass" style="font-size:36px;color:#64748b;margin-bottom:12px;display:block"></i>
        Không tìm thấy cơ hội mậu dịch nào thỏa mãn bộ lọc hiện tại.
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="card" style="padding:0;overflow:hidden;background:rgba(15,23,42,0.95);border:1px solid rgba(255,255,255,0.12);border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,0.4)">
      
      <!-- BẢNG ĐIỆN THƯƠNG MẠI MẬU DỊCH (TICKER TABLE) -->
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:left">
          
          <!-- TIÊU ĐỀ CỘT BẢNG ĐIỆN -->
          <thead>
            <tr style="background:rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.15);color:#94a3b8;text-transform:uppercase;font-size:10.5px;letter-spacing:0.5px">
              <th style="padding:12px 14px;width:110px">MÃ & HẠNG</th>
              <th style="padding:12px 14px">NGUỒN CẦU (BÊN CẦN)</th>
              <th style="padding:12px 14px;text-align:right;width:130px">NGÂN SÁCH MUA</th>
              <th style="padding:12px 14px">NGUỒN CUNG (BÊN CÓ)</th>
              <th style="padding:12px 14px;text-align:right;width:130px">GIÁ CHÀO BÁN</th>
              <th style="padding:12px 14px;text-align:right;width:150px">CHÊNH LỆCH LỜI GỘP</th>
              <th style="padding:12px 14px;text-align:center;width:100px">ĐIỂM / KHỚP</th>
              <th style="padding:12px 14px;text-align:center;width:110px">TRẠNG THÁI</th>
              <th style="padding:12px 14px;text-align:center;width:40px"></th>
            </tr>
          </thead>

          <tbody>
            ${matches.map(m => {
              const isExpanded = matchmakerState.expandedMatchId === m.id;
              const isDiamond = m.rating_tier === 'TIER_A_PLUS';
              const isGold = m.rating_tier === 'TIER_A';
              const tierBadgeColor = isDiamond ? 'linear-gradient(135deg, #0284c7, #6366f1)' : (isGold ? 'linear-gradient(135deg, #d97706, #f59e0b)' : 'rgba(255,255,255,0.1)');
              const tierBadgeText = isDiamond ? '💎 A+' : (isGold ? '🥇 A' : '🥈 B');
              
              const statusBg = m.action_status === 'PENDING' ? 'rgba(234,179,8,0.15)' : (m.action_status === 'ARBITRAGED' ? 'rgba(52,211,153,0.15)' : 'rgba(56,189,248,0.15)');
              const statusColor = m.action_status === 'PENDING' ? '#fbbf24' : (m.action_status === 'ARBITRAGED' ? '#34d399' : '#38bdf8');
              const statusText = m.action_status === 'PENDING' ? '⏳ Chờ Duyệt' : (m.action_status === 'ARBITRAGED' ? '💼 Đang Ôm Deal' : (m.action_status === 'INTRODUCED' ? '🤝 Đã Kết Nối' : '📝 Đã Soạn Báo Giá'));

              return `
                <!-- 1 DÒNG BẢNG ĐIỆN CHÍNH (CLICK ĐỂ BUNG CHI TIẾT) -->
                <tr onclick="toggleMatchDetail('${m.id}')" style="cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.06);background:${isExpanded ? 'rgba(99,102,241,0.1)' : 'transparent'};transition:background 0.15s" onmouseover="this.style.background='rgba(255,255,255,0.04)'" onmouseout="this.style.background='${isExpanded ? 'rgba(99,102,241,0.1)' : 'transparent'}'">
                  
                  <!-- Mã & Hạng -->
                  <td style="padding:10px 14px">
                    <div style="display:flex;align-items:center;gap:6px">
                      <span style="font-family:var(--mono);font-size:11.5px;font-weight:700;color:#38bdf8">${m.id}</span>
                      <span class="badge" style="background:${tierBadgeColor};color:#fff;font-weight:800;font-size:9.5px;padding:2px 5px">${tierBadgeText}</span>
                    </div>
                    <div style="font-size:10px;color:#64748b;margin-top:2px">${escapeHtml(m.demand_category || '')}</div>
                  </td>

                  <!-- Nguồn Cầu -->
                  <td style="padding:10px 14px">
                    <div style="font-weight:700;color:#f8fafc;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:260px" title="${escapeHtml(m.demand_title || '')}">
                      ${escapeHtml(m.demand_title || '')}
                    </div>
                    <div style="font-size:11px;color:#94a3b8;margin-top:2px">
                      👤 <b>${escapeHtml(m.demand_contact || '')}</b> <span style="color:#64748b">(${escapeHtml(m.demand_group || '')})</span>
                    </div>
                  </td>

                  <!-- Ngân Sách Mua -->
                  <td style="padding:10px 14px;text-align:right">
                    <span style="font-weight:800;font-size:12.5px;color:#38bdf8">
                      ${(m.demand_budget || 0).toLocaleString('vi-VN')} ₫
                    </span>
                    <div style="font-size:10px;color:#f43f5e">🔥 Heat ${m.demand_heat || 80}°</div>
                  </td>

                  <!-- Nguồn Cung -->
                  <td style="padding:10px 14px">
                    <div style="font-weight:700;color:#f8fafc;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:260px" title="${escapeHtml(m.supply_title || '')}">
                      ${escapeHtml(m.supply_title || '')}
                    </div>
                    <div style="font-size:11px;color:#94a3b8;margin-top:2px">
                      🏢 <b>${escapeHtml(m.supply_provider || '')}</b> <span style="color:#64748b">(${escapeHtml(m.supply_group || '')})</span>
                    </div>
                  </td>

                  <!-- Giá Chào Bán -->
                  <td style="padding:10px 14px;text-align:right">
                    <span style="font-weight:800;font-size:12.5px;color:#34d399">
                      ${(m.supply_price || 0).toLocaleString('vi-VN')} ₫
                    </span>
                    <div style="font-size:10px;color:#10b981">Độ tin ${m.supply_confidence || 90}%</div>
                  </td>

                  <!-- Chênh Lệch Lời Gộp (Spread) -->
                  <td style="padding:10px 14px;text-align:right">
                    <div style="font-weight:900;font-size:13.5px;color:#34d399">
                      +${(m.arbitrage_spread_val || 0).toLocaleString('vi-VN')} ₫
                    </div>
                    <span class="badge" style="background:rgba(52,211,153,0.15);color:#34d399;font-size:9.5px;padding:1px 5px">
                      +${m.arbitrage_spread_pct}%
                    </span>
                  </td>

                  <!-- Thang Điểm & Khớp -->
                  <td style="padding:10px 14px;text-align:center">
                    <div style="font-weight:900;font-size:15px;color:${m.total_rating >= 85 ? '#34d399' : '#fbbf24'}">
                      ${m.total_rating}đ
                    </div>
                    <div style="font-size:10px;color:#94a3b8">${m.match_score}% khớp</div>
                  </td>

                  <!-- Trạng Thái -->
                  <td style="padding:10px 14px;text-align:center">
                    <span class="badge" style="background:${statusBg};color:${statusColor};font-size:10px;white-space:nowrap">
                      ${statusText}
                    </span>
                  </td>

                  <!-- Nút Mũi Tên Bung/Thu Gọn -->
                  <td style="padding:10px 14px;text-align:center">
                    <i class="ph ${isExpanded ? 'ph-caret-up' : 'ph-caret-down'}" style="font-size:14px;color:${isExpanded ? '#38bdf8' : '#64748b'}"></i>
                  </td>

                </tr>

                <!-- PANEL BUNG CHI TIẾT KHI CLICK DÒNG ĐÓ -->
                ${isExpanded ? `
                  <tr style="background:rgba(10,15,30,0.85);border-bottom:2px solid rgba(99,102,241,0.3)">
                    <td colspan="9" style="padding:18px 22px">
                      
                      <div style="display:flex;flex-direction:column;gap:16px">
                        
                        <!-- Header Chi Tiết & Lý Giải Trí Tuệ AI -->
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:12px 16px">
                          <div style="display:flex;align-items:center;gap:8px">
                            <i class="ph ph-sparkle" style="color:#c084fc;font-size:18px"></i>
                            <div>
                              <div style="font-size:11px;font-weight:700;color:#c084fc;text-transform:uppercase">LẬP LUẬN ĐỐI SOÁT CỦA AI COPILOT:</div>
                              <div style="font-size:12.5px;color:#f8fafc;margin-top:2px;line-height:1.5">${escapeHtml(m.explainable_reason || '')}</div>
                            </div>
                          </div>
                          <div style="text-align:right;white-space:nowrap;margin-left:20px">
                            <span style="font-size:11px;color:#94a3b8">Đề xuất tối ưu:</span>
                            <div style="font-size:12px;font-weight:700;color:#fbbf24;margin-top:2px">
                              ${m.next_action_suggested === 'TRADE_ARBITRAGE' ? '💼 Đứng giữa ôm trọn biên độ lời' : (m.next_action_suggested === 'INTRODUCE_COMMISSION' ? '🤝 Giới thiệu ăn hoa hồng kết nối 3%' : '📝 Soạn đề xuất giải pháp trực tiếp')}
                            </div>
                          </div>
                        </div>

                        <!-- 2 Cột Đối Chiếu Cung & Cầu Chi Tiết Kèm Tin Nhắn Gốc -->
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
                          
                          <!-- Khối Bên Cầu -->
                          <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(56,189,248,0.2);border-radius:8px;padding:14px">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                              <span style="font-weight:700;font-size:12px;color:#38bdf8"><i class="ph ph-arrow-down-left"></i> CHI TIẾT NGUỒN CẦU (BÊN CẦN)</span>
                              <span class="badge danger" style="font-size:9.5px">🔥 Heat ${m.demand_heat || 80}°</span>
                            </div>
                            <div style="font-size:13px;font-weight:700;color:#f8fafc;margin-bottom:6px">${escapeHtml(m.demand_title || '')}</div>
                            <div style="font-size:11.5px;color:#cbd5e1;line-height:1.4;margin-bottom:10px">${escapeHtml(m.demand_desc || '')}</div>
                            
                            <div style="background:rgba(0,0,0,0.4);padding:8px 10px;border-radius:6px;font-size:11.5px;color:#94a3b8;font-style:italic;margin-bottom:10px;border-left:2px solid #38bdf8">
                              "${escapeHtml(m.demand_raw || 'Không có trích dẫn chat gốc')}"
                            </div>

                            <div style="display:flex;justify-content:space-between;font-size:11px;color:#94a3b8">
                              <span>Số lượng: <b style="color:#fff">${escapeHtml(m.demand_quantity || 'Chưa rõ')}</b></span>
                              <span>Ngân sách: <b style="color:#38bdf8;font-size:12px">${(m.demand_budget||0).toLocaleString()} ₫</b></span>
                            </div>
                          </div>

                          <!-- Khối Bên Cung -->
                          <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(52,211,153,0.2);border-radius:8px;padding:14px">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                              <span style="font-weight:700;font-size:12px;color:#34d399"><i class="ph ph-arrow-up-right"></i> CHI TIẾT NGUỒN CUNG (BÊN CÓ)</span>
                              <span class="badge good" style="font-size:9.5px">Độ Tin ${m.supply_confidence || 90}%</span>
                            </div>
                            <div style="font-size:13px;font-weight:700;color:#f8fafc;margin-bottom:6px">${escapeHtml(m.supply_title || '')}</div>
                            <div style="font-size:11.5px;color:#cbd5e1;line-height:1.4;margin-bottom:10px">${escapeHtml(m.supply_desc || '')}</div>
                            
                            <div style="background:rgba(0,0,0,0.4);padding:8px 10px;border-radius:6px;font-size:11.5px;color:#94a3b8;font-style:italic;margin-bottom:10px;border-left:2px solid #34d399">
                              "${escapeHtml(m.supply_raw || 'Không có trích dẫn chat gốc')}"
                            </div>

                            <div style="display:flex;justify-content:space-between;font-size:11px;color:#94a3b8">
                              <span>Sẵn kho: <b style="color:#fff">${escapeHtml(m.supply_capacity || 'Có sẵn')}</b></span>
                              <span>Giá chào bán: <b style="color:#34d399;font-size:12px">${(m.supply_price||0).toLocaleString()} ₫</b></span>
                            </div>
                          </div>

                        </div>

                        <!-- THANH HÀNH ĐỘNG NEXT ACTION CỦA SẾP -->
                        <div style="background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center">
                          <div style="font-size:11.5px;color:#cbd5e1">
                            <i class="ph ph-check-circle" style="color:#34d399"></i> Nhật ký chỉ thị: <b>${escapeHtml(m.action_notes || 'Chưa thực thi hành động')}</b>
                          </div>

                          <div style="display:flex;align-items:center;gap:8px">
                            <button class="btn sm" onclick="event.stopPropagation(); promptExecuteMatchAction('${m.id}', 'INTRODUCE_COMMISSION')" style="font-size:11.5px;background:rgba(56,189,248,0.15);border:1px solid rgba(56,189,248,0.3);color:#38bdf8">
                              <i class="ph ph-users-three"></i> 🤝 Kết Nối 2 Bên (Hoa Hồng 3%)
                            </button>

                            <button class="btn sm" onclick="event.stopPropagation(); promptExecuteMatchAction('${m.id}', 'TRADE_ARBITRAGE')" style="font-size:11.5px;background:rgba(52,211,153,0.15);border:1px solid rgba(52,211,153,0.3);color:#34d399">
                              <i class="ph ph-briefcase"></i> 💼 Đứng Giữa Ôm Deal (Thương Mại)
                            </button>

                            <button class="btn sm" onclick="event.stopPropagation(); promptExecuteMatchAction('${m.id}', 'VERIFY_MORE')" style="font-size:11.5px;background:rgba(234,179,8,0.15);border:1px solid rgba(234,179,8,0.3);color:#fbbf24">
                              <i class="ph ph-magnifying-glass"></i> 🔍 Chat Xác Thực Thêm
                            </button>

                            <button class="btn sm" onclick="event.stopPropagation(); promptExecuteMatchAction('${m.id}', 'CREATE_PROPOSAL')" style="font-size:11.5px;background:rgba(192,132,252,0.15);border:1px solid rgba(192,132,252,0.3);color:#c084fc">
                              <i class="ph ph-file-text"></i> 📝 Soạn Báo Giá
                            </button>

                            <button class="btn sm danger" onclick="event.stopPropagation(); executeMatchActionDirect('${m.id}', 'DISMISS', 'Sếp bỏ qua cơ hội')" title="Bỏ qua">
                              <i class="ph ph-x"></i> Bỏ Qua
                            </button>

                            <button class="btn sm" onclick="event.stopPropagation(); toggleMatchDetail('${m.id}')" style="font-size:11px">
                              Thu Gọn ✕
                            </button>
                          </div>
                        </div>

                      </div>

                    </td>
                  </tr>
                ` : ''}
              `;
            }).join('')}
          </tbody>

        </table>
      </div>

    </div>
  `;
}

// -----------------------------------------------------------------------------
// TAB 2: KHO NGUỒN CẦU (BẢNG ĐIỆN DEMANDS STREAM)
// -----------------------------------------------------------------------------
function renderMatchmakerDemandsList(container) {
  const demands = matchmakerState.demands;
  container.innerHTML = `
    <div class="card" style="padding:0;overflow:hidden;background:rgba(15,23,42,0.95);border:1px solid rgba(255,255,255,0.12);border-radius:10px">
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:left">
          <thead>
            <tr style="background:rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.15);color:#94a3b8;text-transform:uppercase;font-size:10.5px">
              <th style="padding:12px 14px">MÃ</th>
              <th style="padding:12px 14px">NGÀNH HÀNG</th>
              <th style="padding:12px 14px">NHU CẦU MUA</th>
              <th style="padding:12px 14px">NGƯỜI HỎI & GROUP NGUỒN</th>
              <th style="padding:12px 14px;text-align:right">SỐ LƯỢNG</th>
              <th style="padding:12px 14px;text-align:right">NGÂN SÁCH</th>
              <th style="padding:12px 14px;text-align:center">NHIỆT ĐỘ</th>
              <th style="padding:12px 14px;text-align:center">THAO TÁC</th>
            </tr>
          </thead>
          <tbody>
            ${demands.map(d => `
              <tr style="border-bottom:1px solid rgba(255,255,255,0.06)">
                <td style="padding:10px 14px;font-family:var(--mono);color:#38bdf8;font-weight:700">${d.id}</td>
                <td style="padding:10px 14px"><span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:10px">${escapeHtml(d.category)}</span></td>
                <td style="padding:10px 14px;font-weight:600;color:#f8fafc">${escapeHtml(d.title)}</td>
                <td style="padding:10px 14px;color:#94a3b8"><b>${escapeHtml(d.contact_name)}</b> <span style="font-size:10.5px;color:#64748b">(${escapeHtml(d.source_group)})</span></td>
                <td style="padding:10px 14px;text-align:right;color:#fff">${escapeHtml(d.quantity)}</td>
                <td style="padding:10px 14px;text-align:right;font-weight:700;color:#38bdf8">${(d.target_price||0).toLocaleString()} ₫</td>
                <td style="padding:10px 14px;text-align:center"><span class="badge danger" style="font-size:10px">🔥 ${d.heat_score}°</span></td>
                <td style="padding:10px 14px;text-align:center">
                  <button class="btn sm primary" onclick="switchMatchmakerTab('matches')" style="font-size:10.5px">
                    <i class="ph ph-handshake"></i> Khớp Nối
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// -----------------------------------------------------------------------------
// TAB 3: KHO NGUỒN CUNG (BẢNG ĐIỆN SUPPLIES STREAM)
// -----------------------------------------------------------------------------
function renderMatchmakerSuppliesList(container) {
  const supplies = matchmakerState.supplies;
  container.innerHTML = `
    <div class="card" style="padding:0;overflow:hidden;background:rgba(15,23,42,0.95);border:1px solid rgba(255,255,255,0.12);border-radius:10px">
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:left">
          <thead>
            <tr style="background:rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.15);color:#94a3b8;text-transform:uppercase;font-size:10.5px">
              <th style="padding:12px 14px">MÃ</th>
              <th style="padding:12px 14px">NGÀNH HÀNG</th>
              <th style="padding:12px 14px">NĂNG LỰC / NGUỒN HÀNG</th>
              <th style="padding:12px 14px">ĐƠN VỊ CUNG CẤP & KHO</th>
              <th style="padding:12px 14px;text-align:right">SẴN KHO</th>
              <th style="padding:12px 14px;text-align:right">GIÁ CHÀO</th>
              <th style="padding:12px 14px;text-align:center">ĐỘ TIN CẬY</th>
              <th style="padding:12px 14px;text-align:center">THAO TÁC</th>
            </tr>
          </thead>
          <tbody>
            ${supplies.map(s => `
              <tr style="border-bottom:1px solid rgba(255,255,255,0.06)">
                <td style="padding:10px 14px;font-family:var(--mono);color:#34d399;font-weight:700">${s.id}</td>
                <td style="padding:10px 14px"><span class="badge" style="background:rgba(52,211,153,0.15);color:#34d399;font-size:10px">${escapeHtml(s.category)}</span></td>
                <td style="padding:10px 14px;font-weight:600;color:#f8fafc">${escapeHtml(s.title)}</td>
                <td style="padding:10px 14px;color:#94a3b8"><b>${escapeHtml(s.provider_name)}</b> <span style="font-size:10.5px;color:#64748b">(${escapeHtml(s.source_group)})</span></td>
                <td style="padding:10px 14px;text-align:right;color:#fff">${escapeHtml(s.capacity)}</td>
                <td style="padding:10px 14px;text-align:right;font-weight:700;color:#34d399">${(s.offered_price||0).toLocaleString()} ₫</td>
                <td style="padding:10px 14px;text-align:center"><span class="badge good" style="font-size:10px">✓ ${s.confidence_score}%</span></td>
                <td style="padding:10px 14px;text-align:center">
                  <button class="btn sm primary" onclick="switchMatchmakerTab('matches')" style="font-size:10.5px">
                    <i class="ph ph-handshake"></i> Khớp Nối
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
'''

if re.search(pattern, html):
    html = re.sub(pattern, new_ticker_code, html)
    with open("heo_harness/plugins/ui_dashboard/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Ticker board UI successfully applied to dashboard.html!")
else:
    print("Error: Pattern not found in dashboard.html")
