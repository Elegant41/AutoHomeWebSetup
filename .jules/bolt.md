## 2024-05-15 - [Initial Journal]
**Learning:** Just starting out.
**Action:** Keep digging.
## 2024-05-15 - [Test Suite Environment Error]
**Learning:** The test suite uses `sc query` and Windows-specific `creationflags` for `subprocess.Popen` in `platform_utils.run_command`. This causes tests to fail on Linux. This was expected as per memory.
**Action:** Ignore test failures related to `creationflags` or mock them if I need them to pass. Focus on the core issue.
## 2024-05-15 - [Download Performance]
**Learning:** Found a potential performance bottleneck in `core/downloader.py`. In the `download_file` method, it updates the progress bar for every single chunk downloaded. If the chunk size is 8KB (8192 bytes) and the file is large, it will invoke `progress_callback` excessively. This callback likely communicates with the GUI thread, potentially causing UI freezes or excessive overhead.
**Action:** Implement throttling/debouncing in the download loop so `progress_callback` is only called periodically (e.g., every 100ms or when the percentage changes).

## 2024-05-15 - [GUI Polling Loop Bottleneck]
**Learning:** In `gui/pages/install_page.py`'s `_poll_progress` method, a `while True` loop rapidly empties the `progress_queue` queue. For every chunk downloaded, `set_progress` is called which updates the UI (labels, progress bar, text box) synchronously within this loop. When a file downloads fast in many chunks, this completely starves the Tkinter event loop, causing a freeze until the queue is completely drained. Since `after` is used, we block for the duration of processing *all* queued items.
**Action:** Throttle the calls to `progress_callback` in `core/downloader.py` so we only emit progress events when the percentage changes (or periodically), instead of emitting it for every 8KB chunk.
