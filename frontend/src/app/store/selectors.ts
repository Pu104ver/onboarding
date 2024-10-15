import {createSelector} from '@reduxjs/toolkit';

import {RootState} from './rootReducer';

export const getIsOpenedPageFilters = createSelector(
  [(state: RootState) => state.filters.isOpened],
  isOpened => isOpened,
);
