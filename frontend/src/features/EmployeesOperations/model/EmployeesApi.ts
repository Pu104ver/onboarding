import {baseApi} from '@/app/providers/api/BaseApi';
import {
  EmployeeDataType,
  EmployeeDataTypeRequest,
  EmployeesPageRequest,
  IAvailablePollsRequest,
  ICompletePollRequest,
  ILaunchPollRequest,
  IPoll,
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
      query: ({offset, queryParams}) =>
        `employees/${queryParams}&role=employee&limit=${PAGES_LIMIT}&offset=${offset}`,
      serializeQueryArgs: ({endpointName, queryArgs}) => {
        return `${endpointName}-${queryArgs.queryParams}`;
      },
      merge: (currentCache, newItems, {arg}) => {
        if (+arg.offset === 0) {
          return newItems;
        }

        if (newItems) {
          currentCache?.results?.push(...newItems.results);
        }
      },
      forceRefetch({currentArg, previousArg}) {
        return currentArg?.offset !== previousArg?.offset;
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
    getAvailablePolls: builder.query<IPoll[], IAvailablePollsRequest>({
      query: ({employee, intended_for, poll_type}) =>
        `/available-polls/?employee=${employee}&intended_for=${intended_for}&poll_type=${poll_type}`,
    }),
    launchPoll: builder.mutation<void, ILaunchPollRequest>({
      query: body => ({
        url: '/create-poll/',
        method: 'POST',
        body,
      }),
      invalidatesTags: (result, error, {target_employee, employee}) => [
        {type: 'Employee', employeeId: target_employee || employee},
      ],
    }),
    getStatusDictionary: builder.query<TSelectOption[], void>({
      query: () => '/employee-statuses/',
    }),
  }),
});

export const {
  useGetEmployeesQuery,
  useGetEmployeesByPageQuery: useGetEmployees,
  useGetEmployeeByIdQuery,
  useCompletePollMutation: useCompletePoll,
  useCreateNewEmployeeMutation: useCreateEmployee,
  useChangeEmployeeDataMutation: useChangeEmployeeData,
  useGetStatusDictionaryQuery: useGetStatusDictionary,
  useLaunchPollMutation: useLaunchPoll,
  useLazyGetAvailablePollsQuery: useGetAvailablePolls,
} = employeesApi;
