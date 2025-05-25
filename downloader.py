import requests
from tqdm import tqdm
import concurrent.futures
import math
import os
from slugify import slugify
import time
import sys


class GoogleDriveVideoDownloader:
    """A class to download videos from Google Drive using parallel chunk downloading"""
    
    def __init__(self, chunk_size=8*1024*1024, stream_chunk_size=8192, max_workers=8, 
                 max_retries=3, retry_delay=2):
        """
        Initialize the downloader with configurable parameters
        
        Args:
            chunk_size (int): Size of chunks for parallel download (default: 8MB)
            stream_chunk_size (int): Size of streaming chunks (default: 8KB)
            max_workers (int): Maximum number of parallel workers (default: 8)
            max_retries (int): Maximum number of retry attempts (default: 3)
            retry_delay (int): Delay between retries in seconds (default: 2)
        """
        self.chunk_size = chunk_size
        self.stream_chunk_size = stream_chunk_size
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.temp_chunks_dir = 'temp_chunks'
        
        # Google Drive API constants
        self.api_key = 'AIzaSyDVQw45DwoYh632gvsP5vPDqEKvb-Ywnb8'
        self.api_unique = 'gc078'
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://drive.google.com',
            'referer': 'https://drive.google.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }
    
    def extract_video_id(self, video_url):
        """
        Extract video ID from Google Drive URL
        
        Args:
            video_url (str): Google Drive video URL
            
        Returns:
            str: Video ID
        """
        try:
            return video_url.split('/d/')[1].split('/view')[0]
        except IndexError:
            raise ValueError("Invalid Google Drive URL format")
    
    
    def get_video_stream_info(self, video_id, headers):
        """
        Get video streaming information from Google Drive
        
        Args:
            video_id (str): Google Drive video ID
            headers (dict): Request headers
            
        Returns:
            tuple: (stream_url, content_length, video_title)
        """
        url = f'https://workspacevideo-pa.clients6.google.com/v1/drive/media/{video_id}/playback'
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    params={'key': self.api_key, '$unique': self.api_unique},
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    jd = response.json()
                    storage = jd.get('mediaStreamingData', {}).get('formatStreamingData', {})
                    transcoding = storage.get('progressiveTranscodes', [])
                    video_title = jd.get("mediaMetadata", {}).get("title", "untitled_video")
                    
                    for index, t in enumerate(transcoding)  :
                        metadata = t.get('transcodeMetadata', {})
                        quality = metadata.get('width', 0)
                        
                        resolution = f"{quality}p" if quality > 0 else "unknown"
                        print(f"[{index}] Found {resolution} stream")
                    
                    choice = input("Enter the index of the stream you want to download: ")
                    try:
                        choice = int(choice)
                    except ValueError:
                        raise ValueError("Invalid stream index")
                    
                    choosed_stream = transcoding[choice]
                    return choosed_stream.get('url')  , video_title
                    
                    raise Exception("No suitable video stream found")
                
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                        
                raise Exception(f"Failed to get video info. Status code: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Network error: {str(e)}")
        
        raise Exception("Max retries exceeded")
    
    def get_actual_file_size(self, stream_url, headers):
        """
        Get the actual file size from headers
        
        Args:
            stream_url (str): Video stream URL
            headers (dict): Request headers
            
        Returns:
            int: File size in bytes
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.head(stream_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return int(response.headers.get('content-length', 0))
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                raise Exception(f"Failed to get file size. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Network error: {str(e)}")
        
        raise Exception("Max retries exceeded")
    
    def download_chunk(self, stream_url, chunk_index, total_size, headers):
        """
        Download a single chunk of the video
        
        Args:
            stream_url (str): Video stream URL
            chunk_index (int): Index of the chunk to download
            total_size (int): Total file size
            headers (dict): Request headers
            
        Returns:
            int: Chunk index if successful
        """
        start = chunk_index * self.chunk_size
        end = min(start + self.chunk_size - 1, total_size - 1)
        
        chunk_headers = headers.copy()
        chunk_headers['Range'] = f'bytes={start}-{end}'
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(stream_url, headers=chunk_headers, stream=True, timeout=30)
                
                if response.status_code in [200, 206]:
                    chunk_file = os.path.join(self.temp_chunks_dir, f'chunk_{chunk_index}')
                    with open(chunk_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=self.stream_chunk_size):
                            if chunk:
                                f.write(chunk)
                    return chunk_index
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                raise Exception(f"Failed to download chunk {chunk_index}. Status code: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Network error in chunk {chunk_index}: {str(e)}")
        
        raise Exception(f"Max retries exceeded for chunk {chunk_index}")
    
    def download_video_in_chunks(self, stream_url, file_name, total_size, headers):
        """
        Download video in parallel chunks and combine them
        
        Args:
            stream_url (str): Video stream URL
            file_name (str): Output file name
            total_size (int): Total file size
            headers (dict): Request headers
        """
        num_chunks = math.ceil(total_size / self.chunk_size)
        print(f"Number of chunks: {num_chunks}")
        
        # Create temporary directory for chunks
        os.makedirs(self.temp_chunks_dir, exist_ok=True)
        
        try:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading video') as pbar:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [
                        executor.submit(self.download_chunk, stream_url, i, total_size, headers)
                        for i in range(num_chunks)
                    ]
                    
                    # Collect completed chunks in order
                    completed_chunks = {}
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            chunk_index = future.result()
                            completed_chunks[chunk_index] = True
                        except Exception as e:
                            print(f"Error downloading chunk: {str(e)}")
                            raise
                    
                    # Write chunks to output file in order
                    with open(file_name, 'wb') as outfile:
                        for chunk_index in range(num_chunks):
                            chunk_file = os.path.join(self.temp_chunks_dir, f'chunk_{chunk_index}')
                            
                            if os.path.exists(chunk_file):
                                with open(chunk_file, 'rb') as infile:
                                    data = infile.read()
                                    outfile.write(data)
                                    pbar.update(len(data))
                                
                                os.remove(chunk_file)
                            else:
                                raise Exception(f"Chunk {chunk_index} not found")
        finally:
            # Clean up temporary directory
            if os.path.exists(self.temp_chunks_dir):
                try:
                    os.rmdir(self.temp_chunks_dir)
                except OSError:
                    print("Warning: Could not remove temporary directory")
    
    def download(self, video_url, headers=None, output_filename=None):
        """
        Download a video from Google Drive
        
        Args:
            video_url (str): Google Drive video URL
            headers (dict, optional): Custom headers. If None, default headers are used
            output_filename (str, optional): Custom output filename. If None, uses video title
            
        Returns:
            str: Downloaded file name
        """
        try:
            # Extract video ID from URL
            video_id = self.extract_video_id(video_url)
            
            # Use default headers if none provided
            if headers is None:
                headers = self.headers
            
            # Get video stream URL and size
            stream_url, video_title = self.get_video_stream_info(video_id, headers)
            print(f"Title: {video_title}")
            
            # Determine output filename
            if output_filename is None:
                file_name = slugify(video_title) + ".mp4"
            else:
                file_name = output_filename
            
            # Verify actual file size
            actual_size = self.get_actual_file_size(stream_url, headers)
            if actual_size > 0:
                total_size = actual_size
            print(f"Total size from headers: {total_size}")
            
            if total_size == 0:
                raise ValueError("Could not determine file size. Please check if the video is accessible.")
            
            # Download the video
            self.download_video_in_chunks(stream_url, file_name, total_size, headers)
            
            print("Video downloaded successfully!")
            return file_name
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # Initialize the downloader
    downloader = GoogleDriveVideoDownloader()
    # Example video URL
    video_url = input("Enter the video URL: ").strip()
    try:
        # Download the video
        downloaded_file = downloader.download(video_url)
        print(f"Downloaded: {downloaded_file}")
    except Exception as e:
        print(f"Download failed: {str(e)}")
        sys.exit(1)
