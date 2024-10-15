import {createEntityAdapter, createSlice, PayloadAction} from '@reduxjs/toolkit';

import {RootState} from '../rootReducer';

import {IFilters} from '@/app/types/filters.type';

const initialState: IFilters = {
  isOpened: false,
  offset: 0,
};

const filtersAdapter = createEntityAdapter({});

export const filtersSlice = createSlice({
  name: 'filters',
  initialState: filtersAdapter.getInitialState(initialState),
  reducers: {
    handleOpenFilters: state => {
      state.isOpened = !state.isOpened;
    },
    setOffset: (state, action: PayloadAction<number>) => {
      state.offset = action.payload;
    },
  },
});

export const {handleOpenFilters, setOffset} = filtersSlice.actions;

export const {selectAll: filtersSelector} = filtersAdapter.getSelectors(
  (state: RootState) => state[filtersSlice.name],
);

export const selectOffset = (state: RootState) => state.filters.offset;
