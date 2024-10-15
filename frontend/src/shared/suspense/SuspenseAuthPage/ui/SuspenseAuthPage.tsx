import styles from './SuspenseAuthPage.module.scss';

import Skeleton from '@/shared/ui/Skeleton';

const SuspenseAuthPage = () => {
  return (
    <section className="section">
      <div className={styles.wrapper}>
        <Skeleton active className={styles.auth} />
      </div>
    </section>
  );
};

export default SuspenseAuthPage;
