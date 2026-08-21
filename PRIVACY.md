# Privacy & Data Handling

## Overview

auto-dao is a **local-first** learning tool. By default, all learning data stays on your machine in the `learning-history/` directory. However, certain optional features involve sending data to external services.

## What Data Is Sent Externally

| Feature | Service | Data Sent | When |
|---------|---------|-----------|------|
| Document conversion (PDF/Word/PPT → Markdown) | [MinerU API](https://mineru.net) | The uploaded file content | Only when you explicitly run the conversion script |

### What Is NOT Sent

- Your `settings/background.md` (personal learning profile)
- Your `settings/glossary.md` (terminology table)
- Your `learning-history/` contents (lessons, summaries, reports)
- Your `settings/.env` (API keys)

## How to Minimize Data Exposure

1. **Pre-convert locally**: If your materials contain sensitive content, convert them to Markdown manually before using auto-dao. The learning engine works directly with `.md` files and does not require the MinerU API.
2. **Review before converting**: Check what you are about to upload. The conversion script prints the file path before sending.
3. **Use the API key responsibly**: Your MinerU API key is stored in `settings/.env` (git-ignored). Do not share it or commit it to version control.

## Local AI Model Usage

When using auto-dao with a local AI model (e.g., Qwen, Ollama), no learning data leaves your machine at all. The skills are pure prompt definitions — they instruct the AI but do not phone home.

When using cloud-based AI providers (e.g., Claude via claude.ai/code), your conversation content is subject to that provider's privacy policy. auto-dao itself does not add any additional data collection on top of what the AI provider already processes.

## Questions

If you have questions about data handling, please open a [GitHub Issue](https://github.com/Jun-maxs/auto-dao/issues).
