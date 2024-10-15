import {Key} from 'react';

import {TSelectOption} from '@/app/types/Select';

interface IData {
  name?: string;
  full_name?: string;
  id: Key;
}

export const convertToSelectOptions = <T extends IData>(data?: T[]): TSelectOption[] =>
  data?.map(item => ({
    label: item.name ?? item.full_name ?? 'Значение не найдено"',
    value: item.id,
  })) ?? [];
