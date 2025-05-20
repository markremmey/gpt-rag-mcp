class SearchInput:
    def __init__(self, search_query: str):
        self.search_query = search_query

    def get_search_query(self) -> str:
        return self.search_query