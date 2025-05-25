# Google Drive Video Downloader

A Python class for downloading videos from Google Drive using parallel chunk downloading for faster speeds and better reliability.

## Features

- **Parallel Downloads**: Downloads video files in multiple chunks simultaneously for faster speeds
- **Automatic Retry**: Built-in retry mechanism with exponential backoff for handling network issues
- **Progress Tracking**: Real-time progress bar showing download status
- **Rate Limit Handling**: Automatically handles Google Drive API rate limits
- **Configurable Parameters**: Customizable chunk sizes, worker threads, and retry attempts
- **Clean Temporary Files**: Automatic cleanup of temporary chunk files
- **Error Recovery**: Robust error handling with detailed error messages

## Requirements

```bash
pip install requests tqdm python-slugify
```

## Installation

1. Clone this repository or download the `GoogleDriveVideoDownloader` class
2. Install the required dependencies
3. Import and use the class in your Python project

## Quick Start

```python
from google_drive_downloader import GoogleDriveVideoDownloader

# Initialize the downloader
downloader = GoogleDriveVideoDownloader()

# Download a video
video_url = 'https://drive.google.com/file/d/YOUR_VIDEO_ID/view'
downloaded_file = downloader.download(video_url)
print(f"Downloaded: {downloaded_file}")
```

## Usage Examples

### Basic Usage

```python
# Simple download with default settings
downloader = GoogleDriveVideoDownloader()
file_name = downloader.download(video_url)
```

### Custom Configuration

```python
# Customize download parameters
downloader = GoogleDriveVideoDownloader(
    chunk_size=16*1024*1024,  # 16MB chunks (default: 8MB)
    max_workers=12,           # 12 parallel downloads (default: 8)
    max_retries=5,            # 5 retry attempts (default: 3)
    retry_delay=3             # 3 second delay between retries (default: 2)
)

file_name = downloader.download(video_url)
```

### Custom Headers and Filename

```python
# Use custom headers and specify output filename
custom_headers = {
    'user-agent': 'Your Custom User Agent',
    'referer': 'https://drive.google.com/',
    # ... other headers
}

file_name = downloader.download(
    video_url=video_url,
    headers=custom_headers,
    output_filename="my_custom_video.mp4"
)
```

### Multiple Downloads

```python
# Download multiple videos with the same configuration
downloader = GoogleDriveVideoDownloader(max_workers=6)

video_urls = [
    'https://drive.google.com/file/d/VIDEO_ID_1/view',
    'https://drive.google.com/file/d/VIDEO_ID_2/view',
    'https://drive.google.com/file/d/VIDEO_ID_3/view'
]

for url in video_urls:
    try:
        file_name = downloader.download(url)
        print(f"Successfully downloaded: {file_name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chunk_size` | int | 8MB | Size of each download chunk |
| `stream_chunk_size` | int | 8KB | Size of streaming chunks |
| `max_workers` | int | 8 | Maximum number of parallel download threads |
| `max_retries` | int | 3 | Maximum number of retry attempts |
| `retry_delay` | int | 2 | Delay between retries (seconds) |

## Class Methods

### `__init__(chunk_size, stream_chunk_size, max_workers, max_retries, retry_delay)`
Initialize the downloader with custom parameters.

### `download(video_url, headers=None, output_filename=None)`
Download a video from Google Drive.

**Parameters:**
- `video_url` (str): Google Drive video URL
- `headers` (dict, optional): Custom request headers
- `output_filename` (str, optional): Custom output filename

**Returns:**
- `str`: Downloaded file name

### `extract_video_id(video_url)`
Extract video ID from Google Drive URL.

### `get_default_headers()`
Get default headers for requests.

## Error Handling

The downloader includes comprehensive error handling for:
- Network connectivity issues
- Google Drive API rate limits
- Invalid URLs or video IDs
- File access permissions
- Disk space issues

All errors are logged with descriptive messages to help with debugging.

## Performance Tips

1. **Adjust chunk size**: Larger chunks (16-32MB) may be faster for larger files
2. **Optimize workers**: More workers aren't always better - test with 4-12 workers
3. **Network conditions**: Reduce workers and increase retry delay for unstable connections
4. **Large files**: For very large files (>1GB), consider increasing `max_retries`

## Limitations

- Requires the video to be accessible (not private or restricted)
- Depends on Google Drive's internal API which may change
- Rate limiting may slow down downloads for multiple files
- Some videos may not be available in the highest quality (itag 37)

## Example Output

```
Title: My Awesome Video
Initial size estimate: 157286400
Total size from headers: 157286400
Number of chunks: 19
Downloading video: 100%|██████████| 150M/150M [00:45<00:00, 3.33MB/s]
Video downloaded successfully!
Downloaded: my-awesome-video.mp4
```

## Troubleshooting

### Common Issues

**"No suitable video stream found"**
- The video may not be available in the expected quality
- Check if the video is accessible and not private

**"Could not determine file size"**
- The video may be restricted or the URL is invalid
- Verify the Google Drive URL is correct

**Network timeouts**
- Increase `max_retries` and `retry_delay`
- Reduce `max_workers` for unstable connections

**Rate limiting (429 errors)**
- The downloader automatically handles rate limits
- For persistent issues, reduce `max_workers`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational purposes. Make sure you have permission to download videos and comply with Google Drive's Terms of Service.
