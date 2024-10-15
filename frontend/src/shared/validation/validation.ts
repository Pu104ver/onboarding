export const checkEmpty = (value: string | number, msg: string) =>
  value.toString().trim().length > 0 || msg;

export const checkOnlyLetters = (value: string | number, msg: string) =>
  !/[^\p{L}\s]/gu.test(value.toString().trim()) || msg;

export const checkOnlyLettersAndDash = (value: string | number, msg: string) =>
  !/[^\p{L}\s-]/gu.test(value.toString().trim()) || msg;

export const checkOnlyEnglishLetters = (value: string | number, msg: string) =>
  /^[a-zA-Z]+$/.test(value.toString().trim()) || msg;

export const checkEmail = (value: string | number, msg: string) =>
  /^[\w-.]+@([\w-]+.)+[\w-]{2,4}$/.test(value.toString().trim()) || msg;

// Документация Telegram, где говорится какие символы разрешены для никнеймов - https://core.telegram.org/method/account.checkUsername
export const checkTelegramNickname = (value: string | number, msg: string) =>
  /^[A-Za-z\d_]{5,32}$/.test(value.toString().trim()) || msg;
