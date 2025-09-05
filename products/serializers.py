from rest_framework import serializers
from .models import Product, Stock, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "logo", "url"]


class StockSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    history = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            "id",
            "price",
            "is_available",
            "url",
            "photo",
            "category",
            "sub_group",
            "store",
            "history"
        ]

    def get_history(self, obj):
        # pega os últimos registros do histórico
        qs = obj.history.all().order_by("history_date")  # ou "-history_date" se quiser mais recente primeiro
        return StockHistorySerializer(qs, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    stocks = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "stocks"]

    def get_stocks(self, obj):
        stocks = obj.stock_set.all()
        return StockSerializer(stocks, many=True).data


class StockHistorySerializer(serializers.Serializer):
    price = serializers.FloatField()
    history_date = serializers.DateTimeField()