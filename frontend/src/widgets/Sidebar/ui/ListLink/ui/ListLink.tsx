import {useLocation} from 'react-router-dom';

import cn from 'classnames';

import styles from './ListLink.module.scss';

import {ISidebarLink} from '@/app/types/SideBar.type';
import LinkSidebar from '@/widgets/Sidebar/ui/Link';

interface IListLinkProps {
  links: ISidebarLink[];
}

const ListLink = ({links}: IListLinkProps) => {
  const {pathname} = useLocation();

  return (
    <ul className={styles.list}>
      {links.map(link => (
        <li
          key={link.id}
          className={cn(styles.linkItem, {
            [styles.currentLink]: pathname?.toLowerCase()?.includes(link.id),
          })}>
          <LinkSidebar {...link} />
        </li>
      ))}
    </ul>
  );
};

export default ListLink;
