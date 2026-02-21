# CFT CLI Documentation

Complete documentation for the CloudFormation CLI tools.

## Documentation Files

- **[index.md](index.md)** - Main documentation index
- **[installation.md](installation.md)** - Installation instructions
- **[quickstart.md](quickstart.md)** - Quick start guide
- **[commands.md](commands.md)** - Complete command reference
- **[configuration.md](configuration.md)** - Configuration options
- **[examples.md](examples.md)** - Usage examples
- **[api.md](api.md)** - API reference

## Building Documentation

To view the documentation locally, you can use any markdown viewer or convert to HTML:

```bash
# Using Python markdown
pip install markdown
python -m markdown docs/index.md > index.html

# Using pandoc
pandoc docs/index.md -o index.html
```

## Contributing

To contribute to the documentation:

1. Edit the relevant `.md` file
2. Ensure examples are tested
3. Submit a pull request

## Documentation Standards

- Use clear, concise language
- Include working examples
- Keep code blocks properly formatted
- Update all related sections when making changes
