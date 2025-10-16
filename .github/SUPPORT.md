# Support RepoLens

## Getting Help

### Documentation
- **[README](README.md)** - Quick start and overview
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute
- **[Project Info](docs/INFO.md)** - Architecture and roadmap

### Bug Reports
If you find a bug, please:
1. **Search existing issues** first
2. **Create a new issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, browser, versions)

### Feature Requests
Have an idea? We'd love to hear it!
1. **Check the roadmap** in [INFO.md](docs/INFO.md)
2. **Create a feature request** with:
   - Clear description of the feature
   - Use case and motivation
   - Proposed implementation (if you have ideas)

### Community Support
- **GitHub Discussions** - Ask questions and share ideas
- **Issues** - Report bugs and request features
- **Discord** - Join our community (coming soon)

### Quick Start Issues
Common setup problems and solutions:

#### Backend Issues
```bash
# Database connection issues
docker-compose up -d  # Start services
alembic upgrade head  # Run migrations

# Python dependencies
pip install -r requirements.txt
```

#### Frontend Issues
```bash
# Node modules
npm install

# Environment variables
cp env.example .env.local
# Edit .env.local with your settings
```

#### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### Direct Contact
For urgent issues or enterprise inquiries:
- **Email**: [hello@repolens.org]
- **Security issues**: [hello@repolens.org]

## Contributing
We welcome contributions! See our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## License
This project is licensed under AGPL-3.0. See [LICENSE](LICENSE) for details.
