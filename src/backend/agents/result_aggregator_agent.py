"""
結果集約エージェント
検索結果を統合してユーザーフレンドリーなレスポンスを生成
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.helpers import format_price, truncate_text

logger = logging.getLogger(__name__)

class ResultAggregatorAgent:
    """結果集約エージェント"""
    
    def __init__(self):
        """初期化"""
        self.is_initialized = False
        
        # レスポンステンプレート
        self.response_templates = {
            "no_results": [
                "申し訳ございません。条件に合う商品が見つかりませんでした。別のキーワードや条件で検索してみてください。",
                "該当する商品が見つかりませんでした。価格帯やカテゴリを変更して再度お試しください。",
                "検索結果が0件でした。より一般的なキーワードで検索してみてください。"
            ],
            "single_result": [
                "見つかった商品をご紹介します。",
                "条件に合う商品を1件見つけました。",
                "検索結果をご確認ください。"
            ],
            "multiple_results": [
                "検索結果をご紹介します。",
                "条件に合う商品を複数見つけました。",
                "お探しの商品が見つかりました。"
            ],
            "price_focus": [
                "価格を重視した商品をご紹介します。",
                "お得な商品をピックアップしました。",
                "コストパフォーマンスの良い商品です。"
            ],
            "quality_focus": [
                "品質を重視した商品をご紹介します。",
                "高評価の商品をピックアップしました。",
                "信頼できる商品です。"
            ]
        }
    
    async def initialize(self) -> None:
        """エージェントの初期化"""
        try:
            logger.info("Initializing ResultAggregatorAgent...")
            
            # 初期化処理（将来的にAIモデルの読み込みなど）
            await asyncio.sleep(0.1)  # 非同期処理のシミュレーション
            
            self.is_initialized = True
            logger.info("ResultAggregatorAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ResultAggregatorAgent: {e}")
            raise
    
    async def cleanup(self) -> None:
        """エージェントのクリーンアップ"""
        try:
            logger.info("Cleaning up ResultAggregatorAgent...")
            self.is_initialized = False
            logger.info("ResultAggregatorAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup ResultAggregatorAgent: {e}")
    
    def is_ready(self) -> bool:
        """エージェントの準備状況を確認"""
        return self.is_initialized
    
    async def generate_response(
        self, 
        user_message: str, 
        search_results: Dict[str, Any], 
        preferences: Dict[str, Any], 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        検索結果を統合してレスポンスを生成
        
        Args:
            user_message: ユーザーメッセージ
            search_results: 検索結果
            preferences: ユーザー希望
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: レスポンス
        """
        try:
            products = search_results.get("products", [])
            total_count = search_results.get("total_count", 0)
            search_time = search_results.get("search_time", 0)
            
            # 結果数に基づいてレスポンスを生成
            if total_count == 0:
                response = self._generate_no_results_response(user_message, preferences)
            elif total_count == 1:
                response = self._generate_single_result_response(products[0], preferences)
            else:
                response = self._generate_multiple_results_response(products, preferences, total_count)
            
            # サジェストを生成
            suggestions = self._generate_suggestions(products, preferences, session_data)
            
            # 商品データを整形
            formatted_products = self._format_products_for_display(products)
            
            return {
                "message": response,
                "products": formatted_products,
                "total_count": total_count,
                "search_time": search_time,
                "suggestions": suggestions,
                "has_products": total_count > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "message": "申し訳ございません。エラーが発生しました。",
                "products": [],
                "total_count": 0,
                "search_time": 0,
                "suggestions": [],
                "has_products": False
            }
    
    def _generate_no_results_response(self, user_message: str, preferences: Dict[str, Any]) -> str:
        """結果が0件の場合のレスポンスを生成"""
        import random
        
        # 基本テンプレートから選択
        base_response = random.choice(self.response_templates["no_results"])
        
        # 希望に基づいてカスタマイズ
        if preferences.get("price_range") == "low":
            base_response += " 価格を少し上げてみることをお勧めします。"
        elif preferences.get("brands"):
            brands = ", ".join(preferences["brands"])
            base_response += f" {brands}以外のブランドもご検討ください。"
        elif preferences.get("categories"):
            categories = ", ".join(preferences["categories"])
            base_response += f" {categories}以外のカテゴリもご検討ください。"
        
        return base_response
    
    def _generate_single_result_response(self, product: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """結果が1件の場合のレスポンスを生成"""
        import random
        
        base_response = random.choice(self.response_templates["single_result"])
        
        # 商品情報を追加
        product_name = product.get("name", "商品")
        price = format_price(product.get("price", 0))
        rating = product.get("rating", 0)
        
        response = f"{base_response}\n\n"
        response += f"【{product_name}】\n"
        response += f"価格: {price}\n"
        
        if rating > 0:
            response += f"評価: {rating}/5.0\n"
        
        description = product.get("description", "")
        if description:
            response += f"説明: {truncate_text(description, 100)}\n"
        
        # 希望に基づいて追加情報
        if preferences.get("price_range") == "low":
            response += "\nこの商品はお求めやすい価格帯です。"
        elif preferences.get("quality") == "high":
            response += "\nこの商品は高評価でおすすめです。"
        
        return response
    
    def _generate_multiple_results_response(
        self, 
        products: List[Dict[str, Any]], 
        preferences: Dict[str, Any], 
        total_count: int
    ) -> str:
        """結果が複数件の場合のレスポンスを生成"""
        import random
        
        base_response = random.choice(self.response_templates["multiple_results"])
        
        # 希望に基づいてレスポンスをカスタマイズ
        if preferences.get("price_range") == "low":
            base_response = random.choice(self.response_templates["price_focus"])
        elif preferences.get("quality") == "high":
            base_response = random.choice(self.response_templates["quality_focus"])
        
        response = f"{base_response}\n"
        response += f"検索結果: {total_count}件\n\n"
        
        # 上位3件の商品を紹介
        top_products = products[:3]
        for i, product in enumerate(top_products, 1):
            product_name = product.get("name", "商品")
            price = format_price(product.get("price", 0))
            rating = product.get("rating", 0)
            
            response += f"{i}. {product_name}\n"
            response += f"   価格: {price}\n"
            
            if rating > 0:
                response += f"   評価: {rating}/5.0\n"
            
            response += "\n"
        
        if total_count > 3:
            response += f"他にも{total_count - 3}件の商品があります。詳細は商品一覧をご確認ください。"
        
        return response
    
    def _format_products_for_display(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """商品データを表示用に整形"""
        formatted_products = []
        
        for product in products:
            formatted_product = {
                "id": product.get("id"),
                "name": product.get("name"),
                "price": product.get("price"),
                "formatted_price": format_price(product.get("price", 0)),
                "description": truncate_text(product.get("description", ""), 150),
                "category": product.get("category"),
                "brand": product.get("brand"),
                "rating": product.get("rating", 0),
                "review_count": product.get("review_count", 0),
                "image_url": product.get("image_url"),
                "features": product.get("features", []),
                "stores": product.get("stores", [])
            }
            
            # 最安値を計算
            if formatted_product["stores"]:
                min_price = min(store.get("price", formatted_product["price"]) for store in formatted_product["stores"])
                formatted_product["min_price"] = min_price
                formatted_product["formatted_min_price"] = format_price(min_price)
            
            formatted_products.append(formatted_product)
        
        return formatted_products
    
    def _generate_suggestions(
        self, 
        products: List[Dict[str, Any]], 
        preferences: Dict[str, Any], 
        session_data: Dict[str, Any]
    ) -> List[str]:
        """サジェストを生成"""
        suggestions = []
        
        if not products:
            suggestions = [
                "価格を変更して検索",
                "カテゴリを変更して検索",
                "別のキーワードで検索"
            ]
        else:
            # 商品に基づくサジェスト
            if len(products) > 1:
                suggestions.append("商品を比較する")
            
            # 価格関連のサジェスト
            prices = [p.get("price", 0) for p in products]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                
                if max_price - min_price > 10000:
                    suggestions.append("価格の安い順で並び替え")
                    suggestions.append("価格の高い順で並び替え")
            
            # 評価関連のサジェスト
            high_rated = [p for p in products if p.get("rating", 0) >= 4.5]
            if high_rated:
                suggestions.append("高評価商品のみ表示")
            
            # ブランド関連のサジェスト
            brands = set(p.get("brand") for p in products if p.get("brand"))
            if len(brands) > 1:
                suggestions.append("ブランドで絞り込み")
        
        return suggestions[:5]  # 最大5個まで
    
    async def generate_comparison_response(self, comparison_data: Dict[str, Any]) -> str:
        """
        商品比較のレスポンスを生成
        
        Args:
            comparison_data: 比較データ
            
        Returns:
            str: 比較レスポンス
        """
        try:
            if "error" in comparison_data:
                return comparison_data["error"]
            
            products = comparison_data.get("products", [])
            if len(products) < 2:
                return "比較する商品が不足しています。"
            
            response = "商品比較結果をご紹介します。\n\n"
            
            # 価格比較
            price_comp = comparison_data.get("price_comparison", {})
            if price_comp:
                response += "【価格比較】\n"
                response += f"最安値: {format_price(price_comp.get('min_price', 0))}\n"
                response += f"最高値: {format_price(price_comp.get('max_price', 0))}\n"
                response += f"平均価格: {format_price(price_comp.get('average_price', 0))}\n\n"
            
            # 評価比較
            rating_comp = comparison_data.get("rating_comparison", {})
            if rating_comp:
                response += "【評価比較】\n"
                response += f"最高評価: {rating_comp.get('highest_rating', 0)}/5.0\n"
                response += f"最低評価: {rating_comp.get('lowest_rating', 0)}/5.0\n"
                response += f"平均評価: {rating_comp.get('average_rating', 0):.1f}/5.0\n\n"
            
            # 機能比較
            feature_comp = comparison_data.get("feature_comparison", {})
            if feature_comp:
                response += "【機能比較】\n"
                for feature, availability in feature_comp.items():
                    available_count = sum(availability)
                    response += f"{feature}: {available_count}/{len(products)}商品に搭載\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating comparison response: {e}")
            return "商品比較の生成中にエラーが発生しました。"
    
    async def generate_summary_response(self, session_data: Dict[str, Any]) -> str:
        """
        セッション要約のレスポンスを生成
        
        Args:
            session_data: セッションデータ
            
        Returns:
            str: 要約レスポンス
        """
        try:
            conversation_history = session_data.get("conversation_history", [])
            user_preferences = session_data.get("user_preferences", {})
            favorites = session_data.get("favorites", [])
            
            response = "セッション要約をご紹介します。\n\n"
            
            # 会話履歴の要約
            user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
            if user_messages:
                response += f"会話回数: {len(user_messages)}回\n"
                
                # 最近のメッセージを抽出
                recent_messages = user_messages[-3:]
                response += "最近の検索:\n"
                for msg in recent_messages:
                    content = msg.get("content", "")
                    if content:
                        response += f"・{truncate_text(content, 50)}\n"
                response += "\n"
            
            # ユーザー希望の要約
            if user_preferences:
                response += "設定された希望:\n"
                if user_preferences.get("price_range"):
                    response += f"・価格: {user_preferences['price_range']}\n"
                if user_preferences.get("brands"):
                    brands = ", ".join(user_preferences["brands"])
                    response += f"・ブランド: {brands}\n"
                if user_preferences.get("categories"):
                    categories = ", ".join(user_preferences["categories"])
                    response += f"・カテゴリ: {categories}\n"
                response += "\n"
            
            # お気に入りの要約
            if favorites:
                response += f"お気に入り商品: {len(favorites)}件\n"
                for i, favorite in enumerate(favorites[:3], 1):
                    name = favorite.get("name", "商品")
                    price = format_price(favorite.get("price", 0))
                    response += f"{i}. {name} ({price})\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating summary response: {e}")
            return "セッション要約の生成中にエラーが発生しました。" 