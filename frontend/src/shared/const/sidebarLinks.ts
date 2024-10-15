import {ISidebar} from '@/app/types/SideBar.type';

export const sidebarLinks: ISidebar[] = [
  {
    key: '/onboarding',
    title: 'Онбординг',
    listLink: [
      {
        id: '/onboarding/employees',
        title: 'Сотрудники',
        to: '/onboarding/employees',
      },
      {
        id: '/onboarding/curators',
        title: 'Кураторы',
        to: '/onboarding/curators',
      },
      //TODO {
      //   id: '/onboarding/analytics',
      //   title: 'Аналитика',
      //   to: '/onboarding/analytics',
      // },
    ],
  },
  //TODO {
  //   key: '/corporate-culture',
  //   title: 'Корпоративная культура',
  //   listLink: [
  //     {
  //       id: '/corporate-culture/events',
  //       title: 'Мероприятия',
  //       to: '/corporate-culture/events',
  //     },
  //     {
  //       id: '/corporate-culture/analytics',
  //       title: 'Аналитика',
  //       to: '/corporate-culture/analytics',
  //     },
  //     {
  //       id: '/corporate-culture/activities',
  //       title: 'Активности',
  //       to: '/corporate-culture/activities',
  //     },
  //     {
  //       id: '/corporate-culture/calendar',
  //       title: 'Календарь',
  //       to: '/corporate-culture/calendar',
  //     },
  //   ],
  // },
];
