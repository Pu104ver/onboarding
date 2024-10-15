import {SubmitHandler, useForm} from 'react-hook-form';

import style from './RegisterForm.module.scss';

import Button from '@/shared/ui/Button/index';
import Input from '@/shared/ui/Input/index';

type Inputs = {
  login: string;
  email: string;
  password: string;
};

const RegisterForm = () => {
  const {register, handleSubmit} = useForm<Inputs>();

  const onSubmit: SubmitHandler<Inputs> = data => {
    console.log(data);
    //функция регистрации
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={style.RegisterForm}>
      <h2>Регистрация</h2>
      <Input placeholder="Логин" {...register('login', {required: true})} />
      <Input placeholder="Почта" type="email" {...register('email', {required: true})} />
      <Input placeholder="Пароль" type="password" {...register('password', {required: true})} />
      <Button type="submit" variant="primary">
        Регистрация
      </Button>
    </form>
  );
};

export default RegisterForm;
