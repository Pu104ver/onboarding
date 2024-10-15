import {BaseQueryApi, createApi, FetchArgs, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import Cookies from 'js-cookie';

import {ILoginResponse, IRefreshTokenRequest} from '@/app/types/Login.type';

const baseQuery = fetchBaseQuery({
  baseUrl: process.env.REACT_APP_API_BASE_URL,
  prepareHeaders: headers => {
    const access_token = Cookies.get('access_token');

    if (access_token) {
      headers.set('Authorization', `Bearer ${access_token}`);
    }

    return headers;
  },
});

const baseQueryWithReauth = async (
  args: string | FetchArgs,
  api: BaseQueryApi,
  extraOptions: object,
) => {
  let query = await baseQuery(args, api, extraOptions);
  const refresh_token = localStorage.getItem('refresh_token');

  if (query.error && query.error.status === 401) {
    const refreshResult = (await fetch(`${process.env.REACT_APP_API_BASE_URL}auth/token/refresh/`, {
      method: 'POST',
      body: JSON.stringify({refresh_token}),
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(res => res.json())) as ILoginResponse;

    if (refreshResult) {
      Cookies.set('access_token', refreshResult.access_token);
      localStorage.setItem('refresh_token', refreshResult.refresh_token);
      query = await baseQuery(args, api, extraOptions);

      console.log(query);
    }
  }

  return query;
};

export const baseApi = createApi({
  reducerPath: 'baseApi',
  tagTypes: ['Employees', 'Employee', 'Projects', 'Curators', 'Comments'],
  baseQuery: baseQueryWithReauth,
  endpoints: builder => ({
    getNewAccessToken: builder.mutation<void, IRefreshTokenRequest>({
      query: body => ({
        url: '/auth/token/refresh',
        method: 'POST',
        body,
      }),
    }),
  }),
});
