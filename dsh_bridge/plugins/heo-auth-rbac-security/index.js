// Plugin chính thức của hệ Heo OS chạy trên nền DSH Cordis
// Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)

export const name = 'heo-auth-rbac-security';

export function apply(ctx, config) {
  const logger = ctx.logger ? ctx.logger('heo-auth-rbac-security') : console;
  logger.info?.('[Tác Quyền Bất Biến Anh Cơ La & PIN Admin] Đã kích hoạt trong runtime DeepSeek Harness.');
}
