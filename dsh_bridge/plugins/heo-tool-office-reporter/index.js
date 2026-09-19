// Plugin chính thức của hệ Heo OS chạy trên nền DSH Cordis
// Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)

export const name = 'heo-tool-office-reporter';

export function apply(ctx, config) {
  const logger = ctx.logger ? ctx.logger('heo-tool-office-reporter') : console;
  logger.info?.('[Báo Cáo Tài Liệu Word (.docx) & Excel (.xlsx)] Đã kích hoạt trong runtime DeepSeek Harness.');
}
