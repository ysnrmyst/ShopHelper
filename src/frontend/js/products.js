/**
 * 商品一覧画面
 */

class ProductsManager {
  constructor() {
    this.products = [];
    this.filteredProducts = [];
    this.currentPage = 1;
    this.productsPerPage = 12;
    this.currentFilters = {
      priceMin: '',
      priceMax: '',
      sort: 'relevance'
    };
    this.currentView = 'grid'; // 'grid' or 'list'
    
    // DOM要素
    this.productsGrid = utils.getElement('#productsGrid');
    this.pagination = utils.getElement('#pagination');
    this.priceMin = utils.getElement('#priceMin');
    this.priceMax = utils.getElement('#priceMax');
    this.sortFilter = utils.getElement('#sortFilter');
    this.applyFiltersBtn = utils.getElement('#applyFiltersBtn');
    this.clearFiltersBtn = utils.getElement('#clearFiltersBtn');
    this.resultsCount = utils.getElement('#resultsCount');
    this.gridViewBtn = utils.getElement('#gridViewBtn');
    this.listViewBtn = utils.getElement('#listViewBtn');
    this.backBtn = utils.getElement('#backBtn');
    this.favoritesBtn = utils.getElement('#favoritesBtn');
    this.loadingOverlay = utils.getElement('#loadingOverlay');
    this.productModal = utils.getElement('#productModal');
    this.closeProductModal = utils.getElement('#closeProductModal');
    this.addToFavoritesBtn = utils.getElement('#addToFavoritesBtn');
    this.closeModalBtn = utils.getElement('#closeModalBtn');
    
    // イベントリスナー
    this.bindEvents();
    
    // 初期化
    this.initialize();
  }
  
