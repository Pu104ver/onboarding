import {Link, useLocation} from 'react-router-dom';

import styles from './Link.module.scss';

import {ISidebarLink} from '@/app/types/SideBar.type';
import Icon from '@/shared/assets/empty-image.svg?react';

const LinkSidebar = ({title, icon, to, ...props}: ISidebarLink) => {
  const {search} = useLocation();

  return (
    <Link className={styles.link} {...props} to={`${to}${search}`}>
      <div className={styles.imgWrapper}>{icon ? icon : <Icon />}</div>

      <span className={styles.title}>{title}</span>
    </Link>
  );
};

export default LinkSidebar;
