# お買い物エージェント 詳細設計書

## 1. 各エージェントの内部構造

### 1.1 会話管理エージェント（ConversationAgent）
- 主なクラス・関数
  - ConversationAgent: 対話の流れを制御
    - handle_user_input(text): ユーザー入力の処理
    - ask_next_question(): 次の質問生成
    - present_results(results): 検索結果の提示
    - call_sub_agents(): サブエージェント呼び出し
    - **reset_conversation()**: 会話セッションのリセット
    - **get_conversation_history()**: 会話履歴の取得
- 主要属性
  - session_id: セッション識別子
  - conversation_history: 会話履歴（発言者・テキスト・タイムスタンプ等を記録）

#### 会話リセット機能
- reset_conversation() で session_id, conversation_history, preferences などを初期化
- ユーザーが「やり直し」を希望した場合や、システム側で必要と判断した場合に呼び出し

#### 会話履歴の保持・表示機能
- conversation_history にユーザー発言・エージェント回答を逐次記録
- get_conversation_history() で履歴を取得し、チャットUIやデバッグ用に利用可能
- 各履歴は以下のような構造で保持：
```json
{
  "role": "user" | "agent",
  "text": "発話内容",
  "timestamp": "2024-06-01T10:00:00"
}
```

### 1.2 ユーザー希望管理エージェント（UserPreferenceAgent）
- 主なクラス・関数
  - UserPreferenceAgent: 希望条件の管理
    - extract_preferences(text): テキストから希望条件抽出
    - update_preferences(new): 希望条件の更新
    - get_preferences(): 現在の希望条件取得
- 主要属性
  - preferences: 希望条件（dict形式）

### 1.3 商品検索エージェント（ProductSearchAgent）
- 主なクラス・関数
  - ProductSearchAgent: 商品検索処理
    - search_products(preferences): 条件に合う商品を検索
    - fetch_from_api(site, params): 各サイトAPI/スクレイピング
- 主要属性
  - search_results: 検索結果リスト

### 1.4 検索結果集約エージェント（ResultAggregatorAgent）
- 主なクラス・関数
  - ResultAggregatorAgent: 結果集約・要約
    - aggregate_results(results_list): 複数サイトの結果統合
    - filter_by_preferences(results, preferences): 希望条件で絞り込み
    - summarize_results(results): 比較・要約生成
- 主要属性
  - aggregated_results: 集約済み商品リスト

---

## 2. データ構造

- preferences（希望条件例）:
```json
{
  "category": "日傘",
  "price_min": 2000,
  "price_max": 5000,
  "color": "白",
  "features": ["UVカット", "軽量"]
}
```

- product（商品情報例）:
```json
{
  "name": "晴雨兼用日傘 UVカット 軽量",
  "price": 2980,
  "url": "https://example.com/item/123",
  "image_url": "https://example.com/item/123.jpg",
  "features": ["UVカット", "軽量", "折りたたみ"],
  "shop": "楽天"
}
```

- aggregated_results（集約結果例）:
```json
[
  {"name": "...", "price": ..., ...},
  {"name": "...", "price": ..., ...}
]
```

---

## 3. エージェント間インターフェース

- 会話管理エージェント → ユーザー希望管理エージェント
  - 入力: ユーザー発話テキスト
  - 出力: 構造化希望条件（preferences）
- 会話管理エージェント → 商品検索エージェント
  - 入力: preferences
  - 出力: 商品情報リスト
- 商品検索エージェント → 検索結果集約エージェント
  - 入力: 複数サイトの商品情報リスト
  - 出力: 集約・絞り込み済み商品リスト
- 会話管理エージェント → ユーザー
  - 入力: 集約済み商品リスト
  - 出力: テキスト・リスト形式で提示

---

## 4. 例外処理・エラー時の挙動
- APIエラー時は「現在情報取得ができません」と通知
- 希望条件が曖昧・不足時は追加質問を生成
- 検索結果が0件の場合は再検索や条件緩和を提案

---

## 5. テスト方針
- 各エージェントのユニットテスト（正常系・異常系）
- エージェント間連携の結合テスト
- 主要なユーザーシナリオのE2Eテスト 

---

## 6. 各エージェントの主要メソッド入出力例

