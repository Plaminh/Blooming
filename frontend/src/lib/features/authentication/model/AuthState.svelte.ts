import type { AuthMode } from '../types';
import { validateEmail, validatePassword, validateConfirmPassword } from './validationHelpers';

export type AuthField = 'email' | 'password' | 'confirmPassword' | 'general';
export type AuthErrors = Partial<Record<AuthField, string>>;

export class AuthState {
    mode = $state<AuthMode>('login');
    email = $state('');
    password = $state('');
    confirmPassword = $state('');
    rememberMe = $state(false);
    
    passwordVisible = $state(false);
    confirmPasswordVisible = $state(false);

    errors = $state<AuthErrors>({});
    hasAttemptedSubmit = $state(false);
    isLoading = $state(false);
    isAwaitingVerification = $state(false);
    emailDeliveryFailed = $state(false);

    switchMode(newMode: AuthMode) {
        this.mode = newMode;
        // Preserve values where reasonable (email, password)
        // Clear errors unrelated to the new view, or all errors to be safe since we haven't submitted yet
        this.errors = {};
        this.hasAttemptedSubmit = false;
    }

    togglePasswordVisibility() {
        this.passwordVisible = !this.passwordVisible;
    }

    toggleConfirmPasswordVisibility() {
        this.confirmPasswordVisible = !this.confirmPasswordVisible;
    }

    setFieldError(field: AuthField, error: string | null) {
        const nextErrors = { ...this.errors };
        if (error) nextErrors[field] = error;
        else delete nextErrors[field];
        this.errors = nextErrors;
    }

    revalidateEmail() {
        if (!this.hasAttemptedSubmit) return;
        this.setFieldError('email', validateEmail(this.email));
    }

    revalidatePassword() {
        if (!this.hasAttemptedSubmit) return;
        this.setFieldError('password', validatePassword(this.password));
        if (this.mode === 'register') {
            this.setFieldError(
                'confirmPassword',
                validateConfirmPassword(this.password, this.confirmPassword),
            );
        }
    }

    revalidateConfirmPassword() {
        if (!this.hasAttemptedSubmit) return;
        this.setFieldError(
            'confirmPassword',
            validateConfirmPassword(this.password, this.confirmPassword),
        );
    }

    validate(): boolean {
        this.hasAttemptedSubmit = true;
        const newErrors: AuthErrors = {};

        const emailError = validateEmail(this.email);
        if (emailError) newErrors.email = emailError;

        const passwordError = validatePassword(this.password);
        if (passwordError) newErrors.password = passwordError;

        if (this.mode === 'register') {
            const confirmError = validateConfirmPassword(this.password, this.confirmPassword);
            if (confirmError) newErrors.confirmPassword = confirmError;
        }

        this.errors = newErrors;
        return Object.keys(newErrors).length === 0;
    }
}

export function createAuthState() {
    return new AuthState();
}
