from crawl import UrlScrapper
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Build a retrieval database')
    parser.add_argument("--data_config",
                        type=str,
                        required=True,
                        default = "./cfg/data.json")
    
    parser.add_argument("--source",
                        type=str,
                        default="flickr")
    
    parser.add_argument("--max_images",
                        type=int,
                        default=50,
                        required=True)
    
    parser.add_argument("--max_workers",
                        type=int,
                        default=4)
    
    parser.add_argument("--saved_filename",
                        type=str,
                        default = "./cfg/flickr_50.json")
    
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    with open(args.data_config, "r") as f:
        data = json.load(f)

    url_template = data["url"][args.source]
    categories = data["labels"]

    scraper = UrlScrapper(url_template=url_template,
                          max_images = args.max_images,
                          max_workers = args.max_workers)
    
    image_urls = scraper.scrape_urls(categories=categories)
    scraper.save_to_file(image_urls, args.saved_filename)


if __name__ == "__main__":
    main()
