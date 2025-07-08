# 🧼 PDF Revision Cleanup Script – Instructions & Prompt

This document describes how to create and run a Python script that cleans up old PDF revisions in a selected folder by moving outdated versions into a `superseded` subfolder. Designed for Windows 11.

---

## ✅ Script Purpose

The script:

- Scans a user-selected folder for PDF files.
- Identifies and groups them based on a base filename with a revision letter (e.g., `_A`, `_B`, `_C`, etc.).
- Keeps only the most recent revision (e.g., `_F` is newer than `_E`).
- Moves any older revisions to a subfolder called `superseded`, which it creates if it doesn't exist.

---

## 🔤 Filename Format

Expected filename format:

