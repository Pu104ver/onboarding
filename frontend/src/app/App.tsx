import {Route, Routes} from 'react-router-dom';

import Layout from './layout';

import {ListRoutes} from '@/shared/config/RouteConfig/RouteConfig';

import './styles/index.scss';

export const App = () => {
  return (
    <Routes>
      {ListRoutes.map(route => (
        <Route
          key={route.path}
          element={
            <Layout suspense={route.suspense} sidebar={route.sidebar}>
              {route.element}
            </Layout>
          }
          path={route.path}
        />
      ))}
    </Routes>
  );
};
