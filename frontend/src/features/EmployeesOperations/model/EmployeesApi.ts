import {baseApi} from '@/app/providers/api/BaseApi';
import {
  EmployeeDataType,
  EmployeeDataTypeRequest,
  EmployeesPageRequest,
  ICompletePollRequest,
  TEmployeeByIdRequest,
} from '@/app/types/Employee';
import {INewEmployeeRequest, INewEmployeeResponse} from '@/app/types/NewEmployee.type';
import {IBaseResponse} from '@/app/types/Response.type';
import {TSelectOption} from '@/app/types/Select';
import {PAGES_LIMIT} from '@/shared/const/ApiConst';

export const employeesApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getEmployees: builder.query({
      query: () => '/employees',
      providesTags: ['Employees'],
    }),
    getEmployeesByPage: builder.query<IBaseResponse<EmployeeDataType>, EmployeesPageRequest>({
      query: ({page = 1, queryParams}) =>
        `employees/${queryParams}&role=employee&is_curator_employee=true&limit=${PAGES_LIMIT}&offset=${(page - 1) * PAGES_LIMIT}`,
      serializeQueryArgs: ({endpointName}) => {
        return endpointName;
      },
      merge: (currentCache, newItems, {arg}) => {
        if (+arg.page === 1) {
          return newItems;
        }

        if (newItems) {
          currentCache?.results?.push(...newItems.results);
        }
      },
      forceRefetch({currentArg, previousArg}) {
        return currentArg !== previousArg;
      },
      providesTags: ['Employees'],
    }),
    createNewEmployee: builder.mutation<INewEmployeeResponse, INewEmployeeRequest>({
      query: body => ({
        url: 'employees/',
        method: 'POST',
        body: {
          ...body,
        },
      }),
      invalidatesTags: ['Employees', 'Curators'],
    }),
    changeEmployeeData: builder.mutation<EmployeeDataType, EmployeeDataTypeRequest>({
      query: ({id, ...data}) => ({
        url: `employees/${id}/`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['Employee'],
    }),
    getEmployeeById: builder.query<EmployeeDataType, TEmployeeByIdRequest>({
      query: id => `/employees/${id}/`,
      providesTags: (result, error, id) => [{type: 'Employee', id: id ?? 0}],
    }),
    completePoll: builder.mutation<void, ICompletePollRequest>({
      query: ({pollId}) => ({
        url: `/complete-poll-status/${pollId}/`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, {employeeId}) => [{type: 'Employee', employeeId}],
    }),
    getStatusDictionary: builder.query<TSelectOption[], void>({
      query: () => '/employee-statuses/',
    }),
  }),
});

export const {
  useGetEmployeesQuery,
  useLazyGetEmployeesByPageQuery: useGetEmployees,
  useGetEmployeeByIdQuery,
  useCompletePollMutation: useCompletePoll,
  useCreateNewEmployeeMutation: useCreateEmployee,
  useChangeEmployeeDataMutation: useChangeEmployeeData,
  useGetStatusDictionaryQuery: useGetStatusDictionary,
} = employeesApi;
