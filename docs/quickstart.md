# Quick Start

## Deploy a Stack

```bash
deploy-stack --stack my-stack --filename template.yaml
```

## Deploy with Parameters

```bash
deploy-stack --stack my-stack --filename template.yaml \
  --parameters "Environment=prod,Version=1.0"
```

## Deploy with Parameter File

```bash
deploy-stack --stack my-stack --filename template.yaml \
  --parameter-file params.json
```

## List All Stacks

```bash
list-stacks
```

## Describe a Stack

```bash
describe-stack my-stack
```

## Delete a Stack

```bash
delete-stack --stack my-stack
```

## Monitor Stack Changes

```bash
attach-stack --stack my-stack
```

## Common Workflow

1. Create/update a stack:
   ```bash
   deploy-stack -s my-stack -f template.yaml -i "Env=prod"
   ```

2. Check stack status:
   ```bash
   describe-stack my-stack
   ```

3. Delete when done:
   ```bash
   delete-stack -s my-stack
   ```
