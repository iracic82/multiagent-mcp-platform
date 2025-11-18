# Contributing to Multi-Agent MCP Platform

Thank you for your interest in contributing to this project. This platform is designed as a production-grade template for building MCP servers with enterprise features.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/multiagent-mcp-platform.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run tests
python -m pytest
```

## Code Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

### Testing

- Write tests for new features
- Ensure all existing tests pass
- Test production features (caching, circuit breakers, metrics)
- Include integration tests for end-to-end workflows

### Documentation

- Update README.md if adding new features
- Document configuration options in DEPLOYMENT_GUIDE.md
- Add architecture changes to ARCHITECTURE.md
- Log improvements in IMPROVEMENTS_CHANGELOG.md

## Project Structure

When adding new features, follow the existing structure:

```
services/          # Business logic and API clients
agents/            # Multi-agent framework
mcp_*.py          # MCP server implementations
test_*.py         # Test files
docs/             # Documentation
```

## Adding New MCP Tools

1. Add tool function to appropriate MCP server file
2. Use `@mcp.tool()` decorator
3. Include comprehensive docstring
4. Add error handling
5. Implement caching if appropriate
6. Add metrics collection
7. Write tests
8. Update documentation

Example:

```python
@mcp.tool()
async def my_new_tool(param: str) -> dict:
    """
    Description of what this tool does.

    Args:
        param: Description of parameter

    Returns:
        dict: Description of return value
    """
    try:
        # Increment request counter
        metrics.increment_request("my_new_tool")

        # Your implementation here
        result = await some_operation(param)

        return {"success": True, "data": result}

    except Exception as e:
        metrics.increment_error("my_new_tool", type(e).__name__)
        logger.error("my_new_tool_failed", error=str(e))
        raise
```

## Adding Production Features

When adding observability or reliability features:

1. **Metrics**: Add to `services/metrics.py`
2. **Tracing**: Add spans in `services/tracing.py`
3. **Caching**: Use `services/cache.py` pattern
4. **Circuit Breakers**: Follow `services/circuit_breaker.py` pattern

## Pull Request Process

1. **Description**: Provide clear description of changes
2. **Testing**: Include test results
3. **Documentation**: Update relevant docs
4. **Breaking Changes**: Clearly mark any breaking changes
5. **Performance**: Note any performance impacts

## Reusable Patterns

This platform provides reusable patterns for any REST API MCP server:

### Caching Layer
- TTL-based response caching
- Configurable cache size
- Metrics integration
- Adaptable to any API

### Circuit Breaker
- Fast-fail protection
- Configurable thresholds
- State machine implementation
- Metrics tracking

### Metrics Collection
- Prometheus-compatible
- Request/response tracking
- Error monitoring
- Custom metrics support

### Distributed Tracing
- OpenTelemetry integration
- Automatic HTTP instrumentation
- Manual span creation
- Jaeger export

### Health Checks
- Load balancer compatible
- Kubernetes readiness/liveness
- Dependency checking

## Adapting for Other APIs

To adapt this platform for a different API:

1. **Create new service client** in `services/`
2. **Implement authentication** (OAuth, API key, etc.)
3. **Create MCP server** file (`mcp_yourapi.py`)
4. **Define tools** using `@mcp.tool()` decorator
5. **Add caching** for appropriate endpoints
6. **Implement metrics** collection
7. **Add tests**
8. **Document** in README.md

## Code Review Guidelines

Reviewers will check for:

- Code quality and style
- Test coverage
- Documentation completeness
- Security considerations
- Performance implications
- Backward compatibility

## Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Implement proper error handling
- Follow principle of least privilege

## Questions or Issues?

- Open an issue for bugs or feature requests
- Use discussions for questions
- Tag issues appropriately (bug, enhancement, documentation, etc.)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
