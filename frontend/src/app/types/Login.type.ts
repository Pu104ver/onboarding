import {Key} from 'react';
export interface ILoginRequest {
  email: string;
  password: string;
}

export interface ILoginResponse {
  user_id: Key;
  username: string;
  email: string;
  token: string;
  message?: string;
}
