import cn from 'classnames';
import {forwardRef, Ref} from 'react';
import ReactSelect, {ActionMeta, GroupBase, MultiValue, SingleValue} from 'react-select';
import SelectDeclaration from 'react-select/dist/declarations/src/Select';
import {StateManagerProps} from 'react-select/dist/declarations/src/useStateManager';

import styles from './Select.module.scss';

import {TSelectOption} from '@/app/types/Select';

export type TSelectProps = StateManagerProps<TSelectOption> & {
  selectSingleValue?: (
    newValue: SingleValue<TSelectOption>,
    actionMeta: ActionMeta<TSelectOption>,
  ) => void;
  selectMultiValues?: (
    newValue: MultiValue<TSelectOption>,
    actionMeta: ActionMeta<TSelectOption>,
  ) => void;
  loading?: boolean;
};

const Select = forwardRef(
  (
    {className, selectSingleValue, selectMultiValues, loading, isDisabled, ...props}: TSelectProps,
    ref: Ref<SelectDeclaration<TSelectOption, boolean, GroupBase<TSelectOption>>> | undefined,
  ) => {
    return (
      <ReactSelect
        className={cn(styles.select, className)}
        onChange={(newValue, actionValue) =>
          selectSingleValue?.(newValue as SingleValue<TSelectOption>, actionValue) ||
          selectMultiValues?.(newValue as MultiValue<TSelectOption>, actionValue)
        }
        ref={ref}
        isSearchable
        isClearable
        isDisabled={loading || isDisabled}
        getOptionValue={option => option.label}
        noOptionsMessage={() => 'Нет данных'}
        loadingMessage={() => 'Загрузка данных...'}
        styles={{
          option: (base, {isSelected, isFocused}) => ({
            ...base,
            fontFamily: 'Inter',
            backgroundColor: isSelected ? '#467fe5' : isFocused ? '#F2F2F2' : '#ffffff',
            cursor: 'pointer',
          }),
          control: base => ({
            ...base,
            cursor: 'pointer',
          }),
        }}
        {...props}
      />
    );
  },
);

export default Select;
