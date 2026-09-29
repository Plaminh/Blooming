# ADR 002: Hosted Email Verification

## Context

Blooming currently uses Brevo to send verification emails upon user registration. However, the default verification frontend URL points to `localhost`. For staging users testing the application, localhost links are invalid, preventing them from verifying their email addresses.

## Decision

- **Email Provider**: Keep Brevo as the email delivery provider.
- **Hosted Staging Route**: Use a hosted staging web route for email verification. The email verification links generated should conceptually point to: `https://<staging-frontend>/verify-email?token=...`
- **Verification Flow**: The hosted page will extract the token and verify it against the staging backend.
- **Deep Linking**: Do NOT implement Tauri deep links in this block.

## Rationale

Separating the responsibilities simplifies staging deployment. Brevo strictly handles email delivery, while the hosted frontend serves as a reliable endpoint to receive the verification link. This establishes a fully working flow for staging users without introducing the complexities of deep linking in the desktop app yet.

## Consequences & Boundaries

- **Localhost Limits**: Localhost remains for development-only. The staging contract must not assume localhost.
- **Configuration Contract**: `EMAIL_VERIFICATION_FRONTEND_URL` is documented as the required environment variable for specifying the verification URL in staging/production.

## Deferred Work

- **Post-MVP / Future Blocks**: Implementation of Tauri deep links to directly open the desktop app from the email link.

## Acceptance Criteria

- [ ] `EMAIL_VERIFICATION_FRONTEND_URL` is defined in the configuration contract to point to a hosted staging URL, not localhost.
- [ ] Brevo is designated as the email delivery provider.
- [ ] Deep linking is explicitly marked as deferred.
