# テスト設計書

## 1. テストの種類・方針

### 1.1 ユニットテスト
- 各エージェント（ConversationAgent, UserPreferenceAgent, ProductSearchAgent, ResultAggregatorAgent）の個別機能テスト
- 各APIラッパー（RakutenApiClient, AmazonApiClient, GoogleSearchApiClient, VertexAiClient）の通信・データ整形テスト
- セッション管理（SessionManager）のデータ保持・初期化テスト

### 1.2 結合テスト
- エージェント間の連携テスト（会話管理エージェント → 他エージェント呼び出し）
- APIラッパーとエージェントの連携テスト
- セッション管理とエージェントの連携テスト

### 1.3 E2Eテスト（エンドツーエンドテスト）
- 主要ユーザーシナリオの全体フローテスト
- 会話開始 → 要件ヒアリング → 商品検索 → 結果表示 → お気に入り登録の一連の流れ

---

## 2. テストケース例

### 2.1 ConversationAgent テストケース
- 正常系：
  - ユーザー入力「日傘が欲しい」→ サジェスト「ご予算は？」「どんな機能が必要ですか？」「希望のブランドは？」
  - 会話リセット → 全データ初期化
  - 状態遷移（ヒアリング → 検索 → 提案）
- 異常系：
  - 空文字入力 → 適切なエラーメッセージ
  - 外部APIエラー → フォールバック処理

### 2.2 UserPreferenceAgent テストケース
- 正常系：
  - 「UVカット 放熱,軽量、遮光」→ ["UVカット", "放熱", "軽量", "遮光"]
  - 希望条件の更新・取得
- 異常系：
  - 不正な入力形式 → 適切な処理

### 2.3 ProductSearchAgent テストケース
- 正常系：
  - 楽天API呼び出し → 商品情報取得
  - Amazon API呼び出し → 商品情報取得
  - Google Custom Search API呼び出し → 検索結果取得
- 異常系：
  - APIタイムアウト → エラーハンドリング
  - 認証エラー → 適切なエラーメッセージ

### 2.4 APIラッパー テストケース
- 正常系：
  - 各APIの正常レスポンス処理
  - データ形式の変換・整形
- 異常系：
  - ネットワークエラー
  - API制限エラー
  - 不正なレスポンス形式

---

## 3. テスト環境・ツール

### 3.1 テスト実行環境
- Python unittest または pytest
- モックライブラリ（unittest.mock または pytest-mock）
- テストデータ管理（JSONファイルまたはテスト用クラス）

### 3.2 モックAPI
- 外部API（楽天、Amazon、Google、Vertex AI）のモック実装
- レスポンス例をJSONファイルで管理
- エラーケースも含めたモック

### 3.3 テストデータ
- 会話履歴サンプル
- 商品情報サンプル
- ユーザー希望条件サンプル
- お気に入りリストサンプル

---

## 4. テスト実行方針

### 4.1 自動化
- ユニットテスト・結合テストは自動実行
- CI/CDパイプラインへの組み込み
- テスト結果のレポート生成

### 4.2 テスト実行順序
1. ユニットテスト（各モジュール個別）
2. 結合テスト（モジュール間連携）
3. E2Eテスト（全体フロー）

### 4.3 テストカバレッジ
- コードカバレッジ80%以上を目標
- 主要機能・エラー処理のカバレッジを重視

---

## 5. テストファイル構成例

```
src/tests/
├── test_agents.py          # エージェントテスト
├── test_api.py            # APIラッパーテスト
├── test_session.py        # セッション管理テスト
├── test_integration.py    # 結合テスト
├── test_e2e.py           # E2Eテスト
├── mocks/                 # モックデータ
│   ├── rakuten_response.json
│   ├── amazon_response.json
│   └── ...
└── test_data/            # テストデータ
    ├── conversation_samples.json
    ├── product_samples.json
    └── ...
``` 