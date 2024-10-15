import {ReactNode} from 'react';

import {OnlyAuth, OnlyUnAuth} from './ProtectedRoute';

import {AuthPage} from '@/pages/AuthPage';
import {CuratorPage} from '@/pages/CuratorPage';
import {CuratorsPage} from '@/pages/CuratorsPage';
import {EmployeePage} from '@/pages/EmployeePage';
import {EmployeesPage} from '@/pages/EmployeesPage';
import {NotFoundPage} from '@/pages/NotFound';
import {SuspenseAuthPage} from '@/shared/suspense/SuspenseAuthPage';
import {SuspenseNotFoundPage} from '@/shared/suspense/SuspenseNotFoundPage';

export interface IListRoutes {
  element: ReactNode;
  path: string;
  sidebar?: boolean;
  suspense?: ReactNode;
}

const onlyAuthRoutes: IListRoutes[] = [
  {
    element: <EmployeesPage />,
    path: '/onboarding/employees',
  },
  {
    element: <EmployeePage />,
    path: '/onboarding/employees/:id',
  },
  {
    element: <CuratorsPage />,
    path: '/onboarding/curators',
  },
  {
    element: <CuratorPage />,
    path: '/onboarding/curators/:id',
  },
  {
    element: <EmployeePage isMyProfile />,
    path: '/profile/me',
  },
];

const onlyUnAuthRoutes: IListRoutes[] = [
  {
    element: <AuthPage />,
    path: '/login',
    sidebar: false,
    suspense: <SuspenseAuthPage />,
  },
];

export const ListRoutes: IListRoutes[] = [
  ...onlyAuthRoutes.map(route => ({
    ...route,
    element: <OnlyAuth component={route.element} />,
  })),
  ...onlyUnAuthRoutes.map(route => ({
    ...route,
    element: <OnlyUnAuth component={route.element} />,
  })),
  {
    element: <NotFoundPage />,
    path: '*',
    suspense: <SuspenseNotFoundPage />,
    sidebar: false,
  },
];
