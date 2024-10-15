import {HTMLAttributes, ReactNode} from 'react';

export interface ICollapse extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  title: ReactNode;
  isRevert?: boolean;
  icon?: ReactNode;
  defaultHidden?: boolean;
}
