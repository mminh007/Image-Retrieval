import os 
import json
import requests
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
import urllib.request
import concurrent.futures
import time


class ImageDownloader():
	def __init__(self, json_file, download_dir, max_workers, delay):
		self.json_file = json_file
		self.download_dir = download_dir
		self.max_workers = max_workers
		self.delay = delay

		self.filename = set()
		#self.setup_directory()

	def setup_directory(self):
		if not os.path.exists(self.download_dir):
			os.makedirs(self.download_dir)
		
	def read_json(self):
		with open(self.json_file, "r") as f:
			data = json.load(f)
		return data
		
	def is_valid_url(self, url):
		"""
		"""
		try:
			with urllib.request.urlopen(url) as response:
				if response.status == 200 and "image" in response.info().get_content_type():
					return True
			
		except Exception:
			return False
			

	def download_image(self, url, category, term, pbar):
		"""
		"""
		if not self.is_valid_url(url):
			pbar.update(1)
			return f"Invalid URL: {url}"

		category_dir = os.path.join(self.download_dir, category)
		if not os.path.exists(category_dir):
			os.makedirs(category_dir)
		
		term_dir = os.path.join(category_dir, term)
		if not os.path.exists(term_dir):
			os.makedirs(term_dir)

		filename = os.path.join(term_dir, os.path.basename(urlparse(url).path))
		self.filename.add(filename)

		try:
			urllib.request.urlretrieve(url, filename)
			pbar.update(1)
			return f"Download: {url}"
		
		except Exception as e:
			pbar.update(1)
			return f"Failed to download {url}: {str(e)}"
		

	def download_image(self):
		data = self.read_json()
		download_taks = []

		total_images = sum(len(url) for terms in data.values() for url in terms.values())
		with tqdm(total = total_images, desc = "Downloading Images") as pbar:
			with concurrent.futures.ThreadPoolExecutor(max_workers= self.max_workers) as executor:
				for category, terms in data.items():
					for term, urls in terms.items():
						for url in urls:
							download_taks.append(executor.submit(self.download_image, url,
													category, term, pbar))
							time.sleep(self.delay)

				for future in concurrent.futures.as_completed(download_taks):
					print(future.result())

		self.export_filename()
	

	def export_filename(self):
		with open("filename.txt", "w") as f:
			for filename in sorted(self.filename):
				f.write(f"{filename}\n")
				