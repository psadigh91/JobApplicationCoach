# Security Policy

## Supported Versions

Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them responsibly:

1. **Email:** Check the maintainer's GitHub profile for contact information
2. **Private Security Advisory:** Use GitHub's private vulnerability reporting feature
   - Go to the Security tab
   - Click "Report a vulnerability"
   - Fill in the details

### What to Include

Please include:
- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** assessment
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### Response Timeline

You should receive a response within **48 hours**. If the vulnerability is confirmed, we will:

1. Acknowledge receipt of your report
2. Work on a fix with appropriate priority
3. Release a security patch
4. Credit you for the discovery (unless you prefer to remain anonymous)
5. Publish a security advisory

## Security Best Practices

When using Resume Optimizer:

### For Users

1. **Never commit API keys** - Always use `.env` files (which are gitignored)
2. **Protect your `.env`** - Never share or commit this file
3. **Use strong API keys** - Generate secure Anthropic API keys with appropriate permissions
4. **Keep dependencies updated** - Regularly update npm and pip packages
5. **Review uploaded files** - Be cautious with files from untrusted sources

### For Developers

1. **Input validation** - All user inputs are validated before processing
2. **File uploads** - Only accept specific file types (PDF, DOCX, TXT)
3. **Size limits** - 10MB maximum per file upload
4. **SQL injection** - Use parameterized queries via SQLAlchemy ORM
5. **CORS** - Properly configured for production domains only
6. **Session security** - 24-hour auto-expiry with secure session IDs
7. **No permanent storage** - Uploaded files deleted after 24 hours

### For Deployers

1. **HTTPS only** - Always use HTTPS in production
2. **Environment variables** - Never hardcode secrets in code
3. **Database security** - Use PostgreSQL with proper user permissions
4. **Network security** - Configure firewalls and security groups
5. **Monitoring** - Set up logging and monitoring for suspicious activity
6. **Regular updates** - Keep all dependencies and systems updated

## Known Security Considerations

### Data Privacy

- User data is automatically deleted after 24 hours
- No permanent storage of resumes or personal information
- No user accounts or authentication required
- Session-based isolation

### API Key Security

- Anthropic API keys are stored only in `.env` files
- Keys are never logged or exposed in responses
- Use environment variables exclusively

### File Upload Security

- Restricted file types (PDF, DOCX, TXT only)
- File size limits enforced (10MB max)
- Temporary storage with automatic cleanup
- No executable files allowed

## Security Audit Log

| Date       | Issue | Severity | Status |
|------------|-------|----------|--------|
| 2024-01-XX | TBD   | -        | -      |

---

Thank you for helping keep Resume Optimizer secure! 🔒

For questions about this policy, please open an issue (for non-sensitive questions) or contact the maintainers directly (for sensitive matters).
