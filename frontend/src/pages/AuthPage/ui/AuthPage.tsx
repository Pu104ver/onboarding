import style from './AuthPage.module.scss';

import {LoginForm} from '@/features/AuthByEmail/ui';

function AuthPage() {
  return (
    <section className={style.AuthPage}>
      <LoginForm />
    </section>
  );
}

export default AuthPage;
