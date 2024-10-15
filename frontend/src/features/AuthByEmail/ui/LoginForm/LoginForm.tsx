import {useNavigate} from 'react-router-dom';

import Cookies from 'js-cookie';
import {Helmet} from 'react-helmet';
import {SubmitHandler, useForm} from 'react-hook-form';

import style from './LoginForm.module.scss';

import {useAppDispatch} from '@/app/store/hooks';
import {ILoginRequest} from '@/app/types/Login.type';
import {setUserData} from '@/entities/User/model/slice/UserSlice';
import {useLogin} from '@/features/AuthByEmail/model/services/LoginByEmail/login';
import Button from '@/shared/ui/Button/index';
import Input from '@/shared/ui/Input/index';
import {checkEmail, checkEmpty} from '@/shared/validation/validation';

const LoginForm = () => {
  const {
    register,
    handleSubmit,
    formState: {errors},
  } = useForm<ILoginRequest>();
  const [login, {isLoading}] = useLogin();

  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const onSubmit: SubmitHandler<ILoginRequest> = async ({email, password}) => {
    await login({email, password}).then(({data}) => {
      if (data) {
        Cookies.set('token', data.token);
        dispatch(setUserData(data));
        navigate('/onboarding/employees');
      }
    });
  };

  return (
    <>
      <Helmet title="Onboarding | Логин" />

      <form onSubmit={handleSubmit(onSubmit)} className={style.LoginForm} aria-disabled={isLoading}>
        <h2>Авторизация</h2>

        <Input
          placeholder="example@mail.ru"
          disabled={isLoading}
          loading={isLoading}
          {...register('email', {
            required: true,
            validate: value => checkEmail(value, 'Введите почту'),
          })}
        />
        {errors.email && <p className={style.errorMsg}>Введите почту</p>}

        <Input
          placeholder="*****"
          type="password"
          disabled={isLoading}
          loading={isLoading}
          {...register('password', {
            required: true,
            validate: value => checkEmpty(value, 'Введите пароль'),
          })}
        />
        {errors.password && <p className={style.errorMsg}>Введите пароль</p>}

        <p>Не помню пароль</p>

        <Button type="submit" variant="primary" loading={isLoading} style={{flex: 1}}>
          Войти
        </Button>
      </form>
    </>
  );
};

export default LoginForm;
