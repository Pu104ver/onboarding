import styles from './TokenForm.module.scss';

import Button from '@/shared/ui/Button';

interface ITokenFormProps {
  access_token: string;
}

const TokenForm = ({access_token}: ITokenFormProps) => {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>
        Передайте данный токен сотруднику для его регистрации в боте.
      </h3>
      <Button copyable={access_token}>{access_token}</Button>
    </div>
  );
};

export default TokenForm;
