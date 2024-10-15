import cn from 'classnames';

import styles from './TableFilters.module.scss';

import {ColumnsData} from '@/app/types/Employee';
import TableFilter from '@/shared/ui/TableFilter';

interface ITableFiltersProps<T> {
  columns: ColumnsData<T>[];
  isOpened: boolean;
}

const TableFilters = <T,>({columns, isOpened}: ITableFiltersProps<T>) => {
  return (
    <div
      className={cn(styles.filterContainer, {
        [styles.hidden]: !isOpened,
      })}>
      {columns?.map(column => (
        <TableFilter
          key={column.key}
          options={column.filter?.options}
          field={column.key}
          isMulti={column.filter?.isMulti}
          initialValue={column.filter?.initialValue}
          placeholder={column.filter?.placeholder || column.title}
        />
      ))}
    </div>
  );
};

export default TableFilters;
