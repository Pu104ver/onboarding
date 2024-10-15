import {baseApi} from '@/app/providers/api/BaseApi';
import {UserSchema} from '@/entities/User/model/types/user';

export const loginApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getMyData: builder.query<UserSchema, void>({
      query: () => ({
        url: 'me/',
        method: 'GET',
        providesTags: (result: UserSchema) => [{type: 'Employee', id: result.id}],
      }),
    }),
  }),
});

export const {useGetMyDataQuery: useGetMyData} = loginApi;
