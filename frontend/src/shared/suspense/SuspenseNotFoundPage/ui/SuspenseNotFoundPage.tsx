import styles from './SuspenseNotFoundPage.module.scss';

import Skeleton from '@/shared/ui/Skeleton';

const SuspenseNotFoundPage = () => {
  return (
    <section className="section">
      <div className={styles.wrapper}>
        <Skeleton active className={styles.img} />
        <Skeleton className={styles.desc} />
        <Skeleton className={styles.link} />
      </div>
    </section>
  );
};

export default SuspenseNotFoundPage;
