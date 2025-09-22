/**
 * Independent time operation tool to facilitate subsequent switch to dayjs
 */
import dayjs from 'dayjs';

const DATE_TIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';
const DATE_FORMAT = 'YYYY-MM-DD';

/**将传入的日期格式化为日期和时间的字符串 */
export function formatToDateTime(
   date?: dayjs.ConfigType,
   format = DATE_TIME_FORMAT
): string {
   return dayjs(date).format(format);
}
/**将传入的日期格式化为仅包含日期的字符串。 */
export function formatToDate(
   date?: dayjs.ConfigType,
   format = DATE_FORMAT
): string {
   return dayjs(date).format(format);
}

export const dateUtil = dayjs;
