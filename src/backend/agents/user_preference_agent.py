"""
ユーザー希望エージェント
ユーザーの希望を抽出・管理
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from utils.helpers import sanitize_input, extract_keywords

logger = logging.getLogger(__name__)

class UserPreferenceAgent:
    """ユーザー希望エージェント"""
    
    def __init__(self):
        """初期化"""
        self.is_initialized = False
        
        # 価格関連のキーワード
        self.price_keywords = {
            "安い": "low",
            "安価": "low", 
            "高価": "high",
            "高い": "high",
            "格安": "very_low",
            "激安": "very_low",
            "高級": "very_high",
            "プレミアム": "very_high"
        }
        
        # 品質関連のキーワード
        self.quality_keywords = {
            "高品質": "high",
            "品質": "medium",
            "良質": "good",
            "上質": "high",
            "高評価": "high",
            "人気": "popular"
        }
        
        # ブランド関連のキーワード
        self.brand_keywords = {
            "ブランド": "brand",
            "メーカー": "manufacturer",
            "有名": "famous",
            "人気": "popular"
        }
        
        # カテゴリ関連のキーワード
        self.category_keywords = {
            "電化製品": "electronics",
            "家電": "electronics",
            "服": "clothing",
            "ファッション": "clothing",
            "本": "books",
            "書籍": "books",
            "食品": "food",
            "食べ物": "food",
            "化粧品": "cosmetics",
            "美容": "cosmetics",
            "スポーツ": "sports",
            "家具": "furniture",
            "玩具": "toys",
            "おもちゃ": "toys"
        }
    
    async def initialize(self) -> None:
        """エージェントの初期化"""
        try:
            logger.info("Initializing UserPreferenceAgent...")
            
            # 初期化処理（将来的にAIモデルの読み込みなど）
            await asyncio.sleep(0.1)  # 非同期処理のシミュレーション
            
            self.is_initialized = True
            logger.info("UserPreferenceAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UserPreferenceAgent: {e}")
            raise
    
    async def cleanup(self) -> None:
        """エージェントのクリーンアップ"""
        try:
            logger.info("Cleaning up UserPreferenceAgent...")
            self.is_initialized = False
            logger.info("UserPreferenceAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup UserPreferenceAgent: {e}")
    
    def is_ready(self) -> bool:
        """エージェントの準備状況を確認"""
        return self.is_initialized
    
    async def extract_preferences(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ユーザーの希望を抽出
        
        Args:
            message: ユーザーメッセージ
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: 抽出された希望
        """
        try:
            sanitized_message = sanitize_input(message)
            
            # 既存の希望を取得
            existing_preferences = session_data.get("user_preferences", {})
            
            # 新しい希望を抽出
            new_preferences = self._extract_preferences_from_message(sanitized_message)
            
            # 希望を統合
            merged_preferences = self._merge_preferences(existing_preferences, new_preferences)
            
            # セッションデータを更新
            session_data["user_preferences"] = merged_preferences
            
            return merged_preferences
            
        except Exception as e:
            logger.error(f"Error extracting preferences: {e}")
            return session_data.get("user_preferences", {})
    
    def _extract_preferences_from_message(self, message: str) -> Dict[str, Any]:
        """メッセージから希望を抽出"""
        preferences = {
            "price_range": None,
            "quality": None,
            "brands": [],
            "categories": [],
            "keywords": [],
            "features": [],
            "excluded_items": []
        }
        
        # キーワード抽出
        keywords = extract_keywords(message)
        preferences["keywords"] = keywords
        
        # 価格範囲の抽出
        price_pref = self._extract_price_preference(message)
        if price_pref:
            preferences["price_range"] = price_pref
        
        # 品質の抽出
        quality_pref = self._extract_quality_preference(message)
        if quality_pref:
            preferences["quality"] = quality_pref
        
        # ブランドの抽出
        brands = self._extract_brands(message)
        if brands:
            preferences["brands"] = brands
        
        # カテゴリの抽出
        categories = self._extract_categories(message)
        if categories:
            preferences["categories"] = categories
        
        # 機能の抽出
        features = self._extract_features(message)
        if features:
            preferences["features"] = features
        
        # 除外アイテムの抽出
        excluded = self._extract_excluded_items(message)
        if excluded:
            preferences["excluded_items"] = excluded
        
        return preferences
    
    def _extract_price_preference(self, message: str) -> Optional[str]:
        """価格希望を抽出"""
        message_lower = message.lower()
        
        for keyword, preference in self.price_keywords.items():
            if keyword in message_lower:
                return preference
        
        # 数値による価格範囲の抽出
        price_patterns = [
            (r"(\d+)円以下", "low"),
            (r"(\d+)万円以下", "low"),
            (r"(\d+)円以上", "high"),
            (r"(\d+)万円以上", "high"),
            (r"(\d+)円〜(\d+)円", "medium"),
            (r"(\d+)万円〜(\d+)万円", "medium")
        ]
        
        for pattern, preference in price_patterns:
            if re.search(pattern, message):
                return preference
        
        return None
    
    def _extract_quality_preference(self, message: str) -> Optional[str]:
        """品質希望を抽出"""
        message_lower = message.lower()
        
        for keyword, preference in self.quality_keywords.items():
            if keyword in message_lower:
                return preference
        
        return None
    
    def _extract_brands(self, message: str) -> List[str]:
        """ブランドを抽出"""
        brands = []
        message_lower = message.lower()
        
        # 一般的なブランド名
        common_brands = [
            "Apple", "Sony", "Panasonic", "Sharp", "Toshiba",
            "Nike", "Adidas", "Uniqlo", "Zara", "H&M",
            "Samsung", "LG", "Canon", "Nikon", "Fujifilm"
        ]
        
        for brand in common_brands:
            if brand.lower() in message_lower:
                brands.append(brand)
        
        return brands
    
    def _extract_categories(self, message: str) -> List[str]:
        """カテゴリを抽出"""
        categories = []
        message_lower = message.lower()
        
        for keyword, category in self.category_keywords.items():
            if keyword in message_lower:
                categories.append(category)
        
        return categories
    
    def _extract_features(self, message: str) -> List[str]:
        """機能を抽出"""
        features = []
        message_lower = message.lower()
        
        # 機能キーワード
        feature_keywords = {
            "無線": "wireless",
            "ワイヤレス": "wireless",
            "防水": "waterproof",
            "軽量": "lightweight",
            "コンパクト": "compact",
            "大容量": "large_capacity",
            "高速": "high_speed",
            "省エネ": "energy_saving",
            "スマート": "smart",
            "自動": "automatic"
        }
        
        for keyword, feature in feature_keywords.items():
            if keyword in message_lower:
                features.append(feature)
        
        return features
    
    def _extract_excluded_items(self, message: str) -> List[str]:
        """除外アイテムを抽出"""
        excluded = []
        message_lower = message.lower()
        
        # 除外を示すキーワード
        exclusion_keywords = ["除外", "除く", "ない", "不要", "いらない", "except", "without", "not"]
        
        # 除外キーワードが含まれている場合、その前後の単語を除外アイテムとして扱う
        for keyword in exclusion_keywords:
            if keyword in message_lower:
                # 簡易的な除外アイテム抽出
                words = message_lower.split()
                for i, word in enumerate(words):
                    if word == keyword and i > 0:
                        excluded.append(words[i-1])
        
        return excluded
    
    def _merge_preferences(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """希望を統合"""
        merged = existing.copy()
        
        # 新しい希望で既存の希望を更新
        for key, value in new.items():
            if value is not None and value != []:
                if key in ["brands", "categories", "features", "excluded_items"]:
                    # リストの場合は重複を除去して統合
                    existing_list = merged.get(key, [])
                    if isinstance(value, list):
                        merged[key] = list(set(existing_list + value))
                    else:
                        merged[key] = existing_list + [value]
                else:
                    # その他の場合は新しい値で上書き
                    merged[key] = value
        
        return merged
    
    async def get_user_preferences(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ユーザー希望を取得
        
        Args:
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: ユーザー希望
        """
        return session_data.get("user_preferences", {})
    
    async def update_preferences(self, preferences: Dict[str, Any], session_data: Dict[str, Any]) -> bool:
        """
        ユーザー希望を更新
        
        Args:
            preferences: 新しい希望
            session_data: セッションデータ
            
        Returns:
            bool: 更新成功時True
        """
        try:
            existing = session_data.get("user_preferences", {})
            merged = self._merge_preferences(existing, preferences)
            session_data["user_preferences"] = merged
            return True
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False
    
    async def clear_preferences(self, session_data: Dict[str, Any]) -> bool:
        """
        ユーザー希望をクリア
        
        Args:
            session_data: セッションデータ
            
        Returns:
            bool: クリア成功時True
        """
        try:
            session_data["user_preferences"] = {}
            return True
        except Exception as e:
            logger.error(f"Error clearing preferences: {e}")
            return False
    
    async def get_preference_summary(self, session_data: Dict[str, Any]) -> str:
        """
        ユーザー希望の要約を生成
        
        Args:
            session_data: セッションデータ
            
        Returns:
            str: 希望の要約
        """
        try:
            preferences = session_data.get("user_preferences", {})
            
            if not preferences:
                return "特に希望は設定されていません。"
            
            summary_parts = []
            
            # 価格範囲
            if preferences.get("price_range"):
                price_mapping = {
                    "very_low": "非常に安い",
                    "low": "安い",
                    "medium": "普通",
                    "high": "高い",
                    "very_high": "非常に高い"
                }
                price = price_mapping.get(preferences["price_range"], preferences["price_range"])
                summary_parts.append(f"価格: {price}")
            
            # 品質
            if preferences.get("quality"):
                quality_mapping = {
                    "high": "高品質",
                    "medium": "普通",
                    "good": "良質",
                    "popular": "人気"
                }
                quality = quality_mapping.get(preferences["quality"], preferences["quality"])
                summary_parts.append(f"品質: {quality}")
            
            # ブランド
            if preferences.get("brands"):
                brands = ", ".join(preferences["brands"])
                summary_parts.append(f"ブランド: {brands}")
            
            # カテゴリ
            if preferences.get("categories"):
                categories = ", ".join(preferences["categories"])
                summary_parts.append(f"カテゴリ: {categories}")
            
            # 機能
            if preferences.get("features"):
                features = ", ".join(preferences["features"])
                summary_parts.append(f"機能: {features}")
            
            if summary_parts:
                return "希望: " + ", ".join(summary_parts)
            else:
                return "特に希望は設定されていません。"
                
        except Exception as e:
            logger.error(f"Error generating preference summary: {e}")
            return "希望の要約を生成できませんでした。"
    
    async def suggest_preferences(self, message: str, session_data: Dict[str, Any]) -> List[str]:
        """
        希望のサジェストを生成
        
        Args:
            message: ユーザーメッセージ
            session_data: セッションデータ
            
        Returns:
            List[str]: サジェストリスト
        """
        suggestions = []
        
        # メッセージの内容に基づいてサジェストを生成
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["安い", "価格"]):
            suggestions.extend([
                "1万円以下の商品",
                "5千円以下の商品",
                "格安商品"
            ])
        
        if any(word in message_lower for word in ["高品質", "品質"]):
            suggestions.extend([
                "高評価の商品",
                "人気商品",
                "プレミアム商品"
            ])
        
        if any(word in message_lower for word in ["ブランド", "メーカー"]):
            suggestions.extend([
                "Apple製品",
                "Sony製品",
                "Nike製品"
            ])
        
        if any(word in message_lower for word in ["電化製品", "家電"]):
            suggestions.extend([
                "スマートフォン",
                "ノートPC",
                "テレビ"
            ])
        
        # デフォルトのサジェスト
        if not suggestions:
            suggestions = [
                "価格の安い商品",
                "高評価の商品",
                "人気商品"
            ]
        
        return suggestions[:3]  # 最大3個まで 