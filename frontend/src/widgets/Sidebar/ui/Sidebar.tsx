import {Link} from 'react-router-dom';

import cn from 'classnames';
import {useState} from 'react';
import {Fragment} from 'react/jsx-runtime';

import ListLink from './ListLink';
import {Profile} from './Profile/Profile';
import styles from './Sidebar.module.scss';

import CollapseArrowIcon from '@/shared/assets/collapseArrow.svg?react';
import LogoIcon from '@/shared/assets/Logo.svg?react';
import MenuIcon from '@/shared/assets/menu.svg?react';
import {sidebarLinks} from '@/shared/const/sidebarLinks';
import Collapse from '@/shared/ui/Collapse';

interface ISidebarProps {
  hidden?: boolean;
}

const Sidebar = ({hidden}: ISidebarProps) => {
  const [isHidden, setIsHidden] = useState(hidden ?? false);

  const handleHide = () => {
    setIsHidden(prev => !prev);
  };

  return (
    <aside className={cn(styles.aside, {[styles.asideHidden]: isHidden})}>
      <div className={styles.container}>
        <div
          className={cn(styles.sidebarHeader, {
            [styles.sidebarHeaderHidden]: isHidden,
          })}>
          <Link
            to="/onboarding/employees"
            className={cn(styles.logo, {[styles.logoHidden]: isHidden})}>
            <LogoIcon />
          </Link>

          <button
            className={cn(styles.collapseBtn, {
              [styles.collapseBtnHidden]: isHidden,
            })}
            onClick={handleHide}>
            {isHidden ? <MenuIcon /> : <CollapseArrowIcon />}
          </button>
        </div>

        <div className={cn({[styles.hiddenContainer]: isHidden})}>
          <Profile />

          <ul className={styles.list}>
            {sidebarLinks.map((item, index) => (
              <Fragment key={item.key}>
                <li>
                  <Collapse title={item.title}>
                    <ListLink links={item.listLink} />
                  </Collapse>
                </li>

                {index + 1 !== sidebarLinks.length && <hr className={styles.hr} />}
              </Fragment>
            ))}
          </ul>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
