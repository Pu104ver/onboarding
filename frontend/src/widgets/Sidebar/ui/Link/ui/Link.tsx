import {Link} from 'react-router-dom';

import styles from './Link.module.scss';

import {ISidebarLink} from '@/app/types/SideBar.type';
import Icon from '@/shared/assets/empty-image.svg?react';

const LinkSidebar = ({title, icon, ...props}: ISidebarLink) => {
  return (
    <Link className={styles.link} {...props}>
      <div className={styles.imgWrapper}>{icon ? icon : <Icon />}</div>

      <span className={styles.title}>{title}</span>
    </Link>
  );
};

export default LinkSidebar;
