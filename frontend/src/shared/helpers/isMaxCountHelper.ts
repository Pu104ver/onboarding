import {PAGES_LIMIT} from '../const/ApiConst';

interface IData {
  count: number;
}

export const isMaxCountHelper = <T extends IData>(page: number, data?: T) => {
  return data && data.count <= PAGES_LIMIT * page;
};
