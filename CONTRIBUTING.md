# Contributing to Finance Chat Application

Thank you for your interest in contributing to the Finance Chat Application! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- API key from Groq or OpenAI

### Setup Development Environment
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/finance-chatapp.git
   cd finance-chatapp
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment:
   ```bash
   cp env_example.txt .env
   # Add your API keys to .env
   ```
5. Test the setup:
   ```bash
   python main.py
   ```

## 🔧 Development Workflow

### Making Changes
1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Test thoroughly:
   ```bash
   # Test server startup
   python main.py
   
   # Test client functionality
   python finance_chat.py list
   ```
4. Commit with descriptive messages:
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

### Commit Message Guidelines
- **Add**: New features or functionality
- **Fix**: Bug fixes
- **Update**: Modifications to existing features
- **Remove**: Deleted features or code
- **Docs**: Documentation changes
- **Style**: Code formatting, no functional changes
- **Refactor**: Code restructuring without functional changes
- **Test**: Adding or updating tests

## 📝 Code Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### API Design
- Follow RESTful conventions
- Include proper error handling
- Add comprehensive docstrings
- Maintain consistent response formats

### Documentation
- Update README.md for significant changes
- Add inline comments for complex logic
- Update API documentation
- Include examples for new features

## 🧪 Testing

### Before Submitting
Test your changes with:

1. **Server startup**: `python main.py`
2. **PDF upload**: Upload a test document
3. **Query processing**: Ask sample questions
4. **API endpoints**: Test via curl or browser
5. **Error handling**: Test edge cases

### Test Cases to Verify
- [ ] Application starts without errors
- [ ] PDF upload and processing works
- [ ] Chat functionality returns relevant answers
- [ ] API endpoints respond correctly
- [ ] Error messages are user-friendly
- [ ] Documentation is accurate

## 🐛 Bug Reports

When reporting bugs, please include:

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. macOS, Windows, Linux]
- Python version: [e.g. 3.9.0]
- Browser: [e.g. chrome, safari] (if web-related)

**Additional context**
Add any other context about the problem here.
```

## 💡 Feature Requests

For feature requests, please include:
- Clear description of the proposed feature
- Use case and motivation
- Potential implementation approach
- Any breaking changes considerations

## 📋 Pull Request Process

1. **Fork and branch**: Create a feature branch from `main`
2. **Develop**: Implement your changes with tests
3. **Document**: Update documentation as needed
4. **Test**: Ensure all tests pass
5. **Submit**: Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - List of changes made
   - Testing performed

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Server starts successfully
- [ ] PDF upload works
- [ ] Chat functionality works
- [ ] API endpoints respond correctly
- [ ] Error handling works

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🏷️ Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Create GitHub release

## 📞 Getting Help

- **Documentation**: Check README.md first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Be respectful and constructive

## 🎯 Areas for Contribution

We welcome contributions in these areas:

### High Priority
- **Performance optimization**: Improve query response times
- **Error handling**: Better error messages and recovery
- **Documentation**: Examples, tutorials, API docs
- **Testing**: Unit tests, integration tests

### Medium Priority
- **UI improvements**: Better web interface
- **Additional formats**: Support for more document types
- **Security**: Input validation, sanitization
- **Monitoring**: Logging, metrics, health checks

### Future Features
- **Multi-user support**: Authentication and authorization
- **Database persistence**: Non-volatile storage options
- **Advanced analytics**: Document insights and trends
- **API rate limiting**: Throttling and quotas

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for helping make Finance Chat Application better! 🎉 