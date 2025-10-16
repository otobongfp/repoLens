# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |
| < 1.0   | :x:                |

## 🚨 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent exploitation.

### 2. **Email us directly**
Send details to: **security@repolens.org**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. **Response Timeline**
- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution**: Depends on complexity

### 4. **Recognition**
We appreciate security researchers! With your permission, we'll:
- Credit you in our security advisories
- Add you to our security hall of fame
- Consider bug bounty rewards for significant findings

## Security Best Practices

### For Users
- Keep RepoLens updated to the latest version
- Use strong authentication credentials
- Regularly review access permissions
- Monitor for unusual activity

### For Developers
- Follow secure coding practices
- Use dependency scanning tools
- Implement proper input validation
- Keep dependencies updated

## Security Features

RepoLens includes several security features:

- **JWT Authentication** with secure token handling
- **OAuth Integration** (Google, GitHub)
- **Redis Session Management** for secure sessions
- **SQL Injection Protection** via SQLAlchemy ORM
- **CORS Configuration** for API security
- **Environment Variable Protection** for secrets

## Security Checklist

Before deploying RepoLens:

- [ ] Change default JWT secret key
- [ ] Configure secure database credentials
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS in production
- [ ] Configure OAuth credentials securely
- [ ] Set up Redis authentication
- [ ] Review and restrict API permissions
- [ ] Enable database connection encryption

## Contact

- **Security Email**: hello@repolens.org
- **General Support**: See [SUPPORT.md](SUPPORT.md)
- **Documentation**: [docs/](docs/)

Thank you for helping keep RepoLens secure!
