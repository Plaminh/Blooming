export type AuthMode = 'login' | 'register';

export interface LoginSubmitData {
    email: string;
    password: string;
    rememberMe: boolean;
}

export interface RegisterSubmitData {
    email: string;
    password: string;
}

export interface AuthCallbacks {
    onSubmitLogin?: (data: LoginSubmitData) => void;
    onSubmitRegister?: (data: RegisterSubmitData) => void;
    onModeChange?: (mode: AuthMode) => void;
    onTitleBarAction?: (action: 'minimize' | 'maximize' | 'close') => void;
}
