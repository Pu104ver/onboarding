import {Key} from 'react';

export interface ILoginRequest {
  email: string;
  password: string;
}

export interface ILoginResponse {
  access_token: string;
  refresh_token: string;

  user_id: Key;
  username: string;
  email: string;

  message?: string;
}

export interface IRefreshTokenRequest {
  refresh_token: string;
}
