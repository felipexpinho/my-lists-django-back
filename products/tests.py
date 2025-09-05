from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import Product, Store, Stock

class ProductListAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Criar lojas
        store1 = Store.objects.create(name="Loja A", logo="", url="")
        store2 = Store.objects.create(name="Loja B", logo="", url="")

        # Criar produtos e stocks
        for i in range(1, 11):
            product = Product.objects.create(name=f"Produto {i}")
            stock_store = store1 if i % 2 == 0 else store2
            Stock.objects.create(
                product=product,
                store=stock_store,
                price=100 + i*20,
                is_available=True,
                url="",
                photo="",
                category="Categoria",
                sub_group="Subgrupo"
            )

    def setUp(self):
        self.client = APIClient()  # APIClient do DRF

    def test_status_code_ok(self):
        """Verifica se o endpoint responde 200"""
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_contains_expected_fields(self):
        """Verifica se os produtos retornados possuem os campos do serializer"""
        response = self.client.get("/api/products/")
        data = response.json()
        first_item = data["results"][0]
        expected_fields = ["id", "name", "stocks"]
        for field in expected_fields:
            self.assertIn(field, first_item)

    def test_filter_by_name(self):
        """Verifica se o filtro por nome funciona"""
        response = self.client.get("/api/products/?product_search=Produto 1")
        data = response.json()
        for item in data["results"]:
            self.assertIn("Produto 1", item["name"])

    def test_filter_by_store(self):
        """Verifica se o filtro por loja funciona"""
        response = self.client.get("/api/products/?store=Loja A")
        data = response.json()
        for item in data["results"]:
            store_names = [s["store"]["name"] for s in item["stocks"]]
            self.assertTrue(any("Loja A" in name for name in store_names))

    def test_filter_by_name_and_store(self):
        """Verifica filtros combinados"""
        response = self.client.get("/api/products/?product_search=Produto 2&store=Loja A")
        data = response.json()
        for item in data["results"]:
            self.assertIn("Produto 2", item["name"])
            store_names = [s["store"]["name"] for s in item["stocks"]]
            self.assertTrue(any("Loja A" in name for name in store_names))

    def test_pagination(self):
        """Verifica se a paginação funciona"""
        response = self.client.get("/api/products/?page=1&page_size=5")
        data = response.json()
        self.assertEqual(len(data["results"]), 5)

        response2 = self.client.get("/api/products/?page=2&page_size=5")
        data2 = response2.json()
        self.assertEqual(len(data2["results"]), 5)

    def test_page_out_of_range(self):
        """Página maior que o total de páginas retorna vazio"""
        response = self.client.get("/api/products/?page=100&page_size=5")
        data = response.json()
        self.assertEqual(len(data["results"]), 0)

    def test_no_results(self):
        """Filtro que não retorna nenhum produto"""
        response = self.client.get("/api/products/?product_search=ProdutoXYZ")
        data = response.json()
        self.assertEqual(len(data["results"]), 0)

    def test_large_page_size(self):
        """Testa page_size maior que o número de produtos"""
        response = self.client.get("/api/products/?page_size=50")
        data = response.json()
        self.assertEqual(len(data["results"]), 10)  # só existem 10 produtos no setup


class ProductScrapeAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Criar um usuário para autenticação
        cls.user = User.objects.create_user(username="testuser", password="12345")

    def setUp(self):
        self.client = APIClient()
        self.client.login(username="testuser", password="12345")
        self.valid_url = "https://www.kabum.com.br/produto/placa-de-video"
        self.invalid_url = "https://www.kabum.com.br/produto/invalido"

    def test_requires_authentication(self):
        """Falha quando usuário não está autenticado"""
        self.client.logout()
        response = self.client.get(f"/api/products/scrape/?link={self.valid_url}")
        self.assertIn(response.status_code, [401, 403])

    def test_missing_link(self):
        """Falha quando o link está faltando"""
        response = self.client.get("/api/products/scrape/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)

    @patch("products.views.get_product_info_from_url")
    def test_invalid_link(self, mock_scrape):
        """Falha quando o link é inválido"""
        mock_scrape.return_value = "Link inválido!"
        response = self.client.get(f"/api/products/scrape/?link={self.invalid_url}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertIn("Link inválido", response.json()["message"])

    @patch("products.views.get_product_info_from_url")
    def test_valid_link(self, mock_scrape):
        """Retorna o produto do link selecionado"""
        # Simula retorno de dados do produto
        mock_scrape.return_value = {
            "name": "RTX 5070",
            "price": 4999.99,
            "category": "Placa de Vídeo",
            "sub_group": "NVIDIA",
            "is_available": True,
            "link": self.valid_url,
            "photo": "https://img.kabum.com.br/produto.jpg",
            "store": "Kabum",
            "store_url": "https://www.kabum.com.br"
        }
        response = self.client.get(f"/api/products/scrape/?link={self.valid_url}")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["name"], "RTX 5070")
        self.assertEqual(data["store"], "Kabum")

    @patch("products.views.get_product_info_from_url")
    def test_internal_error(self, mock_scrape):
        """Simula erro interno inesperado"""
        mock_scrape.side_effect = Exception("Erro inesperado")
        response = self.client.get(f"/api/products/scrape/?link={self.valid_url}")
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.json()["success"])
        self.assertIn("Erro ao processar link", response.json()["message"])


class ProductCreateAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Criar usuário para autenticação
        cls.user = User.objects.create_user(username="testuser", password="12345")
        # Criar loja válida
        cls.store = Store.objects.create(name="Loja Teste", logo="", url="")

    def setUp(self):
        self.client = APIClient()
        self.client.login(username="testuser", password="12345")
        self.valid_payload = {
            "name": "Produto Teste",
            "price": 199.99,
            "is_available": True,
            "category": "Categoria X",
            "sub_group": "Subgrupo Y",
            "link": "https://example.com/produto",
            "photo": "https://example.com/foto.jpg",
            "store": self.store.name
        }
        
    def test_authentication_required(self):
        """Falha quando usuário não está autenticado"""
        self.client.logout()
        response = self.client.post("/api/products/create/", data=self.valid_payload, format='json')
        self.assertIn(response.status_code, [401, 403])

    def test_successful_creation(self):
        """Criação de produto com todos os campos corretos"""
        response = self.client.post("/api/products/create/", data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["product"]["name"], self.valid_payload["name"])
        self.assertEqual(len(data["product"]["stocks"]), 1)
        self.assertEqual(data["product"]["stocks"][0]["store"]["name"], self.store.name)

    def test_missing_fields(self):
        """Falha quando algum campo obrigatório está faltando"""
        payload = self.valid_payload.copy()
        payload.pop("price")  # remove um campo obrigatório
        response = self.client.post("/api/products/create/", data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["message"], "Campos incompletos")

    def test_nonexistent_store(self):
        """Falha quando a loja não existe"""
        payload = self.valid_payload.copy()
        payload["store"] = "Loja Inexistente"
        response = self.client.post("/api/products/create/", data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["message"], "Loja não encontrada")

    @patch("products.views.Product.objects.create")
    def test_internal_error(self, mock_create):
        """Simula erro interno inesperado"""
        mock_create.side_effect = Exception("Erro inesperado")
        response = self.client.post("/api/products/create/", data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.json()["success"])
        self.assertIn("Erro inesperado", response.json()["message"])


class ProductUpdatePricesAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Criar usuário para autenticação
        cls.user = User.objects.create_user(username="testuser", password="12345")
        # Criar loja válida
        cls.store = Store.objects.create(name="Loja Teste", logo="", url="")

        # Criar produtos e stocks
        cls.products = []
        for i in range(1, 6):
            product = Product.objects.create(name=f"Produto {i}")
            Stock.objects.create(
                product=product,
                store=cls.store,
                price=100 + i*10,
                is_available=True,
                url=f"https://linkproduto{i}.com",
                photo="",
                category="Categoria",
                sub_group="Subgrupo"
            )
            cls.products.append(product)

    def setUp(self):
        # Configura client autenticado
        self.client = APIClient()
        self.client.login(username="testuser", password="12345")

    def test_requires_authentication(self):
        """Falha quando usuário não está autenticado"""
        self.client.logout()
        response = self.client.patch("/api/products/update_prices/")
        self.assertIn(response.status_code, [401, 403])

    @patch("products.views.get_product_info_from_url")
    def test_update_all_products(self, mock_scrape):
        """Atualiza todos os produtos sem fornecer IDs e verifica se os produtos são atualizados corretamente"""
        # Simula alterações de preço e disponibilidade
        def side_effect(url):
            return {"price": 999, "is_available": False}
        mock_scrape.side_effect = side_effect

        response = self.client.patch("/api/products/update_prices/")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_updated"], len(self.products))
        self.assertEqual(len(data["updated_products"]), len(self.products))

        # Verifica no banco
        for product in self.products:
            stock = product.stock_set.first()
            self.assertEqual(stock.price, 999)
            self.assertFalse(stock.is_available)

    @patch("products.views.get_product_info_from_url")
    def test_update_specific_products(self, mock_scrape):
        """Atualiza apenas produtos específicos via product_ids"""
        product_ids = [self.products[0].id, self.products[1].id]
        mock_scrape.side_effect = lambda url: {"price": 1111, "is_available": True}

        response = self.client.patch("/api/products/update_prices/", {"product_ids": product_ids}, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(set(data["updated_products"]), set(product_ids))
        self.assertEqual(data["total_updated"], len(product_ids))

    @patch("products.views.get_product_info_from_url")
    def test_no_stock_products(self, mock_scrape):
        """Produtos sem stock não devem causar erro"""
        # Criar produto sem stock
        product_no_stock = Product.objects.create(name="Sem Stock")
        mock_scrape.return_value = {"price": 500, "is_available": True}

        response = self.client.patch("/api/products/update_prices/")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        # Produto sem stock não deve aparecer na lista de atualizados
        self.assertNotIn(product_no_stock.id, data["updated_products"])

    @patch("products.views.get_product_info_from_url")
    def test_scrape_returns_invalid_data(self, mock_scrape):
        """Scrapper retorna None ou string (erro), fazendo com que o produto não deva ser atualizado"""
        mock_scrape.side_effect = lambda url: "Erro"  # retorno inválido
        response = self.client.patch("/api/products/update_prices/")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_updated"], 0)
        self.assertEqual(data["updated_products"], [])

    @patch("products.views.get_product_info_from_url")
    def test_scrape_raises_exception(self, mock_scrape):
        """Scrapper levanta exceção não quebrando o endpoint"""
        mock_scrape.side_effect = Exception("Erro inesperado")
        response = self.client.patch("/api/products/update_prices/")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        # Nenhum produto foi atualizado
        self.assertEqual(data["total_updated"], 0)