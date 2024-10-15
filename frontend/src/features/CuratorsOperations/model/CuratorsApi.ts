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
      query: ({page = 1, queryParams}) =>
        `employees/${queryParams}&role=curator&limit=${PAGES_LIMIT}&offset=${(page - 1) * PAGES_LIMIT}`,
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
      providesTags: ['Curators'],
    }),
  }),
});

export const {
  useLazyGetCuratorsByPageQuery: useGetCurators,
  useGetCuratorsDictionaryQuery: useGetCuratorsDictionary,
  useLazyGetCuratorsPinnedToProjectsQuery: useGetCuratorsPinnedToProjects,
} = curatorsApi;
