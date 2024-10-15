import {LinkProps} from 'react-router-dom';

import {Key, ReactNode} from 'react';

export interface ISidebarLink extends Omit<LinkProps, 'title'> {
  id: string;
  title: ReactNode;
  icon?: ReactNode;
}

export interface ISidebar {
  key: Key;
  title: ReactNode;
  listLink: ISidebarLink[];
}
