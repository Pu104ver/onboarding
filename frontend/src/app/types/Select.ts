import {Key} from 'react';
import {MultiValue} from 'react-select';

export type TSelectOption = {
  label: string;
  value: Key;
};

export type TSelectMultiOption = MultiValue<TSelectOption> | null;
