import styles from './SuspensePageWithTable.module.scss';

import Skeleton from '@/shared/ui/Skeleton';

const SuspensePageWithTable = () => {
  return (
    <section className="section">
      <div className={styles.header}>
        <Skeleton className={styles.title} />
        <Skeleton className={styles.filter} />
      </div>

      <Skeleton className={styles.input} />

      <Skeleton className={styles.table} />
    </section>
  );
};

export default SuspensePageWithTable;
