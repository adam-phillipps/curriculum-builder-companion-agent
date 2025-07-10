# Contributing to Curriculum Builder Companion Agent

Thank you for your interest in contributing to this open-source educational platform! This project is licensed under AGPL-3.0 to ensure it remains free and open for the educational community.

## 🎯 Our Mission

We're building an AI-powered curriculum development platform that:
- Remains **free and open source** for educators
- Prevents **commercial exploitation** and white-labeling
- Encourages **community collaboration** and improvement
- Supports **educational equity** through accessible technology

## 🤝 How to Contribute

### Code Contributions

1. **Fork the repository** and create a feature branch
2. **Follow our coding standards** (see below)
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

### Non-Code Contributions

- **Documentation improvements**
- **Bug reports and feature requests**
- **Educational content and examples**
- **Translation and localization**
- **User experience feedback**

## 📋 Coding Standards

### Python Backend
- Follow **PEP 8** style guidelines
- Use **type hints** for all functions
- Write **comprehensive docstrings**
- Maintain **>90% test coverage**
- Use **async/await** for database operations

### Frontend (Next.js/React)
- Use **TypeScript** for type safety
- Follow **React best practices**
- Write **accessible components**
- Use **Tailwind CSS** for styling
- Add **proper error handling**

### Database
- Use **Alembic migrations** for schema changes
- Write **reversible migrations**
- Include **proper indexes** and constraints
- Document **schema relationships**

## 🧪 Testing Requirements

All contributions must include appropriate tests:

### Unit Tests
- Mock external dependencies
- Test individual functions/components
- Fast execution (< 1 second per test)
- Located in `tests/unit/`

### Integration Tests
- Test API endpoints and workflows
- Use test database and services
- Located in `tests/integration/`

### Running Tests
```bash
# All tests
docker compose exec app pytest

# Unit tests only (fast)
docker compose exec app pytest tests/unit/

# Integration tests only
docker compose exec app pytest tests/integration/

# With coverage
docker compose exec app pytest --cov=src
```

## 📝 Commit Guidelines

Use **conventional commits** for clear history:

```
feat: add learning outcomes similarity search
fix: resolve graph centering issue
docs: update API documentation
test: add unit tests for progress tracking
refactor: optimize vector store performance
```

## 🔒 License Compliance

### AGPL-3.0 Requirements

By contributing, you agree that your contributions will be licensed under AGPL-3.0, which means:

- ✅ **Source code must remain open**
- ✅ **Modifications must be shared**
- ✅ **Network use requires source availability**
- ✅ **No proprietary derivatives allowed**

### Copyright Assignment

Contributors retain copyright to their contributions, but grant the project permission to use them under AGPL-3.0. Add your copyright notice to significant contributions:

```python
# Copyright (C) 2024 Your Name <your.email@example.com>
# This file is part of Curriculum Builder Companion Agent.
```

## 🚀 Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Quick Start
```bash
# Clone and setup
git clone <your-fork>
cd curriculum-builder-companion-agent
./scripts/dev-setup.sh

# Run tests
docker compose exec app pytest

# Start development
docker compose up
```

## 🐛 Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (OS, browser, etc.)
- **Screenshots or logs** if applicable

Use our bug report template in GitHub Issues.

## 💡 Feature Requests

For new features, please:

- **Check existing issues** to avoid duplicates
- **Describe the educational use case**
- **Explain the expected benefit**
- **Consider implementation complexity**
- **Discuss licensing implications**

## 📚 Documentation

Help improve our documentation:

- **API documentation** (OpenAPI/Swagger)
- **User guides** for educators
- **Developer documentation**
- **Deployment guides**
- **Educational examples**

## 🌍 Community Guidelines

### Code of Conduct

We're committed to providing a welcoming, inclusive environment:

- **Be respectful** and professional
- **Focus on education** and learning
- **Help newcomers** get started
- **Celebrate diversity** of perspectives
- **Assume good intentions**

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code review and collaboration

## 🎓 Educational Focus

Remember that this project serves educators and learners:

- **Prioritize accessibility** and usability
- **Consider diverse learning needs**
- **Support multiple languages** when possible
- **Design for scalability** in educational settings
- **Maintain performance** for resource-constrained environments

## ⚖️ Legal Considerations

### Third-Party Dependencies

When adding dependencies:
- **Check license compatibility** with AGPL-3.0
- **Avoid proprietary libraries**
- **Document license information**
- **Consider maintenance burden**

### Data Privacy

Educational platforms handle sensitive data:
- **Follow FERPA guidelines** (US)
- **Consider GDPR compliance** (EU)
- **Implement data minimization**
- **Provide clear privacy policies**

## 🏆 Recognition

Contributors are recognized in:
- **README.md** contributor list
- **Release notes** for significant contributions
- **GitHub contributor graphs**
- **Special mentions** for major features

## 📞 Getting Help

Need help contributing?

- **Read the documentation** in `/docs`
- **Check existing issues** and discussions
- **Ask questions** in GitHub Discussions
- **Join our community** calls (schedule TBD)

---

## Thank You! 🙏

Your contributions help keep educational technology open, accessible, and community-driven. Together, we're building tools that empower educators and learners worldwide.

**Remember**: By contributing to this project, you're supporting the principle that educational technology should be free, open, and available to all.