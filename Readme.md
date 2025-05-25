# Google Drive Video Downloader

A Python class for downloading videos from Google Drive using parallel chunk downloading with stream quality selection for faster speeds and better reliability.

## Features

- **Stream Quality Selection**: Choose from available video streams or use the highest quality by default
- **Parallel Downloads**: Downloads video files in multiple chunks simultaneously for faster speeds
- **Automatic Retry**: Built-in retry mechanism with exponential backoff for handling network issues
- **Progress Tracking**: Real-time progress bar showing download status
- **Rate Limit Handling**: Automatically handles Google Drive API rate limits
- **Configurable Parameters**: Customizable chunk sizes, worker threads, and retry attempts
- **Clean Temporary Files**: Automatic cleanup of temporary chunk files
- **Error Recovery**: Robust error handling with detailed error messages
- **Interactive Mode**: Choose specific video quality when available

## Requirements

```bash
pip install requests tqdm python-slugify
```

## Installation

1. Clone this repository or download the `GoogleDriveVideoDownloader` class
2. Install the required dependencies using `pip install -r requirements.txt`
3. Import and use the class in your Python project

## Quick Start

```python
from google_drive_downloader import GoogleDriveVideoDownloader

# Initialize the downloader (uses highest quality by default)
downloader = GoogleDriveVideoDownloader()

# Download a video
video_url = 'https://drive.google.com/file/d/YOUR_VIDEO_ID/view'
downloaded_file = downloader.download(video_url)
print(f"Downloaded: {downloaded_file}")
```

## Usage Examples

### Basic Usage (Highest Quality Stream)

```python
# Simple download with default settings - automatically selects highest quality
downloader = GoogleDriveVideoDownloader()
file_name = downloader.download(video_url)
```

### Interactive Stream Selection

```python
# Enable interactive stream selection
downloader = GoogleDriveVideoDownloader(default_stream=False)
file_name = downloader.download(video_url)

# Output example:
# [0] Found 360p stream
# [1] Found 720p stream  
# [2] Found 1080p stream
# Enter the index of the stream you want to download: 2
```

### Custom Configuration

```python
# Customize download parameters
downloader = GoogleDriveVideoDownloader(
    chunk_size=16*1024*1024,  # 16MB chunks (default: 8MB)
    max_workers=12,           # 12 parallel downloads (default: 8)
    max_retries=5,            # 5 retry attempts (default: 3)
    retry_delay=3,            # 3 second delay between retries (default: 2)
    default_stream=True       # Use highest quality automatically (default: True)
)

file_name = downloader.download(video_url)
```

### Custom Output Filename

```python
# Specify custom output filename
downloader = GoogleDriveVideoDownloader()

file_name = downloader.download(
    video_url=video_url,
    output_filename="my_custom_video.mp4"
)
```

### Multiple Downloads with Quality Selection

```python
# Download multiple videos with interactive quality selection
downloader = GoogleDriveVideoDownloader(
    max_workers=6,
    default_stream=False  # Enable interactive selection
)

video_urls = [
    'https://drive.google.com/file/d/VIDEO_ID_1/view',
    'https://drive.google.com/file/d/VIDEO_ID_2/view',
    'https://drive.google.com/file/d/VIDEO_ID_3/view'
]

for url in video_urls:
    try:
        print(f"\nDownloading: {url}")
        file_name = downloader.download(url)
        print(f"Successfully downloaded: {file_name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
```

### Command Line Usage

```python
# Run the script directly for interactive mode
python google_drive_downloader.py
# Enter the video URL: https://drive.google.com/file/d/YOUR_VIDEO_ID/view
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chunk_size` | int | 8MB | Size of each download chunk |
| `stream_chunk_size` | int | 8KB | Size of streaming chunks |
| `max_workers` | int | 8 | Maximum number of parallel download threads |
| `max_retries` | int | 3 | Maximum number of retry attempts |
| `retry_delay` | int | 2 | Delay between retries (seconds) |
| `default_stream` | bool | True | Use highest quality stream automatically |

## Stream Quality Selection

### Automatic Mode (default_stream=True)
- Automatically selects the highest quality stream available
- No user interaction required
- Fastest and most convenient option

### Interactive Mode (default_stream=False)  
- Displays all available video streams with their resolutions
- Allows manual selection of preferred quality
- Useful when you want to choose a specific quality or save bandwidth

Example output in interactive mode:
```
[0] Found 360p stream
[1] Found 720p stream
[2] Found 1080p stream
Enter the index of the stream you want to download: 1
```

## Class Methods

### `__init__(chunk_size, stream_chunk_size, max_workers, max_retries, retry_delay, default_stream)`
Initialize the downloader with custom parameters.

### `download(video_url, headers=None, output_filename=None)`
Download a video from Google Drive.

**Parameters:**
- `video_url` (str): Google Drive video URL
- `headers` (dict, optional): Custom request headers (uses built-in headers if None)
- `output_filename` (str, optional): Custom output filename

**Returns:**
- `str`: Downloaded file name

### `extract_video_id(video_url)`
Extract video ID from Google Drive URL.

### `get_video_stream_info(video_id, headers)`
Get available video streams and metadata from Google Drive.

## Error Handling

The downloader includes comprehensive error handling for:
- Network connectivity issues
- Google Drive API rate limits
- Invalid URLs or video IDs
- File access permissions
- Disk space issues
- Invalid stream selection indices

All errors are logged with descriptive messages to help with debugging.

## Performance Tips

1. **Stream Selection**: Higher quality streams are larger - choose appropriately for your needs
2. **Adjust chunk size**: Larger chunks (16-32MB) may be faster for larger files
3. **Optimize workers**: More workers aren't always better - test with 4-12 workers
4. **Network conditions**: Reduce workers and increase retry delay for unstable connections
5. **Large files**: For very large files (>1GB), consider increasing `max_retries`
6. **Bandwidth**: Use interactive mode to select lower quality streams if bandwidth is limited

## Limitations

- Requires the video to be accessible (not private or restricted)
- Depends on Google Drive's internal API which may change
- Rate limiting may slow down downloads for multiple files
- Available stream qualities depend on the original video upload
- Some videos may have limited quality options

## Example Output

### Automatic Mode
```
Title: My Awesome Video
Total size from headers: 157286400
Number of chunks: 19
Downloading video: 100%|██████████| 150M/150M [00:45<00:00, 3.33MB/s]
Video downloaded successfully!
Downloaded: my-awesome-video.mp4
```

### Interactive Mode
```
Title: My Awesome Video
[0] Found 480p stream
[1] Found 720p stream
[2] Found 1080p stream
Enter the index of the stream you want to download: 2
Total size from headers: 157286400
Number of chunks: 19
Downloading video: 100%|██████████| 150M/150M [00:45<00:00, 3.33MB/s]
Video downloaded successfully!
Downloaded: my-awesome-video.mp4
```

## Troubleshooting

### Common Issues

**"No suitable video stream found"**
- The video may not have transcoded streams available
- Check if the video is accessible and not private
- Try a different video URL

**"Invalid stream index"**
- Make sure to enter a valid number from the displayed options
- Index should be within the range of available streams

**"Could not determine file size"**
- The video may be restricted or the URL is invalid
- Verify the Google Drive URL is correct
- Check if the video is publicly accessible

**Network timeouts**
- Increase `max_retries` and `retry_delay`
- Reduce `max_workers` for unstable connections

**Rate limiting (429 errors)**
- The downloader automatically handles rate limits
- For persistent issues, reduce `max_workers` or add delays between downloads

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational purposes. Make sure you have permission to download videos and comply with Google Drive's Terms of Service.