  bindEvents() {
    // フィルターボタン
    this.applyFiltersBtn.addEventListener('click', () => {
      this.applyFilters();
    });
    
    this.clearFiltersBtn.addEventListener('click', () => {
      this.clearFilters();
    });
    
    // 価格プリセットボタン
    document.querySelectorAll('.price-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const min = btn.dataset.min;
        const max = btn.dataset.max;
        this.setPriceRange(min, max);
      });
    });
    
    // ビュー切り替え
    this.gridViewBtn.addEventListener('click', () => {
      this.switchView('grid');
    });
    
    this.listViewBtn.addEventListener('click', () => {
      this.switchView('list');
    });
    
    // ナビゲーション
    this.backBtn.addEventListener('click', () => {
      window.location.href = '/';
    });
    
    this.favoritesBtn.addEventListener('click', () => {
      this.showFavorites();
    });
    
    // モーダル
    this.closeProductModal.addEventListener('click', () => {
      this.hideProductModal();
    });
    
    this.closeModalBtn.addEventListener('click', () => {
      this.hideProductModal();
    });
    
    this.addToFavoritesBtn.addEventListener('click', () => {
      this.addCurrentProductToFavorites();
    });
    
    // モーダル外クリックで閉じる
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.hideProductModal();
      }
    });
  }
  
  initialize() {
    this.loadDummyProducts();
    this.generatePricePresets(); // 動的価格プリセットを生成
    this.renderProducts();
    this.updatePagination();
    this.updateResultsCount();
    this.updateViewButtons();
    this.switchView('grid'); // 初期ビューをグリッドに設定
  }
  
  loadDummyProducts() {
    this.products = [
      {
        id: 'prod_001',
        title: '軽量折りたたみ日傘 白',
        price: 2980,
        store: '楽天市場',
        image: '/images/placeholder.svg',
        rating: 4.2,
        reviewCount: 156,
        category: 'umbrella',
        description: '軽量で持ち運びやすい折りたたみ日傘です。UVカット率99%で、白い色が清潔感を演出します。',
        features: ['UVカット率99%', '軽量設計', '折りたたみ式', '白い色'],
        shipping: '送料無料',
        delivery: '2-3営業日'
      },
      {
        id: 'prod_002',
        title: 'UVカット日傘 ブラック',
        price: 1580,
        store: 'Amazon',
        image: '/images/placeholder.svg',
        rating: 4.5,
        reviewCount: 89,
        category: 'umbrella',
        description: 'シンプルでスタイリッシュなブラックの日傘。UVカット機能付きで、おしゃれと実用性を両立。',
        features: ['UVカット機能', 'ブラックカラー', 'シンプルデザイン', '軽量'],
        shipping: '送料無料',
        delivery: '1-2営業日'
      },
      {
        id: 'prod_003',
        title: '高級日傘 レディース',
        price: 5980,
        store: 'Yahoo!ショッピング',
        image: '/images/placeholder.svg',
        rating: 4.8,
        reviewCount: 23,
        category: 'umbrella',
        description: '高級感のあるレディース向け日傘。上質な素材を使用し、エレガントなデザインが特徴です。',
        features: ['高級素材', 'エレガントデザイン', 'レディース向け', 'UVカット'],
        shipping: '送料500円',
        delivery: '3-5営業日'
      },
      {
        id: 'prod_004',
        title: 'ノートPC 15インチ',
        price: 89800,
        store: '楽天市場',
        image: '/images/placeholder.svg',
        rating: 4.3,
        reviewCount: 234,
        category: 'electronics',
        description: '高性能な15インチノートPC。仕事や学習に最適なスペックを搭載しています。',
        features: ['15インチディスプレイ', '高性能CPU', '大容量SSD', '軽量設計'],
        shipping: '送料無料',
        delivery: '1-2営業日'
      },
      {
        id: 'prod_005',
        title: 'ワイヤレスイヤホン',
        price: 12800,
        store: 'Amazon',
        image: '/images/placeholder.svg',
        rating: 4.6,
        reviewCount: 567,
        category: 'electronics',
        description: '高音質なワイヤレスイヤホン。ノイズキャンセリング機能付きで、音楽を存分に楽しめます。',
        features: ['ワイヤレス', 'ノイズキャンセリング', '高音質', '長時間バッテリー'],
        shipping: '送料無料',
        delivery: '1-2営業日'
      },
      {
        id: 'prod_006',
        title: 'デニムジャケット',
        price: 8900,
        store: 'Yahoo!ショッピング',
        image: '/images/placeholder.svg',
        rating: 4.1,
        reviewCount: 78,
        category: 'fashion',
        description: 'カジュアルでおしゃれなデニムジャケット。春から秋まで活躍するアイテムです。',
        features: ['デニム素材', 'カジュアルデザイン', '多色展開', '軽量'],
        shipping: '送料無料',
        delivery: '2-3営業日'
      }
    ];
    
    this.filteredProducts = [...this.products];
  }
  
  applyFilters() {
    // フィルター値を取得
    this.currentFilters.priceMin = this.priceMin.value;
    this.currentFilters.priceMax = this.priceMax.value;
    this.currentFilters.sort = this.sortFilter.value;
    
    let filtered = [...this.products];
    
    // 価格フィルター
    const minPrice = this.currentFilters.priceMin ? parseInt(this.currentFilters.priceMin) : null;
    const maxPrice = this.currentFilters.priceMax ? parseInt(this.currentFilters.priceMax) : null;
    
    if (minPrice !== null || maxPrice !== null) {
      filtered = filtered.filter(product => {
        const price = product.price;
        const minOk = minPrice === null || price >= minPrice;
        const maxOk = maxPrice === null || price <= maxPrice;
        return minOk && maxOk;
      });
    }
    
    // ソート
    switch (this.currentFilters.sort) {
      case 'price-low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case 'new':
        filtered.sort((a, b) => b.id.localeCompare(a.id));
        break;
      default:
        // 関連度順（デフォルト）
        break;
    }
    
    this.filteredProducts = filtered;
    this.currentPage = 1;
    this.renderProducts();
    this.updatePagination();
    this.updateResultsCount();
  }
  
  clearFilters() {
    this.priceMin.value = '';
    this.priceMax.value = '';
    this.sortFilter.value = 'relevance';
    this.currentFilters = { priceMin: '', priceMax: '', sort: 'relevance' };
    this.clearPricePresets();
    this.applyFilters();
  }
  
  switchView(view) {
    this.currentView = view;
    this.productsGrid.className = `products-grid ${view}-view`;
    this.updateViewButtons();
  }
  
  updateViewButtons() {
    this.gridViewBtn.classList.toggle('active', this.currentView === 'grid');
    this.listViewBtn.classList.toggle('active', this.currentView === 'list');
  }
  
  updateResultsCount() {
    this.resultsCount.textContent = `${this.filteredProducts.length}件の商品`;
  }
  
  // 価格範囲を設定
  setPriceRange(min, max) {
    this.priceMin.value = min || '';
    this.priceMax.value = max || '';
    this.updatePricePresets(min, max);
  }
  
  // 価格プリセットボタンの状態を更新
  updatePricePresets(selectedMin, selectedMax) {
    document.querySelectorAll('.price-preset-btn').forEach(btn => {
      const btnMin = btn.dataset.min;
      const btnMax = btn.dataset.max;
      const isActive = btnMin === selectedMin && btnMax === selectedMax;
      btn.classList.toggle('active', isActive);
    });
  }
  
  // 価格プリセットボタンをクリア
  clearPricePresets() {
    document.querySelectorAll('.price-preset-btn').forEach(btn => {
      btn.classList.remove('active');
    });
  }
  
  // 動的に価格プリセットを生成
  generatePricePresets() {
    const prices = this.products.map(p => p.price).sort((a, b) => a - b);
    if (prices.length === 0) return;
    
    const maxPrice = prices[prices.length - 1];
    
    // 商品の価格範囲に基づいてプリセットを調整
    const presets = [
      { min: 0, max: 1000, label: '1,000円以下' },
      { min: 1000, max: 3000, label: '1,000〜3,000円' },
      { min: 3000, max: 5000, label: '3,000〜5,000円' },
      { min: 5000, max: 10000, label: '5,000〜10,000円' }
    ];
    
    // 高価格商品がある場合のみ追加
    if (maxPrice > 10000) {
      presets.push({ min: 10000, max: '', label: '10,000円以上' });
    }
    
    const presetsContainer = document.querySelector('.price-presets');
    presetsContainer.innerHTML = '';
    
    presets.forEach(preset => {
      const btn = document.createElement('button');
      btn.className = 'price-preset-btn';
      btn.dataset.min = preset.min;
      btn.dataset.max = preset.max;
      btn.textContent = preset.label;
      btn.addEventListener('click', () => {
        this.setPriceRange(preset.min, preset.max);
      });
      presetsContainer.appendChild(btn);
    });
  }
  
  // チャットから商品を追加
  addProductFromChat(product) {
    // 商品IDが重複しないようにチェック
    const existingProduct = this.products.find(p => p.id === product.id);
    if (existingProduct) {
      return; // 既に存在する場合は追加しない
    }
    
    // 商品を追加
    this.products.push(product);
    
    // 表示を更新
    this.applyFilters();
  }
  
  renderProducts() {
    const startIndex = (this.currentPage - 1) * this.productsPerPage;
    const endIndex = startIndex + this.productsPerPage;
    const productsToShow = this.filteredProducts.slice(startIndex, endIndex);
    
    if (productsToShow.length === 0) {
      this.productsGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-state-icon">🔍</div>
          <div class="empty-state-title">商品が見つかりません</div>
          <div class="empty-state-text">フィルター条件を変更して、もう一度お試しください。</div>
        </div>
      `;
      return;
    }
    
    this.productsGrid.innerHTML = productsToShow.map(product => `
      <div class="product-card" data-product-id="${product.id}">
        <img src="${product.image}" alt="${product.title}" class="product-card-image" onerror="this.src='/images/placeholder.svg'">
        <div class="product-card-content">
          <div class="product-card-info">
            <div class="product-card-title">${product.title}</div>
            <div class="product-card-price">${utils.formatPrice(product.price)}</div>
            <div class="product-card-store">${product.store}</div>
            <div class="product-card-rating">
              <span class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</span>
              <span class="rating-text">${product.rating} (${product.reviewCount}件)</span>
            </div>
          </div>
          <div class="product-card-actions">
            <button class="btn btn-primary" onclick="productsManager.viewProduct('${product.id}')">詳細</button>
            <button class="btn btn-secondary favorite-btn" onclick="productsManager.toggleFavorite('${product.id}')">♡</button>
          </div>
        </div>
      </div>
    `).join('');
    
    // お気に入りボタンの状態を更新
    this.updateFavoriteButtons();
  }
  
  updatePagination() {
    const totalPages = Math.ceil(this.filteredProducts.length / this.productsPerPage);
    
    if (totalPages <= 1) {
      this.pagination.innerHTML = '';
      return;
    }
    
    let paginationHTML = '';
    
    // 前のページボタン
    paginationHTML += `
      <button class="pagination-btn" ${this.currentPage === 1 ? 'disabled' : ''} onclick="productsManager.goToPage(${this.currentPage - 1})">
        前へ
      </button>
    `;
    
    // ページ番号
    const startPage = Math.max(1, this.currentPage - 2);
    const endPage = Math.min(totalPages, this.currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
      paginationHTML += `
        <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" onclick="productsManager.goToPage(${i})">
          ${i}
        </button>
      `;
    }
    
    // 次のページボタン
    paginationHTML += `
      <button class="pagination-btn" ${this.currentPage === totalPages ? 'disabled' : ''} onclick="productsManager.goToPage(${this.currentPage + 1})">
        次へ
      </button>
    `;
    
    // ページ情報
    const startItem = (this.currentPage - 1) * this.productsPerPage + 1;
    const endItem = Math.min(this.currentPage * this.productsPerPage, this.filteredProducts.length);
    
    paginationHTML += `
      <div class="pagination-info">
        ${startItem}-${endItem} / ${this.filteredProducts.length}件
      </div>
    `;
    
    this.pagination.innerHTML = paginationHTML;
  }
  
  goToPage(page) {
    const totalPages = Math.ceil(this.filteredProducts.length / this.productsPerPage);
    if (page >= 1 && page <= totalPages) {
      this.currentPage = page;
      this.renderProducts();
      this.updatePagination();
      
      // ページトップにスクロール
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
  
  viewProduct(productId) {
    const product = this.products.find(p => p.id === productId);
    if (!product) {
      utils.logger.error('Product not found:', productId);
      return;
    }
    
    // モーダルタイトル
    const modalTitle = utils.getElement('#modalTitle');
    modalTitle.textContent = product.title;
    
    // モーダル内容
    const modalBody = utils.getElement('#modalBody');
    modalBody.innerHTML = `
      <div class="product-detail-modal">
        <div class="product-detail-modal-image">
          <img src="${product.image}" alt="${product.title}" onerror="this.src='/images/placeholder.svg'">
        </div>
        <div class="product-detail-modal-info">
          <div class="product-detail-modal-title">${product.title}</div>
          <div class="product-detail-modal-price">${utils.formatPrice(product.price)}</div>
          <div class="product-detail-modal-store">${product.store}</div>
          <div class="product-detail-modal-rating">
            <span class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</span>
            <span class="rating-text">${product.rating} (${product.reviewCount}件のレビュー)</span>
          </div>
          <div class="product-detail-modal-description">
            <h5>商品説明</h5>
            <p>${product.description}</p>
          </div>
          <div class="product-detail-modal-features">
            <h5>特徴</h5>
            <ul>
              ${product.features.map(feature => `<li>${feature}</li>`).join('')}
            </ul>
          </div>
          <div class="product-detail-modal-shipping">
            <div><strong>送料:</strong> ${product.shipping}</div>
            <div><strong>お届け:</strong> ${product.delivery}</div>
          </div>
        </div>
      </div>
    `;
    
    // 現在の商品IDを保存
    this.currentProductId = productId;
    
    // お気に入りボタンの状態を更新
    const favorites = utils.storage.get('favorites', []);
    const isFavorite = favorites.find(fav => fav.id === productId);
    this.addToFavoritesBtn.textContent = isFavorite ? 'お気に入りから削除' : 'お気に入りに追加';
    
    // モーダルを表示
    this.productModal.classList.add('show');
  }
  
  hideProductModal() {
    this.productModal.classList.remove('show');
    this.currentProductId = null;
  }
  
  toggleFavorite(productId) {
    const favorites = utils.storage.get('favorites', []);
    const product = this.products.find(p => p.id === productId);
    
    if (!product) return;
    
    const existingIndex = favorites.findIndex(fav => fav.id === productId);
    
    if (existingIndex >= 0) {
      favorites.splice(existingIndex, 1);
      utils.logger.info('Removed from favorites:', product.title);
    } else {
      favorites.push(product);
      utils.logger.info('Added to favorites:', product.title);
    }
    
    utils.storage.set('favorites', favorites);
    this.updateFavoriteButtons();
  }
  
  addCurrentProductToFavorites() {
    if (this.currentProductId) {
      this.toggleFavorite(this.currentProductId);
      
      // ボタンテキストを更新
      const favorites = utils.storage.get('favorites', []);
      const isFavorite = favorites.find(fav => fav.id === this.currentProductId);
      this.addToFavoritesBtn.textContent = isFavorite ? 'お気に入りから削除' : 'お気に入りに追加';
    }
  }
  
  updateFavoriteButtons() {
    const favorites = utils.storage.get('favorites', []);
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    favoriteButtons.forEach(button => {
      const productCard = button.closest('.product-card');
      if (productCard) {
        const productId = productCard.dataset.productId;
        if (favorites.find(fav => fav.id === productId)) {
          button.classList.add('active');
          button.innerHTML = '♥';
        } else {
          button.classList.remove('active');
          button.innerHTML = '♡';
        }
      }
    });
  }
  
  showFavorites() {
    const favorites = utils.storage.get('favorites', []);
    
    if (favorites.length === 0) {
      alert('お気に入りに登録された商品はありません。');
      return;
    }
    
    // お気に入り商品のみを表示
    this.filteredProducts = favorites;
    this.currentPage = 1;
    this.renderProducts();
    this.updatePagination();
    
    // フィルターをリセット
    this.categoryFilter.value = '';
    this.priceFilter.value = '';
    this.sortFilter.value = 'relevance';
    this.currentFilters = { category: '', price: '', sort: 'relevance' };
  }
  
  showLoading() {
    utils.showElement(this.loadingOverlay);
  }
  
  hideLoading() {
    utils.hideElement(this.loadingOverlay);
  }
}

// グローバルインスタンス
window.productsManager = new ProductsManager(); 