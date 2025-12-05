# WIKI Update Plan

## Current State

The WIKI.md file contains comprehensive documentation but needs updates to reflect:
1. Current CLI implementation (not just Python library)
2. All implemented commands
3. Installation instructions
4. Current project structure

## Required Updates

### 1. Introduction Section
- [x] Update title to reflect CLI tool
- [x] Add installation instructions
- [x] Add quick start guide
- [ ] Update overview to focus on CLI usage

### 2. Installation & Setup
- [x] Add installation from source
- [x] Add configuration instructions
- [x] Add verification steps
- [ ] Add pip install instructions (when published)

### 3. Command Reference
- [ ] Update all command examples to use `wapi` CLI
- [ ] Document all implemented commands:
  - [ ] `wapi auth ping`
  - [ ] `wapi domain list`
  - [ ] `wapi domain info`
  - [ ] `wapi domain update-ns`
  - [ ] `wapi nsset info`
  - [ ] `wapi nsset create`
  - [ ] `wapi contact info`
  - [ ] `wapi config show/validate/set`
  - [ ] `wapi dns list`
  - [ ] `wapi dns records`
  - [ ] `wapi dns add`
  - [ ] `wapi dns delete`
- [ ] Add examples for each command
- [ ] Document all options and flags

### 4. API Reference
- [ ] Update to reflect current API client implementation
- [ ] Document WedosAPIClient class
- [ ] Update method signatures
- [ ] Add current parameter formats

### 5. Examples Section
- [ ] Add CLI usage examples
- [ ] Add workflow examples
- [ ] Add scripting examples
- [ ] Add output format examples

### 6. Remove Outdated Content
- [ ] Remove references to old Python library usage
- [ ] Update code examples to CLI commands
- [ ] Remove outdated file references

### 7. Add New Sections
- [ ] Troubleshooting CLI-specific issues
- [ ] Output format guide
- [ ] Configuration management
- [ ] Error handling guide

## Implementation Strategy

1. **Phase 1: Structure Update**
   - Update introduction
   - Add installation section
   - Reorganize content

2. **Phase 2: Command Documentation**
   - Document all CLI commands
   - Add examples
   - Update API reference

3. **Phase 3: Cleanup**
   - Remove outdated content
   - Update examples
   - Verify all links

4. **Phase 4: Enhancement**
   - Add troubleshooting
   - Add advanced usage
   - Add best practices

## Notes

- Keep all RFC-compliant examples
- Maintain US English
- Keep security focus
- Maintain academic/technical tone
- Verify all commands work
