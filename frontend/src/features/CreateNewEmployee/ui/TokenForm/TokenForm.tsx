import styles from './TokenForm.module.scss';

import Button from '@/shared/ui/Button';

interface ITokenFormProps {
  token: string;
}

const TokenForm = ({token}: ITokenFormProps) => {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>
        Передайте данный токен сотруднику для его регистрации в боте.
      </h3>
      <Button copyable={token}>{token}</Button>
    </div>
  );
};

export default TokenForm;
