import {useLocation, useSearchParams} from 'react-router-dom';

import {TSelectOption} from '@/app/types/Select';

const convertQueryParams = (prevParams: URLSearchParams, newParams: TSelectOption[]) => {
  const result = new Map<string, string>();
  newParams.forEach(param => result.set(param.label, param.value.toString()));

  return {...Object.fromEntries(prevParams), ...Object.fromEntries(result)};
};

export const useQueryParams = () => {
  const {search} = useLocation();
  const [queryParams, setSearchParams] = useSearchParams();

  const setQueryParams = (newParams: TSelectOption | TSelectOption[]) => {
    const paramsArray = Array.isArray(newParams) ? newParams : [newParams];

    setSearchParams(prevParams => {
      return {
        ...convertQueryParams(prevParams, paramsArray),
      };
    });
  };

  const getQueryParam = (searchValue: string) => queryParams.get(searchValue);

  const hasQueryParam = (query: string) => queryParams.has(query);

  const deleteQueryParam = (label: string) => {
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
  };
};
