import styles from './SuspenseProfilePage.module.scss';

import Skeleton from '@/shared/ui/Skeleton';

// Эти числа показывают какой процент от ширины экрана будет занимать блок
const skeletonList = [41, 58, 58, 41, 50, 49];

interface SuspenseProfilePageProps {
  isError?: boolean;
}

const SuspenseProfilePage = ({isError}: SuspenseProfilePageProps) => {
  return (
    <section className="section">
      {isError ? (
        <h2>Произошла ошибка при загрузке данных, попробуйте перезагрузить страницу</h2>
      ) : (
        <>
          <Skeleton className={styles.skeletonBackBtn} />

          <div className={styles.contentBody}>
            {skeletonList.map((_, index) => (
              <Skeleton
                key={index}
                className={styles.skeletonBody}
                style={{width: `${skeletonList[index]}%`}}
              />
            ))}
          </div>
        </>
      )}
    </section>
  );
};

export default SuspenseProfilePage;
