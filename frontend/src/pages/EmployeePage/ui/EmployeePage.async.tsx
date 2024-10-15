import {lazy} from 'react';

const EmployeePageAsync = lazy(() => import('./EmployeePage'));
export default EmployeePageAsync;
