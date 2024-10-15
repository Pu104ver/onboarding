export const convertDateFromBackToFront = (date?: string): string => {
  // 2024-08-28T12:33:56.979105+03:00 -> ['2024-08-28', '12:33:56.979105+03:00']
  const splittedDate = date?.split('T');

  // 2024-08-28 -> 28.08.2024
  const resultDate = splittedDate?.at(0)?.split('-').reverse().join('.') || '';

  // 12:33:56.979105+03:00 -> 12:33:56
  const resultTime = splittedDate?.at(1)?.split('.')[0] || '';

  // 28.08.2024 12:33:56
  return `${resultDate} ${resultTime}`;
};
