"""
共通ユーティリティ関数
ログ設定、バリデーション、ヘルパー関数など
"""

import logging
import re
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import hashlib

def setup_logging(level: str = "INFO") -> None:
    """
    ログ設定を初期化
    
    Args:
        level: ログレベル
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )

def validate_session_id(session_id: str) -> bool:
    """
    セッションIDの妥当性をチェック
    
    Args:
        session_id: セッションID
        
    Returns:
        bool: 妥当な場合True
    """
    if not session_id:
        return False
    
    # UUID形式のチェック
    try:
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False

def validate_product_data(product_data: Dict[str, Any]) -> bool:
    """
    商品データの妥当性をチェック
    
    Args:
        product_data: 商品データ
        
    Returns:
        bool: 妥当な場合True
    """
    required_fields = ["id", "name", "price"]
    
    for field in required_fields:
        if field not in product_data:
            return False
    
    # 価格が数値であることを確認
    try:
        price = float(product_data["price"])
        if price < 0:
            return False
    except (ValueError, TypeError):
        return False
    
    return True

def sanitize_input(text: str) -> str:
    """
    入力テキストをサニタイズ
    
    Args:
        text: 入力テキスト
        
    Returns:
        str: サニタイズされたテキスト
    """
    if not text:
        return ""
    
    # HTMLタグを除去
    text = re.sub(r'<[^>]+>', '', text)
    
    # 特殊文字をエスケープ
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    # 改行を統一
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text.strip()

def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    テキストを指定された長さで切り詰める
    
    Args:
        text: 元のテキスト
        max_length: 最大長
        
    Returns:
        str: 切り詰められたテキスト
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def generate_product_id() -> str:
    """
    商品IDを生成
    
    Returns:
        str: 商品ID
    """
    return str(uuid.uuid4())

def calculate_price_range(min_price: Optional[float], max_price: Optional[float]) -> Dict[str, float]:
    """
    価格範囲を計算
    
    Args:
        min_price: 最小価格
        max_price: 最大価格
        
    Returns:
        Dict[str, float]: 価格範囲
    """
    if min_price is None:
        min_price = 0.0
    
    if max_price is None:
        max_price = float('inf')
    
    return {
        "min": min_price,
        "max": max_price
    }

def format_price(price: float, currency: str = "JPY") -> str:
    """
    価格をフォーマット
    
    Args:
        price: 価格
        currency: 通貨
        
    Returns:
        str: フォーマットされた価格
    """
    if currency == "JPY":
        return f"¥{price:,.0f}"
    else:
        return f"{price:.2f}"

def extract_keywords(text: str) -> List[str]:
    """
    テキストからキーワードを抽出
    
    Args:
        text: テキスト
        
    Returns:
        List[str]: キーワードリスト
    """
    if not text:
        return []
    
    # 基本的なキーワード抽出（後でより高度な処理に置き換え）
    words = re.findall(r'\b\w+\b', text.lower())
    
    # ストップワードを除去
    stop_words = {
        'の', 'に', 'は', 'を', 'が', 'で', 'と', 'に', 'から', 'まで',
        'です', 'ます', 'です', 'ください', 'お願い', 'ありがとう',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 1]
    
    return list(set(keywords))

def calculate_similarity(text1: str, text2: str) -> float:
    """
    2つのテキストの類似度を計算（簡易版）
    
    Args:
        text1: テキスト1
        text2: テキスト2
        
    Returns:
        float: 類似度（0.0-1.0）
    """
    if not text1 or not text2:
        return 0.0
    
    # キーワードを抽出
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Jaccard類似度を計算
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1.union(keywords2))
    
    return intersection / union if union > 0 else 0.0

def create_error_response(message: str, error_code: str = None) -> Dict[str, Any]:
    """
    エラーレスポンスを作成
    
    Args:
        message: エラーメッセージ
        error_code: エラーコード
        
    Returns:
        Dict[str, Any]: エラーレスポンス
    """
    response = {
        "error": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return response

def create_success_response(data: Any, message: str = None) -> Dict[str, Any]:
    """
    成功レスポンスを作成
    
    Args:
        data: レスポンスデータ
        message: メッセージ
        
    Returns:
        Dict[str, Any]: 成功レスポンス
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    if message:
        response["message"] = message
    
    return response

