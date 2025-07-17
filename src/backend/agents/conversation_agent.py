"""
会話管理エージェント
メッセージの意図分析と会話フロー制御
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from utils.helpers import sanitize_input, extract_keywords, calculate_similarity

logger = logging.getLogger(__name__)

class ConversationAgent:
    """会話管理エージェント"""
    
    def __init__(self):
        """初期化"""
        self.is_initialized = False
        self.greeting_patterns = [
            r"こんにちは", r"はじめまして", r"おはよう", r"こんばんは",
            r"hello", r"hi", r"good morning", r"good evening"
        ]
        
        self.farewell_patterns = [
            r"さようなら", r"ありがとう", r"お疲れ様", r"失礼します",
            r"goodbye", r"bye", r"thank you", r"thanks"
        ]
        
        self.help_patterns = [
            r"ヘルプ", r"使い方", r"説明", r"サポート",
            r"help", r"how to", r"support"
        ]
        
        self.search_intent_patterns = [
            r"探したい", r"検索", r"見つけたい", r"買いたい",
            r"search", r"find", r"look for", r"buy"
        ]
        
        # 基本的な応答テンプレート
        self.response_templates = {
            "greeting": [
                "こんにちは！お買い物エージェントです。何かお探しの商品はありますか？",
                "はじめまして！買い物のお手伝いをさせていただきます。何かご質問はありますか？",
                "こんにちは！商品検索のお手伝いをいたします。何をお探しでしょうか？"
            ],
            "farewell": [
                "ありがとうございました。また何かございましたらお気軽にお声かけください。",
                "お疲れ様でした。またのご利用をお待ちしております。",
                "ご利用ありがとうございました。何かありましたらいつでもどうぞ。"
            ],
            "help": [
                "使い方についてご説明いたします。商品名やカテゴリを教えていただければ、最適な商品をご提案いたします。",
                "サポートいたします。商品検索、価格比較、お気に入り登録など、様々な機能をご利用いただけます。",
                "ご質問にお答えします。商品の詳細情報、レビュー、価格比較など、お買い物に役立つ情報をお届けします。"
            ],
            "search_intent": [
                "商品検索を開始いたします。より詳しい情報を教えていただけますか？",
                "検索いたします。価格帯やブランドなど、ご希望があればお聞かせください。",
                "商品をお探ししますね。どのような商品をお考えでしょうか？"
            ],
            "unknown": [
                "申し訳ございません。もう少し詳しく教えていただけますか？",
                "ご質問の内容を理解できませんでした。別の表現でお聞かせください。",
                "すみません、もう一度お聞かせいただけますでしょうか？"
            ]
        }
    
    async def initialize(self) -> None:
        """エージェントの初期化"""
        try:
            logger.info("Initializing ConversationAgent...")
            
            # 初期化処理（将来的にAIモデルの読み込みなど）
            await asyncio.sleep(0.1)  # 非同期処理のシミュレーション
            
            self.is_initialized = True
            logger.info("ConversationAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ConversationAgent: {e}")
            raise
    
    async def cleanup(self) -> None:
        """エージェントのクリーンアップ"""
        try:
            logger.info("Cleaning up ConversationAgent...")
            self.is_initialized = False
            logger.info("ConversationAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup ConversationAgent: {e}")
    
    def is_ready(self) -> bool:
        """エージェントの準備状況を確認"""
        return self.is_initialized
    
    async def analyze_intent(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        メッセージの意図を分析
        
        Args:
            message: ユーザーメッセージ
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: 意図分析結果
        """
        try:
            sanitized_message = sanitize_input(message)
            
            # 基本的な意図分析
            intent = {
                "requires_product_search": False,
                "intent_type": "unknown",
                "confidence": 0.0,
                "keywords": [],
                "entities": {}
            }
            
            # キーワード抽出
            keywords = extract_keywords(sanitized_message)
            intent["keywords"] = keywords
            
            # 挨拶の判定
            if self._is_greeting(sanitized_message):
                intent["intent_type"] = "greeting"
                intent["confidence"] = 0.9
                return intent
            
            # 別れの判定
            if self._is_farewell(sanitized_message):
                intent["intent_type"] = "farewell"
                intent["confidence"] = 0.9
                return intent
            
            # ヘルプの判定
            if self._is_help_request(sanitized_message):
                intent["intent_type"] = "help"
                intent["confidence"] = 0.8
                return intent
            
            # 商品検索意図の判定
            if self._is_search_intent(sanitized_message):
                intent["intent_type"] = "product_search"
                intent["requires_product_search"] = True
                intent["confidence"] = 0.7
                
                # 商品関連のエンティティを抽出
                entities = self._extract_product_entities(sanitized_message)
                intent["entities"] = entities
                
                return intent
            
            # 質問の判定
            if self._is_question(sanitized_message):
                intent["intent_type"] = "question"
                intent["confidence"] = 0.6
                return intent
            
            # デフォルトは商品検索として扱う
            intent["intent_type"] = "product_search"
            intent["requires_product_search"] = True
            intent["confidence"] = 0.5
            
            return intent
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {
                "requires_product_search": False,
                "intent_type": "unknown",
                "confidence": 0.0,
                "keywords": [],
                "entities": {}
            }
    
    async def generate_response(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        会話レスポンスを生成
        
        Args:
            message: ユーザーメッセージ
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: レスポンス
        """
        try:
            # 意図を分析
            intent = await self.analyze_intent(message, session_data)
            
            # 意図に基づいてレスポンスを生成
            response = self._generate_intent_response(intent, message, session_data)
            
            # サジェストを生成
            suggestions = self._generate_suggestions(intent, message, session_data)
            
            return {
                "message": response,
                "intent": intent,
                "suggestions": suggestions,
                "requires_action": intent.get("requires_product_search", False)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "message": "申し訳ございません。エラーが発生しました。",
                "intent": {"intent_type": "error"},
                "suggestions": [],
                "requires_action": False
            }
    
    def _is_greeting(self, message: str) -> bool:
        """挨拶かどうかを判定"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.greeting_patterns)
    
    def _is_farewell(self, message: str) -> bool:
        """別れかどうかを判定"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.farewell_patterns)
    
    def _is_help_request(self, message: str) -> bool:
        """ヘルプ要求かどうかを判定"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.help_patterns)
    
    def _is_search_intent(self, message: str) -> bool:
        """商品検索意図かどうかを判定"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.search_intent_patterns)
    
    def _is_question(self, message: str) -> bool:
        """質問かどうかを判定"""
        question_indicators = ["?", "？", "ですか", "でしょうか", "か", "what", "how", "why", "when", "where"]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in question_indicators)
    
    def _extract_product_entities(self, message: str) -> Dict[str, Any]:
        """商品関連のエンティティを抽出"""
        entities = {
            "product_name": None,
            "category": None,
            "price_range": None,
            "brand": None
        }
        
        # 価格範囲の抽出
        price_patterns = [
            r"(\d+)円", r"(\d+)万円", r"(\d+)千円",
            r"(\d+)yen", r"(\d+)万", r"(\d+)k"
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, message)
            if matches:
                entities["price_range"] = matches
                break
        
        # カテゴリの抽出
        categories = ["電化製品", "服", "本", "食品", "化粧品", "スポーツ", "家具", "玩具"]
        for category in categories:
            if category in message:
                entities["category"] = category
                break
        
        # ブランドの抽出
        brands = ["Apple", "Sony", "Panasonic", "Nike", "Adidas", "Uniqlo"]
        for brand in brands:
            if brand.lower() in message.lower():
                entities["brand"] = brand
                break
        
        return entities
    
    def _generate_intent_response(self, intent: Dict[str, Any], message: str, session_data: Dict[str, Any]) -> str:
        """意図に基づいてレスポンスを生成"""
        intent_type = intent.get("intent_type", "unknown")
        
        if intent_type == "greeting":
            return self._get_random_response("greeting")
        elif intent_type == "farewell":
            return self._get_random_response("farewell")
        elif intent_type == "help":
            return self._get_random_response("help")
        elif intent_type == "product_search":
            return self._get_random_response("search_intent")
        else:
            return self._get_random_response("unknown")
    
    def _get_random_response(self, response_type: str) -> str:
        """ランダムなレスポンスを取得"""
        import random
        templates = self.response_templates.get(response_type, self.response_templates["unknown"])
        return random.choice(templates)
    
    def _generate_suggestions(self, intent: Dict[str, Any], message: str, session_data: Dict[str, Any]) -> List[str]:
        """サジェストを生成"""
        suggestions = []
        
        intent_type = intent.get("intent_type", "unknown")
        
        if intent_type == "greeting":
            suggestions = [
                "商品を探したい",
                "おすすめ商品を教えて",
                "価格を比較したい"
            ]
        elif intent_type == "product_search":
            suggestions = [
                "価格の安い商品を探したい",
                "高評価の商品を教えて",
                "商品の詳細を教えて"
            ]
        elif intent_type == "help":
            suggestions = [
                "商品検索の使い方",
                "価格比較の方法",
                "お気に入り登録の方法"
            ]
        else:
            suggestions = [
                "商品を探したい",
                "おすすめ商品を教えて",
                "使い方を教えて"
            ]
        
        return suggestions[:3]  # 最大3個まで
    
    async def get_conversation_context(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        会話コンテキストを取得
        
        Args:
            session_data: セッションデータ
            
        Returns:
            Dict[str, Any]: 会話コンテキスト
        """
        try:
            conversation_history = session_data.get("conversation_history", [])
            user_preferences = session_data.get("user_preferences", {})
            
            # 最近の会話履歴を取得（最新10件）
            recent_history = conversation_history[-10:] if conversation_history else []
            
            # コンテキストを構築
            context = {
                "recent_messages": recent_history,
                "user_preferences": user_preferences,
                "conversation_length": len(conversation_history),
                "session_duration": self._calculate_session_duration(session_data)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {}
    
    def _calculate_session_duration(self, session_data: Dict[str, Any]) -> int:
        """セッション継続時間を計算（分）"""
        try:
            created_at = session_data.get("created_at")
            if not created_at:
                return 0
            
            created_dt = datetime.fromisoformat(created_at)
            current_dt = datetime.now()
            
            duration = current_dt - created_dt
            return int(duration.total_seconds() / 60)
            
        except Exception:
            return 0 