// Plugin chính thức của hệ Heo OS chạy trên nền DSH Cordis
// Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)

export const name = 'heo-provider-antigravity-brain';

export function apply(ctx, config) {
  const logger = ctx.logger ? ctx.logger('heo-provider-antigravity-brain') : console;
  logger.info?.('[Core Agent Google Antigravity CLI (0đ API)] Đã kích hoạt trong runtime DeepSeek Harness.');
}
