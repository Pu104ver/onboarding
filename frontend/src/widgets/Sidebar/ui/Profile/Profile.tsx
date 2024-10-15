import {Link} from 'react-router-dom';

import styles from './Profile.module.scss';

import {useAppSelector} from '@/app/store/hooks';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import ProfileIcon from '@/shared/assets/empty-image.svg?react';

export const Profile = () => {
  const user = useAppSelector(userSelector);

  return (
    <div className={styles.wrapper}>
      <div className={styles.profileImgWrapper}>
        <ProfileIcon />
      </div>

      <div className={styles.personalDataWrapper}>
        <Link to="/profile/me">
          <h2 className={styles.name}>{user?.full_name ?? 'Профиль'}</h2>
        </Link>

        {user?.description && <p className={styles.desc}>{user.description}</p>}
      </div>
    </div>
  );
};
