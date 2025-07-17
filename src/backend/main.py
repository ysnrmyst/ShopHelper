"""
お買い物エージェント - メインアプリケーション
FastAPI基盤とセッション管理
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Dict, Any, Optional
import logging
import os

from session.session_manager import SessionManager
from agents.conversation_agent import ConversationAgent
from agents.user_preference_agent import UserPreferenceAgent
from agents.product_search_agent import ProductSearchAgent
from agents.result_aggregator_agent import ResultAggregatorAgent
from utils.helpers import setup_logging, validate_session_id

# ログ設定
setup_logging()
logger = logging.getLogger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="お買い物エージェント",
    description="AIを活用した買い物支援システム",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信設定
app.mount("/css", StaticFiles(directory="../frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="../frontend/js"), name="js")
app.mount("/images", StaticFiles(directory="../frontend/images"), name="images")
app.mount("/products", StaticFiles(directory="../frontend"), name="products")

# セッション管理
session_manager = SessionManager()

# エージェント初期化
conversation_agent = ConversationAgent()
user_preference_agent = UserPreferenceAgent()
product_search_agent = ProductSearchAgent()
result_aggregator_agent = ResultAggregatorAgent()

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    logger.info("お買い物エージェントを起動中...")
    
    # エージェントの初期化
    await conversation_agent.initialize()
    await user_preference_agent.initialize()
    await product_search_agent.initialize()
    await result_aggregator_agent.initialize()
    
    logger.info("アプリケーションの初期化が完了しました")

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("アプリケーションを終了中...")
    
    # エージェントのクリーンアップ
    await conversation_agent.cleanup()
    await user_preference_agent.cleanup()
    await product_search_agent.cleanup()
    await result_aggregator_agent.cleanup()
    
    logger.info("アプリケーションの終了が完了しました")

# 依存関係
def get_session_manager() -> SessionManager:
    return session_manager

def get_conversation_agent() -> ConversationAgent:
    return conversation_agent

def get_user_preference_agent() -> UserPreferenceAgent:
    return user_preference_agent

def get_product_search_agent() -> ProductSearchAgent:
    return product_search_agent

def get_result_aggregator_agent() -> ResultAggregatorAgent:
    return result_aggregator_agent

# ヘルスチェック
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": {
            "conversation": conversation_agent.is_ready(),
            "user_preference": user_preference_agent.is_ready(),
            "product_search": product_search_agent.is_ready(),
            "result_aggregator": result_aggregator_agent.is_ready()
        }
    }

# セッション管理
@app.post("/api/session/create")
async def create_session():
    """新しいセッションを作成"""
    try:
        session_id = session_manager.create_session()
        logger.info(f"新しいセッションを作成: {session_id}")
        return {"session_id": session_id, "status": "created"}
    except Exception as e:
        logger.error(f"セッション作成エラー: {e}")
        raise HTTPException(status_code=500, detail="セッション作成に失敗しました")

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """セッション情報を取得"""
    try:
        if not validate_session_id(session_id):
            raise HTTPException(status_code=400, detail="無効なセッションID")
        
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        return {"session_id": session_id, "data": session_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"セッション取得エラー: {e}")
        raise HTTPException(status_code=500, detail="セッション取得に失敗しました")

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """セッションを削除"""
    try:
        if not validate_session_id(session_id):
            raise HTTPException(status_code=400, detail="無効なセッションID")
        
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        logger.info(f"セッションを削除: {session_id}")
        return {"session_id": session_id, "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"セッション削除エラー: {e}")
        raise HTTPException(status_code=500, detail="セッション削除に失敗しました")

# チャット機能
@app.post("/api/chat")
async def chat(
    request: Dict[str, Any],
    conv_agent: ConversationAgent = Depends(get_conversation_agent),
    pref_agent: UserPreferenceAgent = Depends(get_user_preference_agent),
    search_agent: ProductSearchAgent = Depends(get_product_search_agent),
    agg_agent: ResultAggregatorAgent = Depends(get_result_aggregator_agent)
):
    """チャットメッセージを処理"""
    try:
        user_message = request.get("message", "")
        session_id = request.get("sessionId", "")
        
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="メッセージが空です")
        
        if not session_id:
            # セッションIDがない場合は新規作成
            session_id = session_manager.create_session()
        
        # セッションデータを取得または作成
        session_data = session_manager.get_session(session_id)
        if not session_data:
            session_data = session_manager.create_session_data(session_id)
        
        # 会話履歴を更新
        session_data["conversation_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": session_manager.get_current_timestamp()
        })
        
        # エージェント連携でレスポンス生成
        response = await process_chat_message(
            user_message, session_data, conv_agent, pref_agent, search_agent, agg_agent
        )
        
        # レスポンスを履歴に追加
        session_data["conversation_history"].append({
            "role": "assistant",
            "content": response["message"],
            "timestamp": session_manager.get_current_timestamp()
        })
        
        # セッションを更新
        session_manager.update_session(session_id, session_data)
        
        # レスポンスにセッションIDを含める
        response["sessionId"] = session_id
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"チャット処理エラー: {e}")
        raise HTTPException(status_code=500, detail="メッセージ処理に失敗しました")

async def process_chat_message(
    user_message: str,
    session_data: Dict[str, Any],
    conv_agent: ConversationAgent,
    pref_agent: UserPreferenceAgent,
    search_agent: ProductSearchAgent,
    agg_agent: ResultAggregatorAgent
) -> Dict[str, Any]:
    """チャットメッセージを処理する内部関数"""
    
    # 1. 会話管理エージェントでメッセージの意図を分析
    intent = await conv_agent.analyze_intent(user_message, session_data)
    
    # 2. ユーザー希望エージェントでユーザーの希望を抽出
    preferences = await pref_agent.extract_preferences(user_message, session_data)
    
    # 3. 商品検索が必要な場合
    if intent.get("requires_product_search", False):
        search_results = await search_agent.search_products(preferences, session_data)
        
        # 4. 結果集約エージェントでレスポンスを生成
        response = await agg_agent.generate_response(
            user_message, search_results, preferences, session_data
        )
    else:
        # 商品検索が不要な場合（挨拶、質問など）
        response = await conv_agent.generate_response(user_message, session_data)
    
    return response

# 商品検索
@app.get("/api/products/search")
async def search_products(
    query: str,
    session_id: str = Depends(validate_session_id),
    search_agent: ProductSearchAgent = Depends(get_product_search_agent)
):
    """商品検索API"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="検索クエリが空です")
        
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        # 検索実行
        results = await search_agent.search_products({"query": query}, session_data)
        
        return {
            "query": query,
            "results": results.get("products", []),
            "total_count": len(results.get("products", [])),
            "search_time": results.get("search_time", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"商品検索エラー: {e}")
        raise HTTPException(status_code=500, detail="商品検索に失敗しました")

# お気に入り機能
@app.post("/api/favorites/add")
async def add_to_favorites(
    product_data: Dict[str, Any],
    session_id: str = Depends(validate_session_id)
):
    """お気に入りに商品を追加"""
    try:
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        # お気に入りリストに追加
        if "favorites" not in session_data:
            session_data["favorites"] = []
        
        # 重複チェック
        product_id = product_data.get("id")
        if not any(fav.get("id") == product_id for fav in session_data["favorites"]):
            session_data["favorites"].append(product_data)
            session_manager.update_session(session_id, session_data)
            logger.info(f"お気に入りに追加: {product_id}")
        
        return {"status": "added", "product_id": product_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"お気に入り追加エラー: {e}")
        raise HTTPException(status_code=500, detail="お気に入り追加に失敗しました")

@app.get("/api/favorites")
async def get_favorites(session_id: str = Depends(validate_session_id)):
    """お気に入りリストを取得"""
    try:
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        favorites = session_data.get("favorites", [])
        return {"favorites": favorites, "count": len(favorites)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"お気に入り取得エラー: {e}")
        raise HTTPException(status_code=500, detail="お気に入り取得に失敗しました")

@app.delete("/api/favorites/{product_id}")
async def remove_from_favorites(
    product_id: str,
    session_id: str = Depends(validate_session_id)
):
    """お気に入りから商品を削除"""
    try:
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        favorites = session_data.get("favorites", [])
        original_count = len(favorites)
        
        # 指定された商品を削除
        session_data["favorites"] = [fav for fav in favorites if fav.get("id") != product_id]
        
        if len(session_data["favorites"]) < original_count:
            session_manager.update_session(session_id, session_data)
            logger.info(f"お気に入りから削除: {product_id}")
            return {"status": "removed", "product_id": product_id}
        else:
            raise HTTPException(status_code=404, detail="商品が見つかりません")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"お気に入り削除エラー: {e}")
        raise HTTPException(status_code=500, detail="お気に入り削除に失敗しました")

# 静的ファイル配信
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """フロントエンドを配信"""
    try:
        # バックエンドディレクトリから見た相対パス
        with open("../frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="フロントエンドファイルが見つかりません")

@app.get("/products", response_class=HTMLResponse)
async def serve_products():
    """商品一覧ページを配信"""
    try:
        # バックエンドディレクトリから見た相対パス
        with open("../frontend/products.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="商品一覧ページが見つかりません")

# 開発用サーバー起動
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 