def merge_product_data(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    商品データを統合・重複除去
    
    Args:
        products: 商品データリスト
        
    Returns:
        List[Dict[str, Any]]: 統合された商品データ
    """
    if not products:
        return []
    
    # IDでグループ化
    product_groups = {}
    
    for product in products:
        product_id = product.get("id")
        if not product_id:
            continue
        
        if product_id not in product_groups:
            product_groups[product_id] = product
        else:
            # 既存の商品と統合
            existing = product_groups[product_id]
            
            # より詳細な情報を優先
            for key, value in product.items():
                if key not in existing or (existing[key] is None and value is not None):
                    existing[key] = value
            
            # ストア情報を統合
            if "stores" not in existing:
                existing["stores"] = []
            
            if "store" in product:
                store_info = product["store"]
                if not any(s.get("name") == store_info.get("name") for s in existing["stores"]):
                    existing["stores"].append(store_info)
    
    return list(product_groups.values())

def sort_products_by_relevance(products: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    商品を関連度順にソート
    
    Args:
        products: 商品リスト
        query: 検索クエリ
        
    Returns:
        List[Dict[str, Any]]: ソートされた商品リスト
    """
    if not products or not query:
        return products
    
    # 各商品の関連度スコアを計算
    scored_products = []
    
    for product in products:
        score = 0.0
        
        # 商品名との類似度
        name = product.get("name", "")
        if name:
            score += calculate_similarity(query, name) * 0.4
        
        # 説明との類似度
        description = product.get("description", "")
        if description:
            score += calculate_similarity(query, description) * 0.3
        
        # カテゴリとの類似度
        category = product.get("category", "")
        if category:
            score += calculate_similarity(query, category) * 0.2
        
        # 評価スコア
        rating = product.get("rating", 0.0)
        score += rating * 0.1
        
        scored_products.append((product, score))
    
    # スコアでソート
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    return [product for product, score in scored_products]

def generate_suggestions(user_message: str, conversation_history: List[Dict[str, Any]]) -> List[str]:
    """
    ユーザーメッセージに基づいてサジェストを生成
    
    Args:
        user_message: ユーザーメッセージ
        conversation_history: 会話履歴
        
    Returns:
        List[str]: サジェストリスト
    """
    suggestions = []
    
    # 基本的なサジェスト
    basic_suggestions = [
        "価格の安い商品を探したい",
        "高評価の商品を教えて",
        "おすすめの商品は？",
        "商品の詳細を教えて",
        "他の店舗も見てみたい"
    ]
    
    # メッセージの内容に基づいてサジェストを選択
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["安い", "安価", "価格"]):
        suggestions.append("価格の安い商品を探したい")
    
    if any(word in message_lower for word in ["評価", "レビュー", "口コミ"]):
        suggestions.append("高評価の商品を教えて")
    
    if any(word in message_lower for word in ["おすすめ", "推奨"]):
        suggestions.append("おすすめの商品は？")
    
    if any(word in message_lower for word in ["詳細", "詳しく", "説明"]):
        suggestions.append("商品の詳細を教えて")
    
    if any(word in message_lower for word in ["店舗", "店", "他の"]):
        suggestions.append("他の店舗も見てみたい")
    
    # 基本的なサジェストを追加
    for suggestion in basic_suggestions:
        if suggestion not in suggestions:
            suggestions.append(suggestion)
    
    return suggestions[:5]  # 最大5個まで

def validate_api_response(response_data: Dict[str, Any]) -> bool:
    """
    APIレスポンスの妥当性をチェック
    
    Args:
        response_data: APIレスポンスデータ
        
    Returns:
        bool: 妥当な場合True
    """
    if not isinstance(response_data, dict):
        return False
    
    # 必須フィールドのチェック
    required_fields = ["message"]
    
    for field in required_fields:
        if field not in response_data:
            return False
    
    return True

def create_mock_product_data() -> List[Dict[str, Any]]:
    """
    モック商品データを作成
    
    Returns:
        List[Dict[str, Any]]: モック商品データ
    """
    return [
        {
            "id": "mock_001",
            "name": "モック商品1",
            "price": 1000,
            "description": "これはモック商品です",
            "category": "テスト",
            "rating": 4.5,
            "store": "モックストア",
            "image_url": "https://via.placeholder.com/150"
        },
        {
            "id": "mock_002",
            "name": "モック商品2",
            "price": 2000,
            "description": "これもモック商品です",
            "category": "テスト",
            "rating": 4.0,
            "store": "モックストア",
            "image_url": "https://via.placeholder.com/150"
        }
    ] 