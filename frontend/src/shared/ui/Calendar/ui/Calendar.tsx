import {ru} from 'date-fns/locale/ru';
import {Ref, forwardRef} from 'react';
import DatePicker, {DatePickerProps} from 'react-datepicker';
import {registerLocale} from 'react-datepicker';
registerLocale('ru', ru);

import styles from './Calendar.module.scss';

const Calendar = forwardRef(({...props}: DatePickerProps, ref: Ref<DatePicker>) => {
  return (
    <div className="react-datepicker-container">
      <DatePicker
        className={styles.calendar}
        dateFormat="dd.MM.yyyy"
        timeFormat="HH:mm"
        isClearable
        shouldCloseOnSelect={false}
        calendarClassName="react-datepicker-calendarClassName"
        locale="ru"
        ref={ref}
        {...props}
      />
    </div>
  );
});

export default Calendar;
