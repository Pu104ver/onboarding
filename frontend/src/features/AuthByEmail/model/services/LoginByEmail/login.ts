import {baseApi} from '@/app/providers/api/BaseApi';
import {ILoginRequest, ILoginResponse} from '@/app/types/Login.type';

export const loginApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    login: builder.mutation<ILoginResponse, ILoginRequest>({
      query: body => ({
        url: '/auth/token/',
        method: 'POST',
        body,
      }),
    }),
  }),
});

export const {useLoginMutation: useLogin} = loginApi;
