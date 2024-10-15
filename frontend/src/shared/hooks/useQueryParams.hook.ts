import {useLocation, useSearchParams} from 'react-router-dom';

import {useEffect, useState} from 'react';

import {useAppDispatch, useAppSelector} from '@/app/store/hooks';
import {selectOffset, setOffset} from '@/app/store/slices/filters';
import {TSelectOption} from '@/app/types/Select';

const convertQueryParams = (prevParams: URLSearchParams, newParams: TSelectOption[]) => {
  const result = new Map<string, string>();
  newParams.forEach(param => result.set(param.label, param.value.toString()));

  return {...Object.fromEntries(prevParams), ...Object.fromEntries(result)};
};

export const useQueryParams = () => {
  const {search} = useLocation();
  const dispatch = useAppDispatch();
  const [queryParams, setSearchParams] = useSearchParams();

  const [isOffsetReset, setIsOffsetReset] = useState(false);
  const offset = useAppSelector(selectOffset);

  useEffect(() => {
    offset === 0 && setIsOffsetReset(true);
  }, [offset]);

  const setQueryParams = (newParams: TSelectOption | TSelectOption[]) => {
    const paramsArray = Array.isArray(newParams) ? newParams : [newParams];

    dispatch(setOffset(0));
    setSearchParams(prevParams => {
      return {
        ...convertQueryParams(prevParams, paramsArray),
      };
    });
  };

  const getQueryParam = (searchValue: string) => queryParams.get(searchValue);

  const hasQueryParam = (query: string) => queryParams.has(query);

  const deleteQueryParam = (label: string) => {
    dispatch(setOffset(0));
    setSearchParams(params => {
      params.delete(label);
      return params;
    });
  };

  return {
    queryParams: search.length > 0 ? search : '?',
    setQueryParams,
    getQueryParam,
    hasQueryParam,
    deleteQueryParam,
    isOffsetReset,
  };
};
