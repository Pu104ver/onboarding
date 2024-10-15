import {PayloadAction, createSlice} from '@reduxjs/toolkit';

import {User, UserSchema} from '../types/user';

const initialState: UserSchema = {
  id: null,
  user: null,
  description: null,
  date_of_dismission: null,
  date_of_employment: null,
  full_name: null,
  projects: [],
  role: null,
  telegram_nickname: null,
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserData: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    setUser: (state, action: PayloadAction<UserSchema>) => {
      return {...action.payload};
    },
    logout: () => {
      return {...initialState};
    },
  },
});

export const {setUserData, setUser, logout} = userSlice.actions;

export const {reducer: userReducer} = userSlice;
