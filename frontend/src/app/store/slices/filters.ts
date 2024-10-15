import {createEntityAdapter, createSlice, PayloadAction} from '@reduxjs/toolkit';

import {RootState} from '../rootReducer';

import {IFilters} from '@/app/types/filters.type';

const initialState: IFilters = {
  employeesPage: {
    isOpened: false,
  },
  curatorsPage: {
    isOpened: false,
  },
};

const filtersAdapter = createEntityAdapter({});

export const filtersSlice = createSlice({
  name: 'filters',
  initialState: filtersAdapter.getInitialState(initialState),
  reducers: {
    handleFilters: (state, action: PayloadAction<keyof IFilters>) => {
      state[action.payload].isOpened = !state[action.payload].isOpened;
    },
  },
});

export const {handleFilters} = filtersSlice.actions;

export const {selectAll: filtersSelector} = filtersAdapter.getSelectors(
  (state: RootState) => state[filtersSlice.name],
);
