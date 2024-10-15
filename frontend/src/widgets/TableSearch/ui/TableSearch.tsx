import styles from './TableSearch.module.scss';

import SearchIcon from '@/shared/assets/search.svg?react';
import Input from '@/shared/ui/Input';
import {InputProps} from '@/shared/ui/Input/ui/Input';

export interface ITableSearchProps extends InputProps {}

export const TableSearch = ({onChange, placeholder, style, ...props}: ITableSearchProps) => {
  return (
    <div style={style} className={styles.EmployeesSearch}>
      <Input icon={<SearchIcon />} placeholder={placeholder} onChange={onChange} {...props} />
    </div>
  );
};