### 6.1 ConversationAgent
- handle_user_input(text: str) -> str
  - 入力例: "日傘が欲しい"
  - 出力例: "ご希望の色はありますか？"
- reset_conversation() -> None
- get_conversation_history() -> List[dict]
  - 出力例: [{"role": "user", "text": "日傘が欲しい", ...}, ...]

### 6.2 UserPreferenceAgent
- extract_preferences(text: str) -> dict
  - 入力例: "白い日傘でUVカットが欲しい"
  - 出力例: {"color": "白", "features": ["UVカット"]}
- update_preferences(new: dict) -> None
- get_preferences() -> dict

### 6.3 ProductSearchAgent
- search_products(preferences: dict) -> List[dict]
  - 入力例: {"color": "白", "features": ["UVカット"]}
  - 出力例: [{"name": "晴雨兼用日傘", "price": 2980, ...}, ...]
- fetch_from_api(site: str, params: dict) -> List[dict]

### 6.4 ResultAggregatorAgent
- aggregate_results(results_list: List[List[dict]]) -> List[dict]
- filter_by_preferences(results: List[dict], preferences: dict) -> List[dict]
- summarize_results(results: List[dict]) -> str

---

## 7. エージェント間やりとりのシーケンス例

1. ユーザー: 「日傘が欲しい」
2. ConversationAgent: UserPreferenceAgentに渡す
3. UserPreferenceAgent: {"category": "日傘"} を返す
4. ConversationAgent: 「ご希望の色はありますか？」
5. ユーザー: 「白がいい」
6. ConversationAgent: UserPreferenceAgentで更新
7. ConversationAgent: ProductSearchAgentに検索依頼
8. ProductSearchAgent: [{"name": ..., "color": "白", ...}, ...] を返す
9. ConversationAgent: ResultAggregatorAgentで集約
10. ResultAggregatorAgent: [{...}, {...}] を返す
11. ConversationAgent: ユーザーに提示

---

## 8. 主要なデータ構造スキーマ詳細

- conversation_history:
```json
[
  {"role": "user", "text": "日傘が欲しい", "timestamp": "..."},
  {"role": "agent", "text": "ご希望の色はありますか？", "timestamp": "..."}
]
```
- preferences:
```json
{
  "category": "日傘",
  "color": "白",
  "features": ["UVカット"],
  "price_min": 2000,
  "price_max": 5000
}
```
- product:
```json
{
  "name": "晴雨兼用日傘 UVカット 軽量",
  "price": 2980,
  "url": "https://example.com/item/123",
  "image_url": "https://example.com/item/123.jpg",
  "features": ["UVカット", "軽量", "折りたたみ"],
  "shop": "楽天"
}
```

---

## 9. エラーケース・例外処理の具体例
- APIタイムアウト時: 「現在情報取得ができません」
- 検索結果0件: 「条件を緩和して再検索しますか？」
- 入力が曖昧: 「もう少し詳しく教えてください」
- 外部APIの認証エラー: 管理者に通知、ユーザーには「一時的に利用できません」

---

## 10. テストケース例
- ユーザーが希望条件を順に入力し、正しく商品が提案される
- 会話リセット後、履歴が初期化される
- APIエラー時に適切なメッセージが返る
- 検索結果が0件のとき再検索提案が表示される 

---

## 11. 品番・品名入力時の画像確認フロー

### 概要
- ユーザーが品番や品名（例：HDMIケーブルの型番）を入力した場合、最初の検索結果から代表的な画像を提示し、「この画像の商品でよろしいですか？」とユーザーに確認します。
- ユーザーが「はい」と答えた場合、その商品情報（型番・特徴）で以降の検索・提案を限定します。
- 「いいえ」の場合は、他の候補画像を提示するか、再度入力を促します。

### 会話管理エージェントの拡張
- handle_user_input(text) で品番・品名を検知した場合、search_productsで得た最初の画像をpresent_image_for_confirmation(image_url)で提示
- ユーザーの「はい」/「いいえ」応答をhandle_image_confirmation(response)で処理
- preferencesに「confirmed_product_id」や「confirmed_image_url」などを追加し、以降の検索条件に反映

