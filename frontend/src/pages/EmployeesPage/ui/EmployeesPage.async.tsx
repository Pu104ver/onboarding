import {lazy} from 'react';

const EmployeesPageAsync = lazy(() => import('./EmployeesPage'));

export default EmployeesPageAsync;
