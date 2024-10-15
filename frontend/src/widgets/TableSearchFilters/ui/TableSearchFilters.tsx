import {ChangeEvent, ReactNode, useEffect, useState} from 'react';

import styles from './TableSearchFilters.module.scss';

import {ColumnsData} from '@/app/types/Employee';
import {TSelectOption} from '@/app/types/Select';
import {useDebounce} from '@/shared/hooks/useDebounce.hook';
import {useQueryParams} from '@/shared/hooks/useQueryParams.hook';
import TableFilters from '@/shared/ui/TableFilters';
import {ITableSearchProps, TableSearch} from '@/widgets/TableSearch/ui/TableSearch';

interface ITableSearchFiltersProps<T> extends Omit<ITableSearchProps, 'placeholder' | 'onChange'> {
  columnsWithFilters: ColumnsData<T>[];
  isOpened: boolean;
  searchField: string;
  searchPlaceholder?: string;
  children?: ReactNode;
}

export const TableSearchFilters = <T,>({
  isOpened,
  columnsWithFilters,
  children,
  searchField,
  searchPlaceholder,
  ...tableSearchProps
}: ITableSearchFiltersProps<T>) => {
  const [search, setSearch] = useState('');

  const {queryParams, setQueryParams} = useQueryParams();
  const debouncedSearch = useDebounce(search);

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  useEffect(() => {
    setQueryParams({label: searchField, value: debouncedSearch});
  }, [debouncedSearch, searchField]);

  useEffect(() => {
    queryParams.length <= 1 &&
      setQueryParams([
        ...columnsWithFilters.reduce<TSelectOption[]>(
          (acc, current) =>
            current.filter?.initialValue
              ? [...acc, {label: current.key, value: current.filter.initialValue}]
              : [...acc],
          [],
        ),
        {label: searchField, value: debouncedSearch},
      ]);
  }, [columnsWithFilters, queryParams]);

  return (
    <>
      <TableFilters isOpened={isOpened} columns={columnsWithFilters} />

      <div className={styles.employeesSearchAndAdd}>
        <TableSearch
          placeholder={searchPlaceholder}
          onChange={handleSearch}
          {...tableSearchProps}
        />

        {children}
      </div>
    </>
  );
};
