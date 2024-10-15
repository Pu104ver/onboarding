import {useSearchParams} from 'react-router-dom';

import {useEffect, useState} from 'react';

import styles from './TableFilter.module.scss';

import {ITableFilter} from '@/app/types/Employee';
import {TSelectOption} from '@/app/types/Select';
import {useQueryParams} from '@/shared/hooks/useQueryParams.hook';
import Select from '@/shared/ui/Select';

interface IFilterProps extends ITableFilter {
  field: string;
}

const TableFilter = ({field, options, placeholder = ''}: IFilterProps) => {
  const {setQueryParams, deleteQueryParam} = useQueryParams();
  const [searchParams] = useSearchParams();

  const [currentSelectValue, setCurrentSelectValue] = useState<TSelectOption | null>(null);

  const handleSelect = (option: TSelectOption | null) => {
    if (option) {
      setQueryParams({label: field, value: option.value});
    } else {
      deleteQueryParam(field);
    }

    setCurrentSelectValue(option);
  };

  useEffect(() => {
    setCurrentSelectValue(
      options?.find(option => option.value.toString() === searchParams.get(field)) ?? null,
    );
  }, [field, options, searchParams]);

  return (
    <div className={styles.wrapper}>
      <Select
        placeholder={placeholder || ''}
        options={options}
        defaultValue={currentSelectValue}
        value={currentSelectValue}
        selectSingleValue={handleSelect}
      />
    </div>
  );
};

export default TableFilter;
