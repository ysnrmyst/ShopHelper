# API仕様書

## 1. 楽天API

### 概要
- 楽天市場の商品検索API（Ichiba Item Search API）を利用し、商品情報を取得

### 認証
- アプリID（Application ID）が必要

### 主なエンドポイント
- `https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706`

### リクエスト例
```http
GET /services/api/IchibaItem/Search/20170706?applicationId=XXXXXX&keyword=日傘&hits=10
```

### レスポンス例（抜粋）
```json
{
  "Items": [
    {
      "Item": {
        "itemName": "晴雨兼用日傘 UVカット 軽量",
        "itemPrice": 2980,
        "itemUrl": "https://item.rakuten.co.jp/...",
        "shopName": "楽天ショップA",
        "mediumImageUrls": [ { "imageUrl": "..." } ]
      }
    }
  ]
}
```

### システム内インターフェース例
- fetch_rakuten_items(keyword: str, hits: int = 10) -> list[dict]

### 注意点
- 1日あたりのリクエスト数制限あり
- 商品画像は複数サイズあり

---

## 2. Amazon Product Advertising API

### 概要
- Amazonの商品情報・レビューを取得

### 認証
- アクセスキー、シークレットキー、アソシエイトタグが必要

### 主なエンドポイント
- `https://webservices.amazon.co.jp/paapi5/searchitems`

### リクエスト例
（POST、署名付きリクエストが必要）

### レスポンス例（抜粋）
```json
{
  "SearchResult": {
    "Items": [
      {
        "ASIN": "B000XXXXXX",
        "Title": "HDMIケーブル 2m",
        "DetailPageURL": "https://www.amazon.co.jp/dp/B000XXXXXX",
        "Images": { "Primary": { "Medium": { "URL": "..." } } },
        "Offers": { "Listings": [ { "Price": { "Amount": 980 } } ] }
      }
    ]
  }
}
```

### システム内インターフェース例
- fetch_amazon_items(keyword: str, count: int = 10) -> list[dict]

### 注意点
- 署名付きリクエストが必要で実装がやや複雑
- 利用には審査・制限あり

---

## 3. Google Custom Search API

### 概要
- Web全体や特定サイトから商品情報を検索

### 認証
- APIキー、検索エンジンID（cx）が必要

### 主なエンドポイント
- `https://www.googleapis.com/customsearch/v1`

### リクエスト例
```http
GET /customsearch/v1?key=XXXXXX&cx=YYYYYY&q=日傘
```

### レスポンス例（抜粋）
```json
{
  "items": [
    {
      "title": "晴雨兼用日傘 - 楽天市場",
      "link": "https://item.rakuten.co.jp/...",
      "snippet": "...",
      "pagemap": { "cse_image": [ { "src": "..." } ] }
    }
  ]
}
```

### システム内インターフェース例
- fetch_google_search_results(query: str, num: int = 10) -> list[dict]

### 注意点
- 1日あたりの無料リクエスト数制限あり
- 画像はpagemapから取得

---

## 4. Vertex AI（LLM/要約）

### 概要
- Google CloudのVertex AIでLLM（会話生成・要約）を利用

### 認証
- サービスアカウントキー、GCPプロジェクト設定

### 主なエンドポイント
- `https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:predict`

### リクエスト例（要約）
```json
{
  "instances": [ { "content": "口コミテキスト..." } ],
  "parameters": { "temperature": 0.2 }
}
```

### レスポンス例（抜粋）
```json
{
  "predictions": [ { "content": "良い点：安い。悪い点：ケーブルが固い。" } ]
}
```

### システム内インターフェース例
- summarize_text(text: str, prompt: str = None) -> str

### 注意点
- 利用料金が発生
- 入力長制限あり

---

## 5. 口コミサイト（kakaku.com等）

### 概要
- 商品名や型番から口コミページURLを生成し、リンクを表示
- 直接APIは提供されていないため、Web検索やURLパターンでリンク生成

### 例：kakaku.com
- URL例：`https://kakaku.com/item/{item_code}/review/`
- item_codeはGoogle検索や商品情報から推定

### システム内インターフェース例
- generate_review_link(product_name: str, site: str = "kakaku.com") -> str

### 注意点
- 口コミ本文の自動取得・要約はWebスクレイピングやAPI利用規約に注意
- 取得困難な場合はリンクのみ表示 

---

## 6. 送料・トータル金額に関する注意

- 楽天API・Amazon Product Advertising APIの標準レスポンスには、送料金額は原則含まれていません。
- 楽天APIでは「postageFlag」（送料無料フラグ）は取得可能ですが、具体的な送料金額は取得できません。
- Amazon APIでも「プライム対象」や「送料無料」などの判別は可能ですが、送料金額は取得できません。
- トータル金額（商品価格＋送料）は、送料が取得できる場合のみ表示し、取得できない場合は「送料は商品ページでご確認ください」等の注記を表示します。
- 送料無料商品のみを優先表示するなどの工夫も有効です。 

---

## 7. ショップ評価点・レビュー件数の取得について

### 楽天
- Shop API（https://app.rakuten.co.jp/services/api/Shop/ShopSearch/20170426）を利用することで、ショップの評価点（reviewAverage）やレビュー件数（reviewCount）が取得可能です。
- 商品API（Ichiba Item Search API）で取得したshopCodeを使い、Shop APIでショップ情報を取得します。
- 例：
```json
{
  "shopName": "楽天ショップA",
  "shopUrl": "https://www.rakuten.co.jp/xxxx/",
  "reviewAverage": 4.5,
  "reviewCount": 1234
}
```

### Amazon
- Product Advertising APIでは、出品者（ショップ）の評価点やレビュー件数は取得できません。
- ショップ評価が必要な場合は、Amazonサイト上での確認を案内してください。 

---

## 8. ユーザー入力の区切り文字仕様とAPIリクエストへの反映

- ユーザーが入力したキーワードや機能・特徴は、
  - 全角スペース（　）
  - 半角スペース（ ）
  - 全角カンマ（、）
  - 半角カンマ（,）
 で分割して抽出する。
- 分割したキーワードは、各APIの仕様に合わせて連結し、リクエストパラメータ（keyword, q など）に渡す。
  - 楽天API、Amazon API、Google Custom Search APIはいずれもスペース区切りでAND検索となるため、スペースで連結して渡す。
- 例：「UVカット 放熱,軽量、遮光」→ ["UVカット", "放熱", "軽量", "遮光"] → "UVカット 放熱 軽量 遮光"
- 必要に応じて、全角・半角の正規化やクォート付与も検討する。 