import {baseApi} from '@/app/providers/api/BaseApi';
import {EmployeeDataType, EmployeesPageRequest, ICurator} from '@/app/types/Employee';
import {IBaseResponse} from '@/app/types/Response.type';
import {PAGES_LIMIT} from '@/shared/const/ApiConst';

export const curatorsApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getCuratorsDictionary: builder.query<ICurator[], void>({
      query: () => 'employees/?curators_and_employees_with_subordinates=true',
    }),
    getCuratorsPinnedToProjects: builder.query<ICurator[], number[]>({
      query: projects_id => `employees/?role=curator&projects=[${projects_id.join(',')}]`,
    }),
    getCuratorsByPage: builder.query<IBaseResponse<EmployeeDataType>, EmployeesPageRequest>({
      query: ({offset, queryParams}) =>
        `employees/${queryParams}&role=curator&limit=${PAGES_LIMIT}&offset=${offset}`,
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
      providesTags: ['Curators'],
    }),
  }),
});

export const {
  useGetCuratorsByPageQuery: useGetCurators,
  useGetCuratorsDictionaryQuery: useGetCuratorsDictionary,
  useLazyGetCuratorsPinnedToProjectsQuery: useGetCuratorsPinnedToProjects,
} = curatorsApi;
