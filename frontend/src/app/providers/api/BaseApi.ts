import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import Cookies from 'js-cookie';

export const baseApi = createApi({
  reducerPath: 'baseApi',
  tagTypes: ['Employees', 'Employee', 'Projects', 'Curators', 'Comments'],
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_BASE_URL,

    prepareHeaders: headers => {
      const token = Cookies.get('token');

      if (token) {
        headers.set('Authorization', `Token ${token}`);
      }

      return headers;
    },
  }),

  refetchOnFocus: true,
  refetchOnReconnect: true,
  keepUnusedDataFor: 5,
  endpoints: () => ({}),
});
