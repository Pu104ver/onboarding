import {Key} from 'react';
interface IData {
  id: Key;
}
export const convertDataForDataCards = <T, K extends IData>(
  firstarray: T[],
  firstparam: keyof T,
  secondarray?: K[],
) => {
  return (
    secondarray?.filter(item =>
      firstarray?.map(item => item[firstparam])?.includes(item.id as T[keyof T]),
    ) || []
  );
};