### データ構造の拡張例
```json
{
  "confirmed_product_id": "HDMI-1234",
  "confirmed_image_url": "https://example.com/item/hdmi-1234.jpg"
}
```

### シーケンス例
1. ユーザー: 「HDMI-1234が欲しい」
2. ConversationAgent: ProductSearchAgentで検索、最初の画像を提示
3. ConversationAgent: 「この画像の商品でよろしいですか？」
4. ユーザー: 「はい」
5. ConversationAgent: preferencesにconfirmed_product_id/confirmed_image_urlを記録
6. 以降の検索・提案はこの商品情報を優先

--- 

## 12. お気に入り登録・一覧・店舗比較機能

### 概要
- 検索結果や提案商品ごとに「お気に入り」ボタンを表示し、ユーザーが気になる商品をお気に入りリストに追加できる。
- お気に入りリストはセッション内で保持し、会話の最後やユーザーのリクエストで一覧表示できる。
- お気に入り内で同じ商品（型番や特徴が一致）を複数店舗から比較できる。

### 会話管理エージェントの拡張
- add_favorite(product: dict) でお気に入り追加
- get_favorites() でお気に入り一覧取得
- compare_favorites(product_id: str) で同一商品の店舗比較
- favorites属性でお気に入りリストを管理

### データ構造例
```json
"favorites": [
  {
    "product_id": "HDMI-1234",
    "name": "HDMIケーブル 2m",
    "image_url": "...",
    "price": 980,
    "shop": "楽天",
    "url": "..."
  }
]
```

### シーケンス例
1. ユーザー: 「この商品をお気に入りに追加」
2. ConversationAgent: add_favoriteでリストに追加
3. ユーザー: 「お気に入り一覧を見せて」
4. ConversationAgent: get_favoritesで一覧表示
5. ユーザー: 「この商品で店舗比較したい」
6. ConversationAgent: compare_favoritesで同一商品の店舗ごとの価格・送料を比較

--- 

## 13. 店舗比較画面での商品＋店舗単位のお気に入り登録

### 概要
- 店舗比較画面で、各店舗ごとに「この店舗をお気に入りに追加」ボタンを表示
- ユーザーが選択した店舗の商品が「商品＋店舗」単位でお気に入りリストに追加される
- お気に入り一覧画面では「商品＋店舗」の組み合わせで表示

### お気に入りデータ構造の拡張
```json
"favorites": [
  {
    "product_id": "HDMI-1234",
    "name": "HDMIケーブル 2m",
    "shop": "店舗AA",
    "price": 980,
    "url": "...",
    "image_url": "..."
  },
  {
    "product_id": "USB-5678",
    "name": "USBケーブル 1m",
    "shop": "店舗BB",
    "price": 500,
    "url": "...",
    "image_url": "..."
  }
]
```

### 会話管理エージェントの拡張
- add_favorite(product: dict, shop: str) で「商品＋店舗」単位でお気に入り登録
- get_favorites() で「商品＋店舗」ごとに一覧取得

### シーケンス例
1. ユーザー: 店舗比較画面で「この店舗をお気に入りに追加」
2. ConversationAgent: add_favorite(product, shop) でリストに追加
3. ユーザー: お気に入り一覧で「商品＋店舗」ごとに確認

--- 

## 14. 口コミ（レビュー）検索・要約機能

### 概要
- 商品詳細や検索結果画面で、kakaku.comやAmazonなど主要な口コミ・レビューサイトへのリンクを表示
- 商品名や型番をもとに、該当商品の口コミページURLを自動生成
- 口コミサイトからレビュー情報を取得し、Vertex AI等で要約して「良い点・悪い点」などを簡潔に提示
- 取得・要約が難しい場合は「口コミを読む」リンクのみ表示

### 会話管理エージェント・商品検索エージェントの拡張
- get_review_links(product) で口コミサイトへのリンクを取得
- summarize_reviews(product) で口コミ要約を取得
- 商品情報に review_links, review_summary を付与

### データ構造例
```json
{
  "review_links": [
    {"site": "kakaku.com", "url": "https://kakaku.com/item/HDMI-1234/review/"},
    {"site": "Amazon", "url": "https://www.amazon.co.jp/dp/B000XXXXXX#customerReviews"}
  ],
  "review_summary": "良い点：安い、画質が良い。悪い点：ケーブルが固い。"
}
```

