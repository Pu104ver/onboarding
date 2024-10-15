import {format} from 'date-fns';
import {useState} from 'react';
import {DatePickerProps} from 'react-datepicker';

import styles from './EditDate.module.scss';

import CheckMarkIcon from '@/shared/assets/checkmark.svg?react';
import PenIcon from '@/shared/assets/pencil.svg?react';
import XIcon from '@/shared/assets/x.svg?react';
import {
  DATE_FOR_BACKEND,
  DATE_FOR_BACKEND_WITH_TIME,
  RUS_DATE,
  RUS_DATE_WITH_TIME,
} from '@/shared/const/DateStrings';
import {useClickEsc} from '@/shared/hooks/useClickEsc.hook';
import Calendar from '@/shared/ui/Calendar';

type EditProps = DatePickerProps & {
  field: string;
  initialDate?: Date | string | null;
  changeData: (field: string, text: string) => void;
  selectsRange?: never;
  selectsMultiple?: never;
  showTimeSelect?: boolean;
};
const EditDate = ({field, changeData, initialDate, showTimeSelect, ...props}: EditProps) => {
  const formatDate = showTimeSelect ? RUS_DATE_WITH_TIME : RUS_DATE;
  const formatDateForBackend = showTimeSelect ? DATE_FOR_BACKEND_WITH_TIME : DATE_FOR_BACKEND;
  const [isChange, setIsChange] = useState(false);
  const [date, setDate] = useState(
    initialDate ? new Date(format(initialDate, formatDateForBackend)) : null,
  );
  useClickEsc(isChange, setIsChange);

  const closeEdit = () => {
    setIsChange(false);
    setDate(initialDate ? new Date(format(initialDate, formatDateForBackend)) : null);
  };

  const handleChange = () => {
    date &&
      changeData(field, showTimeSelect ? date.toISOString() : format(date, formatDateForBackend));
    setIsChange(false);
  };

  return (
    <div className={styles.Edit}>
      {isChange ? (
        <div className={styles.editTools}>
          <Calendar
            showTimeSelect={showTimeSelect}
            selected={date}
            onChange={newDate => {
              setDate(newDate);
            }}
            {...props}
          />

          <XIcon onClick={closeEdit} />

          <CheckMarkIcon
            className={styles.checkmark}
            onClick={() => {
              setIsChange(false);
              handleChange();
            }}
          />
        </div>
      ) : (
        <>
          {initialDate ? format(date || initialDate, formatDate) : 'не назначено'}
          <PenIcon className={styles.icon} onClick={() => setIsChange(true)} />
        </>
      )}
    </div>
  );
};

export default EditDate;
