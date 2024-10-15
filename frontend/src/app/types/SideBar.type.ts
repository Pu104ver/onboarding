import {LinkProps} from 'react-router-dom';

import {Key, ReactNode} from 'react';

export interface ISidebarLink extends Omit<LinkProps, 'title' | 'to'> {
  id: string;
  title: ReactNode;
  icon?: ReactNode;
  to: string;
}

export interface ISidebar {
  key: Key;
  title: ReactNode;
  listLink: ISidebarLink[];
}
