// Plugin chính thức của hệ Heo OS chạy trên nền DSH Cordis
// Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)

export const name = 'heo-provider-deepseek-reasoning';

export function apply(ctx, config) {
  const logger = ctx.logger ? ctx.logger('heo-provider-deepseek-reasoning') : console;
  logger.info?.('[Secondary DeepSeek V3/R1 Reasoning] Đã kích hoạt trong runtime DeepSeek Harness.');
}
