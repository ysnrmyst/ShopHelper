/**
 * UI関連の機能
 */

class UIManager {
  constructor() {
    this.modals = new Map();
    this.sidebarVisible = true;
    
    // DOM要素
    this.resetBtn = utils.getElement('#resetBtn');
    this.productsBtn = utils.getElement('#productsBtn');
    this.helpBtn = utils.getElement('#helpBtn');

    this.errorModal = utils.getElement('#errorModal');
    this.closeErrorModal = utils.getElement('#closeErrorModal');
    this.retryBtn = utils.getElement('#retryBtn');
    this.cancelBtn = utils.getElement('#cancelBtn');
    
    // イベントリスナー
    this.bindEvents();
    
    // 初期化
    this.initialize();
  }
  
  bindEvents() {
    // リセットボタン
    this.resetBtn.addEventListener('click', () => {
      this.showResetConfirm();
    });
    
    // 商品一覧ボタン
    this.productsBtn.addEventListener('click', () => {
      window.location.href = '/products';
    });
    
    // ヘルプボタン
    this.helpBtn.addEventListener('click', () => {
      this.showHelp();
    });
    
    // エラーモーダル
    this.closeErrorModal.addEventListener('click', () => {
      this.hideErrorModal();
    });
    
    this.retryBtn.addEventListener('click', () => {
      this.retryAction();
    });
    
    this.cancelBtn.addEventListener('click', () => {
      this.hideErrorModal();
    });
    
    // モーダル外クリックで閉じる
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.hideAllModals();
      }
    });
    
    // ESCキーでモーダルを閉じる
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.hideAllModals();
      }
    });
    
    // ウィンドウリサイズ時の処理
    window.addEventListener('resize', utils.debounce(() => {
      this.handleResize();
    }, 250));
  }
  
  initialize() {
    // お気に入りボタンの初期状態を更新
    this.updateFavoriteButtons();
    
    utils.logger.info('UI Manager initialized');
  }
  
  showResetConfirm() {
    const modal = this.createModal({
      title: 'リセット確認',
      content: `
        <p>チャット履歴とセッション情報がすべて削除されます。</p>
        <p>本当にリセットしますか？</p>
      `,
      buttons: [
        {
          text: 'リセット',
          className: 'btn-danger',
          action: () => {
            this.resetChat();
            this.hideModal('resetConfirm');
          }
        },
        {
          text: 'キャンセル',
          className: 'btn-secondary',
          action: () => {
            this.hideModal('resetConfirm');
          }
        }
      ]
    });
    
    this.showModal('resetConfirm', modal);
  }
  
  showHelp() {
    const modal = this.createModal({
      title: 'ヘルプ',
      content: `
        <h4>お買い物エージェントの使い方</h4>
        <ul>
          <li>商品名や希望条件を自然な言葉で入力してください</li>
          <li>例：「日傘が欲しい」「白い色で、3000円以下」</li>
          <li>サジェストボタンをクリックして素早く入力できます</li>
          <li>商品の詳細を見るには「詳細を見る」ボタンをクリック</li>
          <li>お気に入りに追加するには「♡」ボタンをクリック</li>
        </ul>
        
        <h4>ショートカット</h4>
        <ul>
          <li>Enter: メッセージ送信</li>
          <li>Shift + Enter: 改行</li>
          <li>ESC: モーダルを閉じる</li>
        </ul>
      `,
      buttons: [
        {
          text: '閉じる',
          className: 'btn-primary',
          action: () => {
            this.hideModal('help');
          }
        }
      ]
    });
    
    this.showModal('help', modal);
  }
  
  showErrorModal(message, retryAction = null) {
    const errorMessage = utils.getElement('#errorMessage');
    errorMessage.textContent = message;
    
    // リトライボタンの表示制御
    const retryBtn = utils.getElement('#retryBtn');
    if (retryAction) {
      utils.showElement(retryBtn);
      this.currentRetryAction = retryAction;
    } else {
      utils.hideElement(retryBtn);
    }
    
    this.errorModal.classList.add('show');
  }
  
  hideErrorModal() {
    this.errorModal.classList.remove('show');
    this.currentRetryAction = null;
  }
  
  retryAction() {
    if (this.currentRetryAction) {
      this.currentRetryAction();
    }
    this.hideErrorModal();
  }
  
  createModal(options) {
    const modal = utils.createElement('div', 'modal-overlay');
    
    const content = utils.createElement('div', 'modal-content');
    
    // ヘッダー
    const header = utils.createElement('div', 'modal-header');
    const title = utils.createElement('h3');
    title.textContent = options.title;
    header.appendChild(title);
    
    const closeBtn = utils.createElement('button', 'modal-close');
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', () => {
      this.hideModal(options.id);
    });
    header.appendChild(closeBtn);
    
    content.appendChild(header);
    
    // ボディ
    const body = utils.createElement('div', 'modal-body');
    body.innerHTML = options.content;
    content.appendChild(body);
    
    // フッター（ボタン）
    if (options.buttons && options.buttons.length > 0) {
      const footer = utils.createElement('div', 'modal-footer');
      
      options.buttons.forEach(button => {
        const btn = utils.createElement('button', `btn ${button.className || 'btn-primary'}`);
        btn.textContent = button.text;
        btn.addEventListener('click', button.action);
        footer.appendChild(btn);
      });
      
      content.appendChild(footer);
    }
    
    modal.appendChild(content);
    return modal;
  }
  
  showModal(id, modal) {
    // 既存のモーダルを閉じる
    this.hideAllModals();
    
    // 新しいモーダルを表示
    this.modals.set(id, modal);
    document.body.appendChild(modal);
    modal.classList.add('show');
    
    // フォーカス管理
    const firstButton = modal.querySelector('button');
    if (firstButton) {
      firstButton.focus();
    }
  }
  
  hideModal(id) {
    const modal = this.modals.get(id);
    if (modal) {
      modal.classList.remove('show');
      modal.remove();
      this.modals.delete(id);
    }
  }
  
  hideAllModals() {
    this.modals.forEach((modal, id) => {
      this.hideModal(id);
    });
    this.hideErrorModal();
  }
  
  resetChat() {
    if (window.chatManager) {
      window.chatManager.reset();
    }
    
    // お気に入りもクリアするか確認
    const clearFavorites = confirm('お気に入りも削除しますか？');
    if (clearFavorites) {
      utils.storage.remove('favorites');
    }
    
    utils.logger.info('Chat reset completed');
  }
  

  
  updateFavoriteButtons() {
    const favorites = utils.storage.get('favorites', []);
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    favoriteButtons.forEach(button => {
      const productInfo = button.closest('.product-info');
      if (productInfo) {
        const productId = productInfo.dataset.productId;
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
  
  showLoading(message = '処理中...') {
    const loadingOverlay = utils.getElement('#loadingOverlay');
    const loadingText = utils.getElement('.loading-text');
    
    if (loadingText) {
      loadingText.textContent = message;
    }
    
    utils.showElement(loadingOverlay);
  }
  
  hideLoading() {
    const loadingOverlay = utils.getElement('#loadingOverlay');
    utils.hideElement(loadingOverlay);
  }
  
  showNotification(message, type = 'info', duration = 3000) {
    const notification = utils.createElement('div', `notification notification-${type}`);
    notification.textContent = message;
    
    // スタイル設定
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '12px 20px',
      borderRadius: '8px',
      color: 'white',
      fontWeight: '500',
      zIndex: '10000',
      transform: 'translateX(100%)',
      transition: 'transform 0.3s ease'
    });
    
    // タイプ別の背景色
    const colors = {
      info: '#0078d7',
      success: '#28a745',
      warning: '#ffc107',
      error: '#dc3545'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // アニメーション
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自動削除
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, duration);
  }
  
  handleResize() {
    // レスポンシブ対応の処理
  }
  
  // アクセシビリティ機能
  setFocusTrap(container) {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    container.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    });
  }
  
  // キーボードナビゲーション
  setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K でチャット入力にフォーカス
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const messageInput = utils.getElement('#messageInput');
        if (messageInput) {
          messageInput.focus();
        }
      }
      
      // Ctrl/Cmd + R でリセット
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        this.showResetConfirm();
      }
    });
  }
  
  // テーマ切り替え
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    utils.storage.set('theme', newTheme);
    
    this.showNotification(
      newTheme === 'dark' ? 'ダークモードに切り替えました' : 'ライトモードに切り替えました',
      'info',
      2000
    );
  }
  
  // 初期テーマ設定
  initializeTheme() {
    const savedTheme = utils.storage.get('theme', 'light');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme === 'auto' ? (prefersDark ? 'dark' : 'light') : savedTheme;
    
    document.documentElement.setAttribute('data-theme', theme);
  }

  showDummyProducts() {
    const dummyProducts = [
      {
        id: 'prod_001',
        title: '軽量折りたたみ日傘 白',
        price: 2980,
        store: '楽天市場',
        image: '/images/placeholder.svg',
        rating: 4.2,
        reviewCount: 156
      },
      {
        id: 'prod_002',
        title: 'UVカット日傘 ブラック',
        price: 1580,
        store: 'Amazon',
        image: '/images/placeholder.svg',
        rating: 4.5,
        reviewCount: 89
      },
      {
        id: 'prod_003',
        title: '高級日傘 レディース',
        price: 5980,
        store: 'Yahoo!ショッピング',
        image: '/images/placeholder.svg',
        rating: 4.8,
        reviewCount: 23
      }
    ];
    
    this.updateSidebarContent(this.createProductCardsHTML(dummyProducts));
  }
  
  createProductCardsHTML(products) {
    if (!products || products.length === 0) {
      return `
        <div class="empty-state">
          <div class="empty-state-icon">🛍️</div>
          <div class="empty-state-title">商品が見つかりません</div>
          <div class="empty-state-text">チャットで商品を検索してみてください</div>
        </div>
      `;
    }
    
    return products.map(product => `
      <div class="product-card" data-product-id="${product.id}">
        <div class="product-card-header">
          <img src="${product.image}" alt="${product.title}" class="product-card-image" onerror="this.src='/images/placeholder.svg'">
          <div class="product-card-title">${utils.truncateText(product.title, 40)}</div>
        </div>
        <div class="product-card-price">${utils.formatPrice(product.price)}</div>
        <div class="product-card-store">${product.store}</div>
        <div class="product-card-rating">
          <span class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</span>
          <span class="rating-text">${product.rating} (${product.reviewCount}件)</span>
        </div>
        <div class="product-card-actions">
          <button class="btn btn-primary btn-sm" onclick="uiManager.viewProduct('${product.id}')">詳細</button>
          <button class="btn btn-secondary btn-sm favorite-btn" onclick="uiManager.toggleFavorite('${product.id}')">♡</button>
        </div>
      </div>
    `).join('');
  }
  
  viewProduct(productId) {
    // ダミー商品データ
    const dummyProducts = {
      'prod_001': {
        id: 'prod_001',
        title: '軽量折りたたみ日傘 白',
        price: 2980,
        store: '楽天市場',
        image: '/images/placeholder.svg',
        rating: 4.2,
        reviewCount: 156,
        description: '軽量で持ち運びやすい折りたたみ日傘です。UVカット率99%で、白い色が清潔感を演出します。',
        features: ['UVカット率99%', '軽量設計', '折りたたみ式', '白い色'],
        shipping: '送料無料',
        delivery: '2-3営業日'
      },
      'prod_002': {
        id: 'prod_002',
        title: 'UVカット日傘 ブラック',
        price: 1580,
        store: 'Amazon',
        image: '/images/placeholder.svg',
        rating: 4.5,
        reviewCount: 89,
        description: 'シンプルでスタイリッシュなブラックの日傘。UVカット機能付きで、おしゃれと実用性を両立。',
        features: ['UVカット機能', 'ブラックカラー', 'シンプルデザイン', '軽量'],
        shipping: '送料無料',
        delivery: '1-2営業日'
      },
      'prod_003': {
        id: 'prod_003',
        title: '高級日傘 レディース',
        price: 5980,
        store: 'Yahoo!ショッピング',
        image: '/images/placeholder.svg',
        rating: 4.8,
        reviewCount: 23,
        description: '高級感のあるレディース向け日傘。上質な素材を使用し、エレガントなデザインが特徴です。',
        features: ['高級素材', 'エレガントデザイン', 'レディース向け', 'UVカット'],
        shipping: '送料500円',
        delivery: '3-5営業日'
      }
    };
    
    const product = dummyProducts[productId];
    if (!product) {
      this.showNotification('商品が見つかりません', 'error');
      return;
    }
    
    const modal = this.createModal({
      title: '商品詳細',
      content: `
        <div class="product-detail">
          <div class="product-detail-image">
            <img src="${product.image}" alt="${product.title}" onerror="this.src='/images/placeholder.svg'">
          </div>
          <div class="product-detail-info">
            <h4 class="product-detail-title">${product.title}</h4>
            <div class="product-detail-price">${utils.formatPrice(product.price)}</div>
            <div class="product-detail-store">${product.store}</div>
            <div class="product-detail-rating">
              <span class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</span>
              <span class="rating-text">${product.rating} (${product.reviewCount}件のレビュー)</span>
            </div>
            <div class="product-detail-description">
              <h5>商品説明</h5>
              <p>${product.description}</p>
            </div>
            <div class="product-detail-features">
              <h5>特徴</h5>
              <ul>
                ${product.features.map(feature => `<li>${feature}</li>`).join('')}
              </ul>
            </div>
            <div class="product-detail-shipping">
              <div><strong>送料:</strong> ${product.shipping}</div>
              <div><strong>お届け:</strong> ${product.delivery}</div>
            </div>
          </div>
        </div>
      `,
      buttons: [
        {
          text: 'お気に入りに追加',
          className: 'btn-primary',
          action: () => {
            this.toggleFavorite(productId);
            this.hideModal('productDetail');
          }
        },
        {
          text: '閉じる',
          className: 'btn-secondary',
          action: () => {
            this.hideModal('productDetail');
          }
        }
      ]
    });
    
    this.showModal('productDetail', modal);
  }
  
  toggleFavorite(productId) {
    const favorites = utils.storage.get('favorites', []);
    const dummyProducts = {
      'prod_001': { id: 'prod_001', title: '軽量折りたたみ日傘 白', price: 2980, store: '楽天市場' },
      'prod_002': { id: 'prod_002', title: 'UVカット日傘 ブラック', price: 1580, store: 'Amazon' },
      'prod_003': { id: 'prod_003', title: '高級日傘 レディース', price: 5980, store: 'Yahoo!ショッピング' }
    };
    
    const product = dummyProducts[productId];
    if (!product) return;
    
    const existingIndex = favorites.findIndex(fav => fav.id === productId);
    
    if (existingIndex >= 0) {
      favorites.splice(existingIndex, 1);
      this.showNotification('お気に入りから削除しました', 'info');
    } else {
      favorites.push(product);
      this.showNotification('お気に入りに追加しました', 'success');
    }
    
    utils.storage.set('favorites', favorites);
    this.updateFavoriteButtons();
  }
}

// グローバルインスタンス
window.uiManager = new UIManager(); 