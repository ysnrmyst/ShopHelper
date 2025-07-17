"""
商品検索エージェント
商品検索とモック商品データの生成
"""

import logging
import asyncio
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from utils.helpers import (
    create_mock_product_data, 
    sort_products_by_relevance,
    merge_product_data,
    format_price
)

logger = logging.getLogger(__name__)

class ProductSearchAgent:
    """商品検索エージェント"""
    
    def __init__(self):
        """初期化"""
        self.is_initialized = False
        self.mock_products = []
        self.search_history = []
        
        # モック商品データの初期化
        self._initialize_mock_products()
    
    async def initialize(self) -> None:
        """エージェントの初期化"""
        try:
            logger.info("Initializing ProductSearchAgent...")
            
            # 初期化処理（将来的にAPIクライアントの初期化など）
            await asyncio.sleep(0.1)  # 非同期処理のシミュレーション
            
            self.is_initialized = True
            logger.info("ProductSearchAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ProductSearchAgent: {e}")
            raise
    
    async def cleanup(self) -> None:
        """エージェントのクリーンアップ"""
        try:
            logger.info("Cleaning up ProductSearchAgent...")
            self.is_initialized = False
            logger.info("ProductSearchAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup ProductSearchAgent: {e}")
    
    def is_ready(self) -> bool:
        """エージェントの準備状況を確認"""
        return self.is_initialized
    
    def _initialize_mock_products(self) -> None:
        """モック商品データを初期化"""
        self.mock_products = [
            # スマートフォン
            {
                "id": "phone_001",
                "name": "iPhone 15",
                "price": 120000,
                "description": "最新のiPhone 15。高性能カメラと長いバッテリーライフを搭載。",
                "category": "electronics",
                "subcategory": "smartphone",
                "brand": "Apple",
                "rating": 4.8,
                "review_count": 1250,
                "image_url": "https://via.placeholder.com/300x300?text=iPhone+15",
                "features": ["5G", "wireless", "waterproof"],
                "stores": [
                    {"name": "Apple Store", "price": 120000, "shipping": 0},
                    {"name": "楽天市場", "price": 118000, "shipping": 500},
                    {"name": "Amazon", "price": 119000, "shipping": 0}
                ]
            },
            {
                "id": "phone_002",
                "name": "Samsung Galaxy S24",
                "price": 110000,
                "description": "Samsungの最新フラッグシップ。高性能プロセッサと美しいディスプレイ。",
                "category": "electronics",
                "subcategory": "smartphone",
                "brand": "Samsung",
                "rating": 4.6,
                "review_count": 890,
                "image_url": "https://via.placeholder.com/300x300?text=Galaxy+S24",
                "features": ["5G", "wireless", "waterproof"],
                "stores": [
                    {"name": "Samsung Store", "price": 110000, "shipping": 0},
                    {"name": "楽天市場", "price": 108000, "shipping": 500},
                    {"name": "Amazon", "price": 109000, "shipping": 0}
                ]
            },
            # ノートPC
            {
                "id": "laptop_001",
                "name": "MacBook Air M2",
                "price": 180000,
                "description": "軽量で高性能なMacBook Air。M2チップ搭載で長時間バッテリー。",
                "category": "electronics",
                "subcategory": "laptop",
                "brand": "Apple",
                "rating": 4.9,
                "review_count": 2100,
                "image_url": "https://via.placeholder.com/300x300?text=MacBook+Air",
                "features": ["lightweight", "wireless", "high_speed"],
                "stores": [
                    {"name": "Apple Store", "price": 180000, "shipping": 0},
                    {"name": "楽天市場", "price": 178000, "shipping": 500},
                    {"name": "Amazon", "price": 179000, "shipping": 0}
                ]
            },
            {
                "id": "laptop_002",
                "name": "Dell XPS 13",
                "price": 160000,
                "description": "ビジネス向けの高性能ノートPC。軽量で持ち運びやすい。",
                "category": "electronics",
                "subcategory": "laptop",
                "brand": "Dell",
                "rating": 4.5,
                "review_count": 750,
                "image_url": "https://via.placeholder.com/300x300?text=Dell+XPS+13",
                "features": ["lightweight", "compact", "high_speed"],
                "stores": [
                    {"name": "Dell Store", "price": 160000, "shipping": 0},
                    {"name": "楽天市場", "price": 158000, "shipping": 500},
                    {"name": "Amazon", "price": 159000, "shipping": 0}
                ]
            },
            # 服
            {
                "id": "clothing_001",
                "name": "Nike Air Max 270",
                "price": 15000,
                "description": "快適な履き心地のNikeスニーカー。スタイリッシュなデザイン。",
                "category": "clothing",
                "subcategory": "shoes",
                "brand": "Nike",
                "rating": 4.7,
                "review_count": 3200,
                "image_url": "https://via.placeholder.com/300x300?text=Nike+Air+Max",
                "features": ["comfortable", "stylish", "lightweight"],
                "stores": [
                    {"name": "Nike Store", "price": 15000, "shipping": 0},
                    {"name": "楽天市場", "price": 14800, "shipping": 500},
                    {"name": "Amazon", "price": 14900, "shipping": 0}
                ]
            },
            {
                "id": "clothing_002",
                "name": "Uniqlo ダウンジャケット",
                "price": 8000,
                "description": "軽量で暖かいダウンジャケット。シンプルで使いやすいデザイン。",
                "category": "clothing",
                "subcategory": "jacket",
                "brand": "Uniqlo",
                "rating": 4.4,
                "review_count": 5600,
                "image_url": "https://via.placeholder.com/300x300?text=Uniqlo+Down",
                "features": ["lightweight", "warm", "compact"],
                "stores": [
                    {"name": "Uniqlo", "price": 8000, "shipping": 0},
                    {"name": "楽天市場", "price": 7800, "shipping": 500},
                    {"name": "Amazon", "price": 7900, "shipping": 0}
                ]
            },
            # 本
            {
                "id": "book_001",
                "name": "Pythonプログラミング入門",
                "price": 2500,
                "description": "初心者向けのPythonプログラミング本。わかりやすい解説付き。",
                "category": "books",
                "subcategory": "programming",
                "brand": "技術評論社",
                "rating": 4.6,
                "review_count": 450,
                "image_url": "https://via.placeholder.com/300x300?text=Python+Book",
                "features": ["educational", "beginner_friendly"],
                "stores": [
                    {"name": "Amazon", "price": 2500, "shipping": 0},
                    {"name": "楽天ブックス", "price": 2480, "shipping": 500},
                    {"name": "紀伊國屋書店", "price": 2500, "shipping": 0}
                ]
            },
            # 食品
            {
                "id": "food_001",
                "name": "有機野菜セット",
                "price": 3000,
                "description": "新鮮な有機野菜のセット。健康に良い食材をお届け。",
                "category": "food",
                "subcategory": "vegetables",
                "brand": "オーガニックファーム",
                "rating": 4.3,
                "review_count": 1200,
                "image_url": "https://via.placeholder.com/300x300?text=Organic+Vegetables",
                "features": ["organic", "fresh", "healthy"],
                "stores": [
                    {"name": "オーガニックファーム", "price": 3000, "shipping": 500},
                    {"name": "楽天市場", "price": 2980, "shipping": 500},
                    {"name": "Amazon", "price": 2990, "shipping": 500}
                ]
            }
        ]
    
    async def search_products(self, preferences: Dict[str, Any], session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        商品検索を実行
        
        Args:
            preferences: 検索条件
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: 検索結果
        """
        try:
            start_time = time.time()
            
            # 検索条件を解析
            search_query = preferences.get("query", "")
            user_preferences = session_data.get("user_preferences", {})
            
            # 商品をフィルタリング
            filtered_products = self._filter_products_by_preferences(
                self.mock_products, search_query, user_preferences
            )
            
            # 関連度でソート
            sorted_products = sort_products_by_relevance(filtered_products, search_query)
            
            # 検索履歴を更新
            self._update_search_history(search_query, len(sorted_products))
            
            search_time = time.time() - start_time
            
            return {
                "products": sorted_products,
                "total_count": len(sorted_products),
                "search_time": search_time,
                "query": search_query,
                "filters_applied": self._get_applied_filters(user_preferences)
            }
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {
                "products": [],
                "total_count": 0,
                "search_time": 0,
                "query": preferences.get("query", ""),
                "filters_applied": {}
            }
    
    def _filter_products_by_preferences(
        self, 
        products: List[Dict[str, Any]], 
        query: str, 
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """希望に基づいて商品をフィルタリング"""
        filtered_products = products.copy()
        
        # クエリによるフィルタリング
        if query:
            query_lower = query.lower()
            filtered_products = [
                p for p in filtered_products
                if (query_lower in p["name"].lower() or 
                    query_lower in p["description"].lower() or
                    query_lower in p["category"].lower() or
                    query_lower in p.get("brand", "").lower())
            ]
        
        # 価格範囲によるフィルタリング
        price_range = preferences.get("price_range")
        if price_range:
            filtered_products = self._filter_by_price_range(filtered_products, price_range)
        
        # ブランドによるフィルタリング
        brands = preferences.get("brands", [])
        if brands:
            filtered_products = [
                p for p in filtered_products
                if p.get("brand") in brands
            ]
        
        # カテゴリによるフィルタリング
        categories = preferences.get("categories", [])
        if categories:
            filtered_products = [
                p for p in filtered_products
                if p.get("category") in categories
            ]
        
        # 機能によるフィルタリング
        features = preferences.get("features", [])
        if features:
            filtered_products = [
                p for p in filtered_products
                if any(feature in p.get("features", []) for feature in features)
            ]
        
        # 除外アイテムによるフィルタリング
        excluded_items = preferences.get("excluded_items", [])
        if excluded_items:
            filtered_products = [
                p for p in filtered_products
                if not any(excluded in p["name"].lower() for excluded in excluded_items)
            ]
        
        return filtered_products
    
    def _filter_by_price_range(self, products: List[Dict[str, Any]], price_range: str) -> List[Dict[str, Any]]:
        """価格範囲でフィルタリング"""
        price_thresholds = {
            "very_low": 5000,
            "low": 15000,
            "medium": 50000,
            "high": 100000,
            "very_high": float('inf')
        }
        
        max_price = price_thresholds.get(price_range, float('inf'))
        
        return [
            p for p in products
            if p["price"] <= max_price
        ]
    
    def _update_search_history(self, query: str, result_count: int) -> None:
        """検索履歴を更新"""
        search_record = {
            "query": query,
            "result_count": result_count,
            "timestamp": datetime.now().isoformat()
        }
        
        self.search_history.append(search_record)
        
        # 履歴が長すぎる場合は古いものを削除
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def _get_applied_filters(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """適用されたフィルターを取得"""
        filters = {}
        
        if preferences.get("price_range"):
            filters["price_range"] = preferences["price_range"]
        
        if preferences.get("brands"):
            filters["brands"] = preferences["brands"]
        
        if preferences.get("categories"):
            filters["categories"] = preferences["categories"]
        
        if preferences.get("features"):
            filters["features"] = preferences["features"]
        
        return filters
    
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        商品詳細を取得
        
        Args:
            product_id: 商品ID
            
        Returns:
            Optional[Dict[str, Any]]: 商品詳細
        """
        try:
            for product in self.mock_products:
                if product["id"] == product_id:
                    return product
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    async def get_recommended_products(self, session_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        おすすめ商品を取得
        
        Args:
            session_data: セッションデータ
            limit: 取得件数
            
        Returns:
            List[Dict[str, Any]]: おすすめ商品リスト
        """
        try:
            # 高評価商品を取得
            high_rated_products = [
                p for p in self.mock_products
                if p.get("rating", 0) >= 4.5
            ]
            
            # ランダムに選択
            recommended = random.sample(high_rated_products, min(limit, len(high_rated_products)))
            
            return recommended
            
        except Exception as e:
            logger.error(f"Error getting recommended products: {e}")
            return []
    
    async def get_popular_products(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        人気商品を取得
        
        Args:
            category: カテゴリ（オプション）
            limit: 取得件数
            
        Returns:
            List[Dict[str, Any]]: 人気商品リスト
        """
        try:
            # レビュー数でソート
            sorted_products = sorted(
                self.mock_products,
                key=lambda p: p.get("review_count", 0),
                reverse=True
            )
            
            # カテゴリでフィルタリング
            if category:
                sorted_products = [
                    p for p in sorted_products
                    if p.get("category") == category
                ]
            
            return sorted_products[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular products: {e}")
            return []
    
    async def compare_products(self, product_ids: List[str]) -> Dict[str, Any]:
        """
        商品を比較
        
        Args:
            product_ids: 商品IDリスト
            
        Returns:
            Dict[str, Any]: 比較結果
        """
        try:
            products = []
            for product_id in product_ids:
                product = await self.get_product_details(product_id)
                if product:
                    products.append(product)
            
            if len(products) < 2:
                return {"error": "比較する商品が不足しています"}
            
            # 比較データを構築
            comparison = {
                "products": products,
                "price_comparison": self._compare_prices(products),
                "feature_comparison": self._compare_features(products),
                "rating_comparison": self._compare_ratings(products)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing products: {e}")
            return {"error": "商品比較中にエラーが発生しました"}
    
    def _compare_prices(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """価格比較"""
        prices = [p["price"] for p in products]
        return {
            "min_price": min(prices),
            "max_price": max(prices),
            "average_price": sum(prices) / len(prices),
            "price_range": max(prices) - min(prices)
        }
    
    def _compare_features(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """機能比較"""
        all_features = set()
        for product in products:
            all_features.update(product.get("features", []))
        
        feature_comparison = {}
        for feature in all_features:
            feature_comparison[feature] = [
                feature in p.get("features", []) for p in products
            ]
        
        return feature_comparison
    
    def _compare_ratings(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """評価比較"""
        ratings = [p.get("rating", 0) for p in products]
        return {
            "highest_rating": max(ratings),
            "lowest_rating": min(ratings),
            "average_rating": sum(ratings) / len(ratings)
        }
    
    async def get_search_suggestions(self, query: str) -> List[str]:
        """
        検索サジェストを取得
        
        Args:
            query: 検索クエリ
            
        Returns:
            List[str]: サジェストリスト
        """
        try:
            suggestions = []
            query_lower = query.lower()
            
            # 商品名からサジェストを生成
            for product in self.mock_products:
                name = product["name"].lower()
                if query_lower in name and name not in suggestions:
                    suggestions.append(product["name"])
            
            # カテゴリからサジェストを生成
            categories = set(p["category"] for p in self.mock_products)
            for category in categories:
                if query_lower in category.lower():
                    suggestions.append(f"{category}の商品")
            
            # ブランドからサジェストを生成
            brands = set(p.get("brand", "") for p in self.mock_products if p.get("brand"))
            for brand in brands:
                if query_lower in brand.lower():
                    suggestions.append(f"{brand}の商品")
            
            return suggestions[:5]  # 最大5個まで
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return [] 