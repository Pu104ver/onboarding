import {baseApi} from '@/app/providers/api/BaseApi';
import {CommentRequest, CommentResponse, TEmployeeByIdRequest} from '@/app/types/Employee';

export const employeeCommentsApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getCommentsForEmployee: builder.query<CommentResponse[], TEmployeeByIdRequest>({
      query: id => `/comments/?employee=${id}`,
      providesTags: ['Comments'],
    }),
    createCommentForEmployee: builder.mutation<void, CommentRequest>({
      query: body => ({
        url: '/comments/',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Comments'],
    }),
  }),
});

export const {
  useGetCommentsForEmployeeQuery: useGetCommentsForEmployee,
  useCreateCommentForEmployeeMutation: useCreateCommentForEmployee,
} = employeeCommentsApi;
