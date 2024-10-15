import {createSelector} from '@reduxjs/toolkit';

import {IFilters} from '../types/filters.type';

import {RootState} from './rootReducer';

export const getIsOpenedPageFilters = (page: keyof IFilters) =>
  createSelector([(state: RootState) => state.filters[page]], filtersPage => filtersPage.isOpened);