### シーケンス例
1. 商品検索・詳細表示時にget_review_links, summarize_reviewsを呼び出し
2. 商品情報に口コミリンク・要約を付与
3. ユーザーが「口コミを見る」「口コミ要約」ボタンをクリック
4. 口コミサイトへ遷移、または要約をポップアップ等で表示

--- 

## 15. チャット画面の「想定される次の質問」サジェスト機能

### 概要
- チャット画面では、ユーザーが次に入力しやすい質問や選択肢をサジェストボタンとして最大3つ表示する。
- サジェスト内容は固定ではなく、会話履歴やユーザーの入力内容、現在の会話コンテキストに応じて動的に生成する。
- 例：色の希望を聞いた後は「ご予算は？」「どんな機能が必要ですか？」など、状況に応じた質問を提示。

### 実装イメージ
- 会話管理エージェントが次に想定される質問候補を推論し、UIに渡す
- サジェストボタンをクリックすると、その内容がユーザー発言として入力欄に反映される

### メソッド例
- get_next_suggestions(conversation_history: list) -> list[str]
  - 入力：現在の会話履歴
  - 出力：次に想定される質問候補（最大3件）

--- 

## 16. 会話制御・サジェスト生成ロジックの詳細

### 16.1 会話管理エージェントの状態遷移・フロー制御
- 会話は以下の主要な状態で管理される：
  1. 会話開始（初期挨拶・商品カテゴリ入力）
  2. 要件ヒアリング（色・価格・機能・ブランド等の条件収集）
  3. 商品検索・提案
  4. 画像確認（品番・品名入力時）
  5. 口コミ要約・リンク提示
  6. お気に入り登録・一覧
  7. 店舗比較
  8. 会話終了・リセット
- 各状態でのユーザー入力やシステム応答により、次の状態へ遷移
- 状態遷移は状態変数（current_state）で管理

#### 状態遷移図（テキスト）
- 開始 → ヒアリング → 検索・提案 → [画像確認] → [口コミ要約] → [お気に入り/比較] → 終了
- 途中で「リセット」や「お気に入り一覧」などの分岐も可能

### 16.2 サジェスト生成ロジック（修正版）
- サジェストは常に最大3つを提示する。
- 「予算」「機能」の2つはルールベースで優先的にサジェストする。
- ルールベースの質問（予算・機能）が未入力の場合は、それぞれをサジェストに含める。
- 残り1つ（またはルールベースがすべて埋まった場合の3つ）は、AI（LLM）が会話文脈から適切な質問を生成して補う。
- すべて埋まった場合は、AIが3つのサジェストを生成する。

#### サジェスト生成メソッド例（修正版）
- get_next_suggestions(conversation_history: list, current_state: str) -> list[str]
  - 予算・機能が未入力ならそれぞれサジェストに含める
  - 残りはAIで補完し、常に3つを維持

### 16.3 主要メソッド・データ構造例
- current_state: str（会話状態）
- conversation_history: list（履歴）
- handle_user_input(text: str) -> str
- transition_state(new_state: str) -> None
- get_next_suggestions(...) -> list[str]

### 16.4 会話制御シーケンス例
1. ユーザー「日傘が欲しい」→ 状態:ヒアリング
2. サジェスト「ご希望の色は？」「ご予算は？」「どんな機能が必要ですか？」
3. ユーザー「白」→ 状態:ヒアリング
4. サジェスト「ご予算は？」「どんな機能が必要ですか？」...
5. 条件が揃う→ 状態:検索・提案
6. 商品提案→ 状態:画像確認 or 口コミ要約 or お気に入り登録

--- 

## 17. データ管理・セッション管理

### 17.1 セッションの定義と管理方法
- 各ユーザーごとに一意のセッションID（session_id）を発行・管理
- セッションIDはランダム生成またはUUIDを利用
- セッションの有効期間は一定時間（例：30分）またはユーザーが明示的にリセットした時点で終了

### 17.2 セッションごとに保持するデータ
- conversation_history: 会話履歴（発言者・テキスト・タイムスタンプ等）
- preferences: ユーザー希望条件（色・価格・機能など）
- favorites: お気に入りリスト（商品＋店舗単位）
- selected_product/shop: 現在選択中の商品・店舗情報
- current_state: 現在の会話状態

