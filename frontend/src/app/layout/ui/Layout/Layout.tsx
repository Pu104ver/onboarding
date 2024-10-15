import {useLocation, useNavigate} from 'react-router-dom';

import Cookies from 'js-cookie';
import {ReactNode, Suspense, useEffect} from 'react';
import {ToastContainer} from 'react-toastify';

import styles from './Layout.module.scss';

import {useAppDispatch} from '@/app/store/hooks';
import {useGetMyData} from '@/entities/User/model/slice/getMyData';
import {setUser} from '@/entities/User/model/slice/UserSlice';
import {IListRoutes} from '@/shared/config/RouteConfig/RouteConfig';
import {SuspensePageWithTable} from '@/shared/suspense/SuspensePageWithTable';
import Sidebar from '@/widgets/Sidebar';

interface ILayoutProps extends Pick<IListRoutes, 'sidebar' | 'suspense'> {
  children: ReactNode;
}

const Layout = ({children, suspense, sidebar = true}: ILayoutProps) => {
  const token = Cookies.get('token');
  const {data} = useGetMyData(undefined, {skip: !token});
  const {pathname} = useLocation();

  const navigate = useNavigate();

  const dispatch = useAppDispatch();

  useEffect(() => {
    if (token && data) {
      dispatch(setUser(data));
    }

    if (pathname === '/') {
      navigate('/login');
    }
  }, [token, data]);

  return (
    <>
      <ToastContainer />

      <div className={styles.wrapper}>
        {sidebar && <Sidebar />}

        <main className={styles.main}>
          <Suspense fallback={suspense ?? <SuspensePageWithTable />}>{children}</Suspense>
        </main>
      </div>
    </>
  );
};

export default Layout;
