import {ReactNode, useEffect, useState} from 'react';
import {StateManagerProps} from 'react-select/dist/declarations/src/useStateManager';

import style from './EditMultipleSelect.module.scss';

import {TSelectOption} from '@/app/types/Select';
import CheckMarkIcon from '@/shared/assets/checkmark.svg?react';
import PenIcon from '@/shared/assets/pencil.svg?react';
import XIcon from '@/shared/assets/x.svg?react';
import {useClickEsc} from '@/shared/hooks/useClickEsc.hook';
import Select from '@/shared/ui/Select';

interface EditMultipleSelect extends StateManagerProps<TSelectOption> {
  field: string;
  initialValueArray?: TSelectOption[];
  changeData: (field: string, text: string[]) => void;
  selectArray?: TSelectOption[];
  render?: (value: TSelectOption) => ReactNode;
}
const EditMultipleSelect = ({
  field,
  initialValueArray,
  changeData,
  selectArray,
  render,
  ...props
}: EditMultipleSelect) => {
  const [isChange, setIsChange] = useState(false);

  const [selectValue, setSelectValue] = useState<TSelectOption[]>(initialValueArray || []);

  useEffect(() => {
    setSelectValue(initialValueArray || []);
  }, [initialValueArray]);

  useClickEsc(isChange, setIsChange);

  const closeEdit = () => {
    setIsChange(false);
    setSelectValue(initialValueArray || []);
  };

  const handleChange = () => {
    selectValue &&
      changeData(
        field,
        selectValue?.map(({value}) => value.toString()),
      );
    setIsChange(false);
  };

  return (
    <div className={style.EditMultiple}>
      {isChange ? (
        <div className={style.editTools}>
          <Select
            className={style.select}
            onChange={select => {
              setSelectValue(select as TSelectOption[]);
            }}
            isClearable={false}
            options={selectArray}
            value={selectValue}
            isMulti
            {...props}
          />
          <XIcon onClick={closeEdit} />
          <CheckMarkIcon
            className={style.checkmark}
            onClick={() => {
              setIsChange(false);
              handleChange();
            }}
          />
        </div>
      ) : (
        <>
          {selectValue.length > 0
            ? selectValue.map(item => (render ? render(item) : item.label + ' '))
            : 'Не назначено'}

          <PenIcon className={style.icon} onClick={() => setIsChange(true)} />
        </>
      )}
    </div>
  );
};

export default EditMultipleSelect;
