/**
 * 中国节假日数据
 * 包含固定日期节日和农历节日（按公历近似日期）
 */

export interface Holiday {
  name: string;
  emoji: string;
  type: 'festival' | 'memorial' | 'international';
}

// 固定日期节日 (月-日)
const fixedHolidays: Record<string, Holiday> = {
  // 一月
  '01-01': { name: '元旦', emoji: '🎊', type: 'festival' },
  // 二月
  '02-14': { name: '情人节', emoji: '💕', type: 'international' },
  // 三月
  '03-08': { name: '妇女节', emoji: '👩', type: 'international' },
  '03-12': { name: '植树节', emoji: '🌲', type: 'memorial' },
  '03-15': { name: '消费者权益日', emoji: '⚖️', type: 'memorial' },
  // 四月
  '04-01': { name: '愚人节', emoji: '🤡', type: 'international' },
  '04-05': { name: '清明节', emoji: '🌿', type: 'festival' }, // 清明节大约在4月4-6日
  '04-22': { name: '地球日', emoji: '🌍', type: 'international' },
  // 五月
  '05-01': { name: '劳动节', emoji: '💪', type: 'festival' },
  '05-04': { name: '青年节', emoji: '🎓', type: 'memorial' },
  '05-12': { name: '母亲节', emoji: '👩‍👧', type: 'international' }, // 5月第二个周日，这里用近似日期
  // 六月
  '06-01': { name: '儿童节', emoji: '🧒', type: 'festival' },
  '06-16': { name: '父亲节', emoji: '👨‍👧', type: 'international' }, // 6月第三个周日，这里用近似日期
  // 七月
  '07-01': { name: '建党节', emoji: '🎖️', type: 'memorial' },
  // 八月
  '08-01': { name: '建军节', emoji: '⭐', type: 'memorial' },
  // 九月
  '09-10': { name: '教师节', emoji: '📚', type: 'memorial' },
  // 十月
  '10-01': { name: '国庆节', emoji: '🇨🇳', type: 'festival' },
  '10-31': { name: '万圣节', emoji: '🎃', type: 'international' },
  // 十一月
  '11-01': { name: '万圣节', emoji: '🎃', type: 'international' },
  '11-11': { name: '光棍节', emoji: '💔', type: 'international' },
  // 十二月
  '12-24': { name: '平安夜', emoji: '🌟', type: 'international' },
  '12-25': { name: '圣诞节', emoji: '🎄', type: 'international' },
  '12-31': { name: '跨年夜', emoji: '🎆', type: 'festival' },
};

// 2025年农历节日对应的公历日期
// 农历节日每年日期不同，需要手动更新或使用农历库
const lunarHolidays2025: Record<string, Holiday> = {
  '01-29': { name: '春节', emoji: '🧧', type: 'festival' }, // 农历正月初一
  '02-12': { name: '元宵节', emoji: '🏮', type: 'festival' }, // 农历正月十五
  '05-31': { name: '端午节', emoji: '🐲', type: 'festival' }, // 农历五月初五
  '08-29': { name: '七夕节', emoji: '🎋', type: 'festival' }, // 农历七月初七
  '10-06': { name: '中秋节', emoji: '🥮', type: 'festival' }, // 农历八月十五
  '10-29': { name: '重阳节', emoji: '🌺', type: 'festival' }, // 农历九月初九
};

// 2026年农历节日对应的公历日期
const lunarHolidays2026: Record<string, Holiday> = {
  '02-17': { name: '春节', emoji: '🧧', type: 'festival' },
  '03-03': { name: '元宵节', emoji: '🏮', type: 'festival' },
  '06-19': { name: '端午节', emoji: '🐲', type: 'festival' },
  '08-19': { name: '七夕节', emoji: '🎋', type: 'festival' },
  '09-25': { name: '中秋节', emoji: '🥮', type: 'festival' },
  '10-18': { name: '重阳节', emoji: '🌺', type: 'festival' },
};

// 合并所有农历节日
const lunarHolidaysByYear: Record<string, Record<string, Holiday>> = {
  '2025': lunarHolidays2025,
  '2026': lunarHolidays2026,
};

/**
 * 获取指定日期的节假日信息
 * @param date 日期对象或日期字符串 (YYYY-MM-DD)
 * @returns 节假日信息，如果不是节假日则返回 null
 */
export function getHoliday(date: Date | string): Holiday | null {
  let dateObj: Date;
  if (typeof date === 'string') {
    dateObj = new Date(date);
  } else {
    dateObj = date;
  }
  
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  const year = String(dateObj.getFullYear());
  const monthDay = `${month}-${day}`;
  
  // 先检查农历节日（按年份）
  const lunarHolidays = lunarHolidaysByYear[year];
  if (lunarHolidays && lunarHolidays[monthDay]) {
    return lunarHolidays[monthDay];
  }
  
  // 再检查固定日期节日
  if (fixedHolidays[monthDay]) {
    return fixedHolidays[monthDay];
  }
  
  return null;
}

/**
 * 获取指定月份的所有节假日
 * @param year 年份
 * @param month 月份 (1-12)
 * @returns 日期到节假日的映射
 */
export function getHolidaysInMonth(year: number, month: number): Record<number, Holiday> {
  const result: Record<number, Holiday> = {};
  const daysInMonth = new Date(year, month, 0).getDate();
  
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month - 1, day);
    const holiday = getHoliday(date);
    if (holiday) {
      result[day] = holiday;
    }
  }
  
  return result;
}

export default {
  getHoliday,
  getHolidaysInMonth,
};
