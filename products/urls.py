from django.urls import path
from .views import ProductListAPI, ProductScrapeAPI, ProductCreateAPI, ProductUpdatePricesAPI

urlpatterns = [
    path('api/products/', ProductListAPI.as_view(), name='api-product-list'),
    path('api/products/scrape/', ProductScrapeAPI.as_view(), name='api-product-scrape'),
    path('api/products/create/', ProductCreateAPI.as_view(), name='api-product-create'),
    path('api/products/update_prices/', ProductUpdatePricesAPI.as_view(), name='api-product-update-prices'),
]