import Calendar from '@/shared/assets/calendar.svg?react';
import ElipsWas from '@/shared/assets/elipsWas.svg?react';
import Handdislike from '@/shared/assets/handdislike.svg?react';
import Handlike from '@/shared/assets/handlike.svg?react';
import Spinner from '@/shared/assets/spinner.svg?react';
import X from '@/shared/assets/x.svg?react';

export const statusObjects = {
  completed: {icon: <Handlike />, text: 'Завершен'},
  expired: {icon: <ElipsWas />, text: 'Просрочен'},
  in_frozen: {icon: <Calendar />, text: 'Не заполнено'},
  in_progress: {icon: <Spinner />, text: 'В процессе'},
  not_started: {icon: <Handdislike />, text: 'Не начато'},
  none: {icon: <X />, text: 'Нет ответа'},
};

export type statusObjectsKeyType = keyof typeof statusObjects;
export const statusObjectsKeys = Object.keys(statusObjects);
