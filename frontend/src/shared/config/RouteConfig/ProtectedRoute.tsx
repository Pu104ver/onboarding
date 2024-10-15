import {Navigate, useLocation} from 'react-router-dom';

import Cookies from 'js-cookie';
import {ReactNode} from 'react';

interface IProtected {
  onlyAuth?: boolean;
  component: ReactNode;
}

export const OnlyAuth = ({component, onlyAuth = true}: IProtected) => {
  const location = useLocation();

  const token = Cookies.get('token');

  if (!onlyAuth && token) {
    // Пользователь авторизован, но запрос предназначен только для неавторизованных пользователей
    // Нужно сделать редирект на главную страницу или на тот адрес, что записан в location.state.from
    const {from} = location?.state || {from: {pathname: '/onboarding/employees'}};
    return <Navigate to={from} />;
  }

  if (onlyAuth && !token) {
    // только для авторизованных пользователей
    return <Navigate to="/login" state={{from: location}} />;
  }

  return component;
};

export const OnlyUnAuth = ({component}: {component: ReactNode}) => (
  <OnlyAuth component={component} onlyAuth={false} />
);
