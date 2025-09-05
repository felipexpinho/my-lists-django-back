from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from .models import Product, Stock, Store
from .serializers import ProductSerializer, StockSerializer, StoreSerializer
from .pagination import ProductPagination
from django.db.models import Q

from .scrapper import get_product_info_from_url

class ProductListAPI(generics.ListAPIView):
    '''
    GET /api/products/?product_search=${productSearch}&store=${store}&page=${page}&page_size=${pageSize}
    '''
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Product.objects.all().order_by('name')

        # Filtro por nome
        product_name = self.request.GET.get('product_search')
        if product_name:
            queryset = queryset.filter(name__icontains=product_name)

        # Filtro por loja
        store_name = self.request.GET.get('store')
        if store_name:
            queryset = queryset.filter(stock__store__name__icontains=store_name).distinct()

        return queryset
    
class ProductScrapeAPI(APIView):
    '''
    GET /api/products/scrape/?link=${encodeURIComponent(produtoUrl)}
    '''
    permission_classes = [permissions.IsAuthenticated]  # apenas usuários logados podem usar

    def get(self, request):
        url = request.GET.get("link")
        if not url:
            return Response(
                {"success": False, "message": "Link não fornecido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product_data = get_product_info_from_url(url)
            
            if isinstance(product_data, str):  # se retornou mensagem de erro
                return Response(
                    {"success": False, "message": product_data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product_data["success"] = True
            return Response(product_data)
        
        except Exception as e:
            return Response(
                {"success": False, "message": f"Erro ao processar link: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ProductCreateAPI(APIView):
    '''
    POST /api/products/create/
    '''
    permission_classes = [permissions.IsAuthenticated]  # apenas usuários logados podem criar

    def post(self, request):
        data = request.data

        # Extraindo campos do JSON
        name = data.get("name")
        price = data.get("price")
        is_available = data.get("is_available")
        category = data.get("category")
        sub_group = data.get("sub_group")
        link = data.get("link")
        photo = data.get("photo")
        store_name = data.get("store")

        if not all([name, price, is_available, category, sub_group, link, photo, store_name]):
            return Response({"success": False, "message": "Campos incompletos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtem o store
            store_instance = Store.objects.get(name=store_name)

            # Cria o produto
            new_product = Product.objects.create(name=name)

            # Cria o stock associado
            Stock.objects.create(
                price=price,
                is_available=is_available,
                url=link,
                photo=photo,
                category=category,
                sub_group=sub_group,
                store=store_instance,
                product=new_product,
            )

            # Retorna o produto criado
            serializer = ProductSerializer(new_product)
            return Response({"success": True, "product": serializer.data}, status=status.HTTP_201_CREATED)

        except Store.DoesNotExist:
            return Response({"success": False, "message": "Loja não encontrada"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductUpdatePricesAPI(APIView):
    """
    PATCH /api/products/update_prices/
    Recebe JSON opcional:
    {
        "product_ids": [1, 2, 3]  # se não fornecido, atualiza todos
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        product_ids = request.data.get("product_ids", None)

        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
        else:
            products = Product.objects.all()

        updated_products = []

        for product in products:
            stock = Stock.objects.filter(product=product).first()
            if not stock:
                continue

            try:
                product_info = get_product_info_from_url(stock.url)
                if not product_info or isinstance(product_info, str):
                    continue

                changed = False

                if stock.price != product_info["price"]:
                    stock.price = product_info["price"]
                    changed = True

                if stock.is_available != product_info["is_available"]:
                    stock.is_available = product_info["is_available"]
                    changed = True

                if changed:
                    stock.save()
                    updated_products.append(product.id)

            except Exception:
                continue

        return Response({
            "success": True,
            "updated_products": updated_products,
            "total_updated": len(updated_products)
        }, status=status.HTTP_200_OK)