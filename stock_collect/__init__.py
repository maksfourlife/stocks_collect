from loading import Loader


if __name__ == "__main__":
    loader = Loader("websites.json")
    loader.load_pages()
    for data in loader.get_data():
        pass
