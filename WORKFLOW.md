# Workflow Guide - How to Work on This Repository

## Protecting the Master Branch

The `master` branch contains the stable, public documentation. To work on changes without affecting the published version:

### Option 1: Create a Feature Branch (Recommended)

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Add your feature description"

# Push to remote (creates branch on GitHub)
git push origin feature/your-feature-name

# When ready, merge to master
git checkout master
git merge feature/your-feature-name
git push origin master
```

### Option 2: Work Locally, Keep Master Safe

```bash
# Create a development branch
git checkout -b dev

# Make all your changes on dev branch
# ... work on dev branch ...

# Only merge to master when ready to publish
git checkout master
git merge dev
git push origin master
```

## Tagged Versions

The initial version is tagged as `v1.0.0-initial`:

```bash
# View all tags
git tag -l

# Checkout a specific version
git checkout v1.0.0-initial

# Create a new branch from a tag
git checkout -b restore-from-tag v1.0.0-initial
```

## Best Practices

### 1. Always Work on Branches

Never commit directly to `master` if you want to keep it stable:

```bash
# Good: Create a branch first
git checkout -b update-wiki
# ... make changes ...
git commit -m "Update wiki"
git push origin update-wiki

# Then review and merge when ready
```

### 2. Use Tags for Important Versions

```bash
# Tag current state as a milestone
git tag -a v1.1.0 -m "Added new features"
git push origin v1.1.0
```

### 3. Keep Master Clean

- `master` = published, stable version
- `dev` or feature branches = work in progress
- Tags = important milestones

### 4. Revert to Initial Version

If you need to go back to the initial version:

```bash
# Option 1: Reset master to initial commit
git checkout master
git reset --hard v1.0.0-initial
git push -f origin master  # ⚠️ Force push - use carefully!

# Option 2: Create new branch from initial version
git checkout -b restore-initial v1.0.0-initial
```

## Example Workflow

```bash
# 1. Start working on a new feature
git checkout -b feature/add-examples

# 2. Make changes
vim WIKI.md
# ... add content ...

# 3. Commit
git add WIKI.md
git commit -m "Add more examples to wiki"

# 4. Push feature branch
git push origin feature/add-examples

# 5. Test and review changes
# ... review on GitHub ...

# 6. When satisfied, merge to master
git checkout master
git merge feature/add-examples
git push origin master

# 7. Tag new version (optional)
git tag -a v1.1.0 -m "Added more examples"
git push origin v1.1.0

# 8. Clean up feature branch
git branch -d feature/add-examples
git push origin --delete feature/add-examples
```

## Protecting Master on GitHub

You can also protect the master branch on GitHub:

1. Go to: https://github.com/merneo/wapi/settings/branches
2. Add branch protection rule for `master`
3. Require pull requests for merging
4. This prevents accidental direct pushes to master

## Quick Reference

```bash
# Create new branch
git checkout -b branch-name

# Switch branches
git checkout branch-name

# List all branches
git branch -a

# View tags
git tag -l

# Go back to initial version
git checkout v1.0.0-initial

# See what changed since initial version
git diff v1.0.0-initial..master
```
