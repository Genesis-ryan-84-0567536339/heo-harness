// Plugin chính thức của hệ Heo OS chạy trên nền DSH Cordis
// Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)

export const name = 'heo-ui-dashboard-executive';

export function apply(ctx, config) {
  const logger = ctx.logger ? ctx.logger('heo-ui-dashboard-executive') : console;
  logger.info?.('[Giao Diện Điều Hành V6 Executive Intelligence OS] Đã kích hoạt trong runtime DeepSeek Harness.');
}
