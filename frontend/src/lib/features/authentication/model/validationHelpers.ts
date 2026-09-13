export function validateEmail(email: string): string | null {
    if (!email) {
        return 'Email is required';
    }
    // Simple email regex for pure deterministic validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return 'Invalid email format';
    }
    return null;
}

export function validatePassword(password: string): string | null {
    if (!password) {
        return 'Password is required';
    }
    if (password.length < 8) {
        return 'Password must be at least 8 characters';
    }
    return null;
}

export function validateConfirmPassword(password: string, confirmPassword: string): string | null {
    if (!confirmPassword) {
        return 'Confirm password is required';
    }
    if (password !== confirmPassword) {
        return 'Passwords do not match';
    }
    return null;
}
