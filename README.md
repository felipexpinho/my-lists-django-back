# Python-Django Back End for my-lists

The back part of a personal project involving getting data from websites via webscraping, displaying these items to users tracking it's price and allowing users to create lists to help them further with tracking the prices of full list components.

Currently the project is being adapted to a separated front-end/back-end as I'm currently learning React. Most of the features are still under development: The authentication process, the lists page and much more.

# Libraries and Frameworks:

**Django**: Base backend framework.

**Django ORM**: Built-in ORM for handling the database.

**Django Test**: Built-in testing framework for writing and running tests.

**beautifulsoup4**: For web scrapping.

**requests**: For handling HTTP requests.

# Database

## Product
| Field | Type | Description |
|-------|------|-------------|
| id    | integer | Unique identifier for the product. |
| name  | string | Name of the product. |

## Store
| Field | Type | Description |
|-------|------|-------------|
| id    | integer | Unique identifier for the store. |
| name  | string | Name of the store. |
| logo  | string | URL or path to the store's logo. |
| url   | string | Link to the store's website. |

## Stock
| Field | Type | Description |
|-------|------|-------------|
| id          | integer | Unique identifier for the stock. |
| store_id    | integer | ID of the store related to this stock. |
| product_id  | integer | ID of the product related to this stock. |
| price       | float   | Price of the product in this store. |
| is_available | boolean | True if the product is available in the store; False if not. |
| url         | string  | Link to the product page in the store. |
| photo       | string  | URL or path to the product photo. |
| category    | string  | Category of the product in the store. |
| sub_group   | string  | Sub-group or sub-category of the product. |
| store       | Store   | The Store related to this Stock. |
| product     | Product | The Product related to this Stock. |
| history     | HistoricalRecords | History tracking for changes in this Stock. |

# Endpoints

## Products

| Endpoint | Method | Expected Payload | Description |
|----------|--------|-----------------|-------------|
| GET /api/products/ | GET | Query params:<br>&nbsp;&nbsp;product_search: Optional[str]<br>&nbsp;&nbsp;store: Optional[str]<br>&nbsp;&nbsp;page: Optional[int]<br>&nbsp;&nbsp;page_size: Optional[int] | Fetch all products, optionally filtered by name or store. Supports pagination. |
| GET /api/products/scrape/ | GET | Query params:<br>&nbsp;&nbsp;link: str | Scrape product info from a given URL. Only for authenticated users. |
| POST /api/products/create/ | POST | {<br>&nbsp;&nbsp;name: str,<br>&nbsp;&nbsp;price: float,<br>&nbsp;&nbsp;is_available: bool,<br>&nbsp;&nbsp;category: str,<br>&nbsp;&nbsp;sub_group: str,<br>&nbsp;&nbsp;link: str,<br>&nbsp;&nbsp;photo: str,<br>&nbsp;&nbsp;store: str<br>} | Create a new product and associated stock. Only for authenticated users. |
| PATCH /api/products/update_prices/ | PATCH | {<br>&nbsp;&nbsp;product_ids: Optional[list[int]]<br>} | Update prices and availability from URLs. If no `product_ids` provided, updates all products. Only for authenticated users. |

### Notes / Additional info:

- **Authentication required**: All `/scrape/`, `/create/`, and `/update_prices/` endpoints require the user to be logged in.
- **Scraper integration**: The `scrape` and `update_prices` endpoints rely on the function `get_product_info_from_url` found on `products/scrapper.py` to fetch real-time product data.
