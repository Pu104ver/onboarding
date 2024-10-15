import {useEffect, useMemo, useState} from 'react';
import {StateManagerProps} from 'react-select/dist/declarations/src/useStateManager';

import style from './EditSelect.module.scss';

import {TSelectOption} from '@/app/types/Select';
import CheckMarkIcon from '@/shared/assets/checkmark.svg?react';
import PenIcon from '@/shared/assets/pencil.svg?react';
import XIcon from '@/shared/assets/x.svg?react';
import {useClickEsc} from '@/shared/hooks/useClickEsc.hook';
import Select from '@/shared/ui/Select';
interface EditProps extends StateManagerProps<TSelectOption> {
  field: string;
  initialValue?: string;
  changeData: (field: string, text: string) => void;
  selectArray?: TSelectOption[];
}
const EditSelect = ({field, initialValue, changeData, selectArray, ...props}: EditProps) => {
  const [isChange, setIsChange] = useState(false);

  const [selectValue, setSelectValue] = useState<TSelectOption>();

  const initialSelect = useMemo(() => {
    return selectArray?.find(status => status.value?.toString() === initialValue);
  }, [initialValue, selectArray]);

  useEffect(() => {
    setSelectValue(initialSelect);
  }, [initialSelect, selectArray]);

  useClickEsc(isChange, setIsChange);
  const closeEdit = () => {
    setIsChange(false);
    setSelectValue(initialSelect);
  };

  const handleChange = () => {
    selectValue && changeData(field, selectValue.value.toString());
    setIsChange(false);
  };

  return (
    <div className={style.Edit}>
      {isChange ? (
        <div className={style.editTools}>
          <Select
            onChange={select => {
              setSelectValue(select as TSelectOption);
            }}
            isClearable={false}
            options={selectArray}
            value={selectValue}
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
          {selectValue?.label}
          <PenIcon className={style.icon} onClick={() => setIsChange(true)} />
        </>
      )}
    </div>
  );
};

export default EditSelect;
