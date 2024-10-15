import {baseApi} from '@/app/providers/api/BaseApi';
import {IProject} from '@/app/types/Projects';

export const projectsApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getProjects: builder.query<IProject[], void>({
      query: () => 'projects/',
      providesTags: ['Projects'],
    }),
  }),
});

export const {useGetProjectsQuery: useGetProjects} = projectsApi;
