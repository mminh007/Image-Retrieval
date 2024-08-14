import argparse
from techniques.embedding import build_collector, search
from techniques.process import plot_results, get_files_path



def parse_args():
    parser = argparse.ArgumentParser(description='Build a retrieval database')
    parser.add_argument("--query_data",
                        type=str,
                        required=True,
                        default = None)
    
    parser.add_argument("--distance",
                        type = str,
                        required=True,
                        default = "l2")
    
    parser.add_argument("--query_image",
                        type=str,
                        default=None)
    
    parser.add_argument("--n_results",
                        type=int,
                        default=5,
                        required=True)
      
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    files_path = get_files_path(args.query_data)
    
    collection = build_collector(args.query_data, distance = args.distance)

    results = search(image_path = args.query_image, collection = collection, n_results = args.n_results)

    plot_results(image_path = args.query_image, files_path = files_path, results = results)



if __name__ == "__main__":
    main()