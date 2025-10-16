# Contributing to RepoLens

Thank you for your interest in contributing to RepoLens! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [License](#license)
- [Questions?](#questions)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html). By participating, you agree to uphold this code.

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git** for version control
- **PostgreSQL** 14+ (or use Docker)
- **Neo4j** 5+ (or use Docker)
- **Redis** 6+ (or use Docker)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/repolens.git
   cd repolens
   ```

2. **Environment Setup**
   ```bash
   # Backend environment
   cp backend/example.env backend/.env
   # Edit backend/.env with your configuration
   
   # Frontend environment
   cp frontend/env.example frontend/.env.local
   # Edit frontend/.env.local with your configuration
   ```

3. **Start Services with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Database setup
   alembic upgrade head
   ```

5. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Start Backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Project Structure

```
repolens/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Configuration & dependencies
│   │   ├── database/       # SQLAlchemy models & migrations
│   │   ├── services/       # Business logic
│   │   └── features/       # Feature modules
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/app/           # App Router pages
│   ├── src/components/     # React components
│   └── package.json       # Node.js dependencies
├── docs/                   # Documentation
└── docker-compose.yml     # Service orchestration
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes** - Fix issues and improve stability
- **New Features** - Add new functionality
- **Documentation** - Improve docs, README, comments
- **UI/UX Improvements** - Enhance user interface
- **Performance** - Optimize code and database queries
- **Tests** - Add unit tests, integration tests
- **DevOps** - Improve CI/CD, Docker, deployment

### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) for clear, consistent commit messages:

#### Common Prefixes:

- **`feat:`** - New features or functionality
  ```bash
  feat: add user authentication with Google OAuth
  feat: implement project analysis dashboard
  feat: add dark mode toggle to navbar
  ```

- **`fix:`** - Bug fixes
  ```bash
  fix: resolve authentication token expiration issue
  fix: prevent memory leak in analysis service
  fix: correct API response format for project list
  ```

- **`refactor:`** - Code restructuring without changing functionality
  ```bash
  refactor: migrate project service from raw SQL to SQLAlchemy ORM
  refactor: extract authentication logic into separate service
  refactor: reorganize frontend components into feature folders
  ```

- **`docs:`** - Documentation changes
  ```bash
  docs: update API documentation with new endpoints
  docs: add contributing guidelines
  docs: improve setup instructions
  ```

- **`test:`** - Adding or updating tests
  ```bash
  test: add unit tests for project creation service
  test: improve integration test coverage
  test: add end-to-end tests for authentication flow
  ```

- **`style:`** - Code formatting, no logic changes
  ```bash
  style: format code according to project standards
  style: fix linting issues
  ```

- **`perf:`** - Performance improvements
  ```bash
  perf: optimize database queries for faster project loading
  perf: implement caching for analysis results
  ```

- **`chore:`** - Maintenance tasks
  ```bash
  chore: update dependencies to latest versions
  chore: configure CI/CD pipeline
  chore: add pre-commit hooks
  ```

#### Commit Message Format:
```
<type>: <description>

[optional body]

[optional footer(s)]
```

**Examples:**
```bash
feat: add project export functionality

Allow users to export project analysis results to PDF and CSV formats.
Includes new API endpoint and frontend export button.

Closes #123
```

```bash
refactor: migrate authentication to use Redis sessions

- Replace in-memory session storage with Redis
- Improve session security and scalability
- Add session expiration handling

BREAKING CHANGE: Session format has changed
```

### Code Style Guidelines

#### Backend (Python)
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for functions and classes
- Use **async/await** for database operations
- Follow **FastAPI** best practices

```python
async def create_project(
    db: AsyncSession, 
    project_data: ProjectCreateRequest,
    user_id: str
) -> Project:
    """
    Create a new project for a user.
    
    Args:
        db: Database session
        project_data: Project creation data
        user_id: ID of the user creating the project
        
    Returns:
        Created project instance
        
    Raises:
        HTTPException: If project creation fails
    """
    # Implementation here
```

#### Frontend (TypeScript/React)
- Use **TypeScript** for type safety
- Follow **React** best practices
- Use **Tailwind CSS** for styling
- Write **functional components** with hooks
- Use **proper error handling**

```typescript
interface ProjectCardProps {
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (projectId: string) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete
}) => {
  // Implementation here
};
```

### Database Changes

When making database changes:

1. **Create Migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Review Migration**
   - Check the generated migration file
   - Ensure it's safe and reversible
   - Test on a copy of production data

3. **Apply Migration**
   ```bash
   alembic upgrade head
   ```

## Pull Request Process

### Before Submitting

- [ ] **Test your changes** thoroughly
- [ ] **Update documentation** if needed
- [ ] **Add tests** for new functionality
- [ ] **Check code style** and formatting
- [ ] **Ensure all tests pass**
- [ ] **Update CHANGELOG.md** if applicable

### PR Guidelines

1. **Clear Title** - Describe what the PR does
2. **Detailed Description** - Explain the changes and why
3. **Link Issues** - Reference any related issues
4. **Screenshots** - For UI changes, include before/after
5. **Testing Notes** - How to test the changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] Database migrations tested

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks** - CI/CD runs tests and linting
2. **Code Review** - Maintainers review the code
3. **Feedback** - Address any requested changes
4. **Approval** - Once approved, PR is merged

## License

By contributing to RepoLens, you agree that your contributions will be licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### Key Points:
- All contributions must be compatible with AGPL-3.0
- You retain copyright to your contributions
- Your contributions become part of the open-source project
- Any derivative works must also be AGPL-3.0 licensed

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, browser, versions)
- **Screenshots** or error messages
- **Logs** if applicable

### Feature Requests

For feature requests:

- **Clear description** of the feature
- **Use case** and motivation
- **Proposed implementation** (if you have ideas)
- **Alternative solutions** considered

## Development Tips

### Backend Development
- Use **FastAPI's automatic documentation** at `/docs`
- **Test API endpoints** with the interactive docs
- **Use async/await** for all database operations
- **Follow dependency injection** patterns

### Frontend Development
- Use **React DevTools** for debugging
- **Test components** in Storybook (if available)
- **Use TypeScript** strict mode
- **Follow accessibility** guidelines

### Database Development
- **Always create migrations** for schema changes
- **Test migrations** on sample data
- **Use transactions** for complex operations
- **Index frequently queried columns**

## Questions?

- **Discord** - Join our community Discord
- **GitHub Discussions** - Ask questions in Discussions
- **Issues** - Create an issue for bugs or features
- **Email** - Contact maintainers directly

<!-- ## Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page -->

Thank you for contributing to RepoLens! 🚀
