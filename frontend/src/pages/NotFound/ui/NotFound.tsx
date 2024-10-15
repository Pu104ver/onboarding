import {Link} from 'react-router-dom';

import {Helmet} from 'react-helmet';

import NotFoundIcon from './icons/not-found.svg?react';
import styles from './NotFound.module.scss';

const NotFound = () => {
  return (
    <>
      <Helmet title="Onboarding | Такой страницы не существует..." />

      <main className={styles.main}>
        <div className={styles.imgWrapper}>
          <NotFoundIcon className={styles.icon} />
        </div>

        <h1 className={styles.title}>Такой страницы не существует...</h1>

        <Link to="/login" className={styles.link}>
          Перейти на главную
        </Link>
      </main>
    </>
  );
};

export default NotFound;
