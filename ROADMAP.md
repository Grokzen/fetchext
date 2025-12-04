# Project Roadmap & Ideas

## 🎨 UX Polish

- [x] **Progress Bars**: Integrate `tqdm` to show download progress, especially for large extensions.
- [ ] **Rich Output**: Use the `rich` library to format the `inspect` command output (tables, colors) and general CLI logs.

## ⚡ Performance

- [x] **Parallel Batch Downloading**: Use `concurrent.futures.ThreadPoolExecutor` in `BatchProcessor` to download multiple extensions simultaneously.

## 🌍 Cross-Platform Support

- [ ] **Windows/MacOS CI**: Add `windows-latest` and `macos-latest` to the GitHub Actions matrix to ensure `pathlib` compatibility across OSs.

## 🛡️ Robustness

- [ ] **Proper CRX Parsing**: Replace the "find ZIP header" hack in `ExtensionInspector` with a proper CRX3 header parser (struct unpacking).

## 🧪 Testing

- [ ] **Mocked File System**: Use `pyfakefs` in unit tests to avoid creating real temporary files on disk.
