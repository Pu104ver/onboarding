import {useEffect, useState} from 'react';

import styles from './TableFilter.module.scss';

import {ITableFilter} from '@/app/types/Employee';
import {TSelectOption} from '@/app/types/Select';
import {useQueryParams} from '@/shared/hooks/useQueryParams.hook';
import Select from '@/shared/ui/Select';

interface IFilterProps extends ITableFilter {
  field: string;
}

const TableFilter = ({field, options, isMulti, placeholder = ''}: IFilterProps) => {
  const {setQueryParams, getQueryParam, deleteQueryParam} = useQueryParams();

  const [currentSelectValue, setCurrentSelectValue] = useState<
    TSelectOption | TSelectOption[] | null
  >(null);
  const handleSelect = (selectOptions: TSelectOption | TSelectOption[] | null) => {
    const isArrayValue = Array.isArray(selectOptions);

    if (selectOptions === null || (isArrayValue && selectOptions.length === 0)) {
      deleteQueryParam(field);
      setCurrentSelectValue(selectOptions);
      return;
    }

    const value = isArrayValue
      ? `[${selectOptions.map(opt => opt.value.toString()).join(',')}]`
      : selectOptions.value;

    setQueryParams({label: field, value});
    setCurrentSelectValue(selectOptions);
  };

  useEffect(() => {
    setCurrentSelectValue(
      options?.filter(option => getQueryParam(field)?.includes(option.value.toString())) || null,
    );
  }, [field, options]);

  return (
    <div className={styles.wrapper}>
      <Select
        placeholder={placeholder || ''}
        options={options}
        defaultValue={currentSelectValue}
        value={currentSelectValue}
        selectSingleValue={handleSelect}
        isMulti={isMulti}
      />
    </div>
  );
};

export default TableFilter;
