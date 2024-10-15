import {baseApi} from '@/app/providers/api/BaseApi';
import {IPoll} from '@/app/types/Employee';

interface IPullsRequest {
  target_employee_id?: number | string;
  id: number | string;
}

export const pullsApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getEmployeePolls: builder.query<IPoll[], IPullsRequest>({
      query: ({id, target_employee_id}) =>
        `/polls/?employee=${id}${target_employee_id ? `&target_employee=${target_employee_id}` : ''}&has_answers=true`,
    }),
  }),
});

export const {useGetEmployeePollsQuery} = pullsApi;
