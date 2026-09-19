// Plugin chính thức của hệ Heo OS chạy trên nền DSH Cordis
// Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)

export const name = 'heo-channel-zalo-gateway';

export function apply(ctx, config) {
  const logger = ctx.logger ? ctx.logger('heo-channel-zalo-gateway') : console;
  logger.info?.('[Cầu Nối Zalo Cá Nhân & Bot 2 Chiều] Đã kích hoạt trong runtime DeepSeek Harness.');
}