### 17.3 データ構造例
```json
{
  "session_id": "abc123-...",
  "conversation_history": [
    {"role": "user", "text": "日傘が欲しい", "timestamp": "..."},
    {"role": "agent", "text": "ご予算は？", "timestamp": "..."}
  ],
  "preferences": {
    "price_min": 2000,
    "price_max": 5000,
    "features": ["UVカット"]
  },
  "favorites": [
    {"product_id": "HDMI-1234", "name": "HDMIケーブル 2m", "shop": "店舗AA", "price": 980, "url": "..."}
  ],
  "selected_product": {"product_id": "HDMI-1234", "name": "HDMIケーブル 2m"},
  "current_state": "hearing"
}
```

### 17.4 データの保存場所・ライフサイクル
- サーバー側のメモリまたは一時ストレージで管理（個人利用・DB不要の場合）
- セッションIDはクッキーやURLパラメータで管理可能
- セッション終了時（タイムアウト・リセット）にデータは破棄

### 17.5 セッション切れ・リセット時の挙動
- セッション有効期限切れやユーザーによるリセット時は、全データを初期化
- 新たなセッションIDを発行し、会話を最初から開始

--- 

## 18. 各エージェント・APIラッパーのクラス設計（インターフェース詳細）

### 18.1 エージェントクラス設計

#### ConversationAgent
- 役割：会話全体の制御、状態遷移、サジェスト生成、他エージェント呼び出し
- 主なメソッド：
  - handle_user_input(text: str) -> str
  - get_next_suggestions() -> list[str]
  - transition_state(new_state: str) -> None
  - reset_conversation() -> None
  - get_conversation_history() -> list[dict]
- 属性例：
  - current_state: str
  - conversation_history: list
  - preferences: dict
  - favorites: list

#### UserPreferenceAgent
- 役割：ユーザー希望条件の抽出・管理
- 主なメソッド：
  - extract_preferences(text: str) -> dict
  - update_preferences(new: dict) -> None
  - get_preferences() -> dict
- 属性例：
  - preferences: dict

#### ProductSearchAgent
- 役割：商品検索、APIラッパー呼び出し
- 主なメソッド：
  - search_products(preferences: dict) -> list[dict]
  - fetch_from_api(site: str, params: dict) -> list[dict]
- 属性例：
  - search_results: list

#### ResultAggregatorAgent
- 役割：検索結果の集約・絞り込み・要約
- 主なメソッド：
  - aggregate_results(results_list: list) -> list[dict]
  - filter_by_preferences(results: list, preferences: dict) -> list[dict]
  - summarize_results(results: list) -> str
- 属性例：
  - aggregated_results: list

---

### 18.2 APIラッパークラス設計

#### RakutenApiClient
- fetch_items(keyword: str, hits: int = 10) -> list[dict]
- fetch_shop_info(shop_code: str) -> dict

#### AmazonApiClient
- fetch_items(keyword: str, count: int = 10) -> list[dict]

#### GoogleSearchApiClient
- search(query: str, num: int = 10) -> list[dict]

#### VertexAiClient
- summarize_text(text: str, prompt: str = None) -> str
- generate_suggestions(context: str) -> list[str]

#### ReviewLinkGenerator
- generate(product_name: str, site: str = "kakaku.com") -> str

---

### 18.3 責任範囲まとめ
- 各エージェントは会話・希望管理・検索・集約の役割を分担
- APIラッパーは外部サービスとの通信・データ整形のみを担当
- セッション管理やデータ保持はSessionManager等の専用クラスで分離

--- 

### 18.4 ユーザー入力の区切り文字仕様（機能・キーワード抽出）
- UserPreferenceAgentのextract_preferencesメソッドでは、機能やキーワードの区切りとして以下の4種類を認識する：
  - 全角スペース（　）
  - 半角スペース（ ）
  - 全角カンマ（、）
  - 半角カンマ（,）
- 例：「UVカット 放熱,軽量、遮光」→ ["UVカット", "放熱", "軽量", "遮光"]
- 正規表現等で分割処理を実装する

--- 