import {configureStore, isRejectedWithValue, Middleware, PayloadAction} from '@reduxjs/toolkit';
import {toast} from 'react-toastify';

import {baseApi} from '../providers/api/BaseApi';
import {IErrorResponse} from '../types/ErrorResponse';

import {filtersSlice} from './slices/filters';

import {userReducer} from '@/entities/User/model/slice/UserSlice';

const rtkQueryErrorLogger: Middleware = () => next => action => {
  const typedAction = action as PayloadAction<IErrorResponse>;

  if (isRejectedWithValue(typedAction)) {
    if (typedAction.payload.status < 500) {
      Object.values(typedAction.payload.data).map(field => {
        if (typeof field === 'string') {
          toast.error(field);
        } else {
          field.map(str => {
            toast.error(str);
          });
        }
      });
    } else {
      toast.error(
        'Ошибка сервера. Попробуйте перезагрузить страницу или повторить попытку позже...',
      );
    }
  }

  return next(action);
};

export const store = configureStore({
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
    user: userReducer,
    [filtersSlice.name]: filtersSlice.reducer,
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware().concat(rtkQueryErrorLogger, baseApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
