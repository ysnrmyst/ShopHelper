/**
 * チャット機能
 */

class ChatManager {
  constructor() {
    this.messages = [];
    this.sessionId = utils.generateUUID();
    this.isLoading = false;
    
    // DOM要素
    this.chatMessages = utils.getElement('#chatMessages');
    this.messageInput = utils.getElement('#messageInput');
    this.sendBtn = utils.getElement('#sendBtn');
    this.suggestButtons = utils.getElement('#suggestButtons');
    this.loadingOverlay = utils.getElement('#loadingOverlay');
    
    // イベントリスナー
    this.bindEvents();
    
    // 初期化
    this.initialize();
  }
  
  bindEvents() {
    // 送信ボタンクリック
    this.sendBtn.addEventListener('click', () => {
      this.sendMessage();
    });
    
    // Enterキーで送信
    this.messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // 入力中の処理
    this.messageInput.addEventListener('input', utils.debounce(() => {
      this.handleInputChange();
    }, 300));
  }
  
  initialize() {
    // セッション情報の復元
    const savedSession = utils.sessionStorage.get('chatSession');
    if (savedSession) {
      this.sessionId = savedSession.sessionId;
      this.messages = savedSession.messages || [];
      this.renderMessages();
    }
    
    // 初期メッセージの表示
    if (this.messages.length === 0) {
      this.addSystemMessage('お買い物エージェントへようこそ！何をお探しですか？');
      this.updateSuggestions([
        '日傘が欲しい',
        'ノートPCを探している',
        'キッチン用品を買いたい'
      ]);
    }
    
    // セッション情報の保存
    this.saveSession();
  }
  
  sendMessage() {
    const input = this.messageInput.value.trim();
    if (!input) return;
    
    // 入力値のバリデーション
    const validation = utils.validateInput(input);
    if (!validation.isValid) {
      this.showError(validation.error);
      return;
    }
    
    // ユーザーメッセージを追加
    this.addUserMessage(input);
    
    // 入力フィールドをクリア
    this.messageInput.value = '';
    
    // 送信ボタンを無効化
    utils.disableElement(this.sendBtn);
    
    // ローディング表示
    this.showLoading();
    
    // サーバーにメッセージを送信
    this.sendToServer(input);
  }
  
  async sendToServer(message) {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          sessionId: this.sessionId,
          timestamp: new Date().toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // エージェントの応答を追加
      if (data.response) {
        this.addAgentMessage(data.response);
      }
      
      // 商品情報がある場合
      if (data.products && data.products.length > 0) {
        this.addProductMessage(data.products);
      }
      
      // サジェストボタンの更新
      if (data.suggestions && data.suggestions.length > 0) {
        this.updateSuggestions(data.suggestions);
      }
      
      // セッション情報の更新
      this.sessionId = data.sessionId || this.sessionId;
      this.saveSession();
      
    } catch (error) {
      utils.logger.error('Failed to send message:', error);
      this.addErrorMessage('申し訳ございません。通信エラーが発生しました。');
    } finally {
      this.hideLoading();
      utils.enableElement(this.sendBtn);
    }
  }
  
  addUserMessage(text) {
    const message = {
      id: utils.generateId(),
      type: 'user',
      text: utils.escapeHtml(text),
      timestamp: new Date(),
      displayTime: utils.formatTime(new Date())
    };
    
    this.messages.push(message);
    this.renderMessage(message);
    this.saveSession();
  }
  
  addAgentMessage(text) {
    const message = {
      id: utils.generateId(),
      type: 'agent',
      text: utils.escapeHtml(text),
      timestamp: new Date(),
      displayTime: utils.formatTime(new Date())
    };
    
    this.messages.push(message);
    this.renderMessage(message);
    this.saveSession();
  }
  
  addProductMessage(products) {
    const message = {
      id: utils.generateId(),
      type: 'product',
      products: products,
      timestamp: new Date(),
      displayTime: utils.formatTime(new Date())
    };
    
    this.messages.push(message);
    this.renderMessage(message);
    this.saveSession();
  }
  
  addSystemMessage(text) {
    const message = {
      id: utils.generateId(),
      type: 'system',
      text: utils.escapeHtml(text),
      timestamp: new Date(),
      displayTime: utils.formatTime(new Date())
    };
    
    this.messages.push(message);
    this.renderMessage(message);
    this.saveSession();
  }
  
  addErrorMessage(text) {
    const message = {
      id: utils.generateId(),
      type: 'error',
      text: utils.escapeHtml(text),
      timestamp: new Date(),
      displayTime: utils.formatTime(new Date())
    };
    
    this.messages.push(message);
    this.renderMessage(message);
    this.saveSession();
  }
  
  renderMessage(message) {
    const messageElement = utils.createElement('div', `message ${message.type}`);
    messageElement.setAttribute('data-message-id', message.id);
    
    const bubbleElement = utils.createElement('div', 'message-bubble');
    
    switch (message.type) {
      case 'user':
      case 'agent':
        bubbleElement.innerHTML = message.text;
        break;
        
      case 'product':
        bubbleElement.appendChild(this.createProductElement(message.products));
        break;
        
      case 'system':
      case 'error':
        bubbleElement.innerHTML = message.text;
        break;
    }
    
    // タイムスタンプを追加
    const timeElement = utils.createElement('div', 'message-time');
    timeElement.textContent = message.displayTime;
    bubbleElement.appendChild(timeElement);
    
    messageElement.appendChild(bubbleElement);
    this.chatMessages.appendChild(messageElement);
    
    // スクロールを最下部に
    this.scrollToBottom();
    
    // アニメーション
    messageElement.classList.add('fade-in');
  }
  
  renderMessages() {
    this.chatMessages.innerHTML = '';
    this.messages.forEach(message => {
      this.renderMessage(message);
    });
  }
  
  createProductElement(products) {
    const container = utils.createElement('div', 'product-message');
    
    products.forEach(product => {
      const productElement = utils.createElement('div', 'product-info');
      productElement.setAttribute('data-product-id', product.id); // 商品IDを追加
      
      // 商品画像
      if (product.image) {
        const imageElement = utils.createElement('img', 'product-image');
        imageElement.src = product.image;
        imageElement.alt = product.title;
        imageElement.onerror = () => {
          imageElement.src = '/images/placeholder.png';
        };
        productElement.appendChild(imageElement);
      }
      
      // 商品詳細
      const detailsElement = utils.createElement('div', 'product-details');
      
      const titleElement = utils.createElement('div', 'product-title');
      titleElement.textContent = utils.truncateText(product.title, 60);
      detailsElement.appendChild(titleElement);
      
      const priceElement = utils.createElement('div', 'product-price');
      priceElement.textContent = utils.formatPrice(product.price);
      detailsElement.appendChild(priceElement);
      
      if (product.store) {
        const storeElement = utils.createElement('div', 'product-store');
        storeElement.textContent = product.store;
        detailsElement.appendChild(storeElement);
      }
      
      // アクションボタン
      const actionsElement = utils.createElement('div', 'product-actions');
      
      const viewBtn = utils.createElement('button', 'btn btn-primary');
      viewBtn.textContent = '詳細を見る';
      viewBtn.addEventListener('click', () => {
        this.viewProduct(product);
      });
      actionsElement.appendChild(viewBtn);
      
      const favoriteBtn = utils.createElement('button', 'btn btn-secondary favorite-btn');
      favoriteBtn.innerHTML = '♡';
      favoriteBtn.addEventListener('click', () => {
        this.toggleFavorite(product);
      });
      actionsElement.appendChild(favoriteBtn);
      
      detailsElement.appendChild(actionsElement);
      productElement.appendChild(detailsElement);
      container.appendChild(productElement);
    });
    
    return container;
  }
  
  updateSuggestions(suggestions) {
    this.suggestButtons.innerHTML = '';
    
    suggestions.forEach(suggestion => {
      const button = utils.createElement('button', 'suggest-btn');
      button.textContent = suggestion;
      button.addEventListener('click', () => {
        this.messageInput.value = suggestion;
        this.sendMessage();
      });
      this.suggestButtons.appendChild(button);
    });
  }
  
  viewProduct(product) {
    // 商品詳細ページへの遷移またはモーダル表示
    utils.logger.info('View product:', product);
    
    // ここで商品詳細画面を表示
    // 現在はログ出力のみ
  }
  
  toggleFavorite(product) {
    const favorites = utils.storage.get('favorites', []);
    const existingIndex = favorites.findIndex(fav => fav.id === product.id);
    
    if (existingIndex >= 0) {
      favorites.splice(existingIndex, 1);
      utils.logger.info('Removed from favorites:', product.title);
    } else {
      favorites.push(product);
      utils.logger.info('Added to favorites:', product.title);
    }
    
    utils.storage.set('favorites', favorites);
    
    // お気に入りボタンの状態を更新
    this.updateFavoriteButtons();
  }
  
  updateFavoriteButtons() {
    const favorites = utils.storage.get('favorites', []);
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    favoriteButtons.forEach(button => {
      const productId = button.closest('.product-info').dataset.productId;
      if (favorites.find(fav => fav.id === productId)) {
        button.classList.add('active');
        button.innerHTML = '♥';
      } else {
        button.classList.remove('active');
        button.innerHTML = '♡';
      }
    });
  }
  
  showLoading() {
    this.isLoading = true;
    utils.showElement(this.loadingOverlay);
    
    // 送信ボタンのローディング表示
    const btnText = utils.getElement('.btn-text', this.sendBtn);
    const btnLoading = utils.getElement('.btn-loading', this.sendBtn);
    
    utils.hideElement(btnText);
    utils.showElement(btnLoading);
  }
  
  hideLoading() {
    this.isLoading = false;
    utils.hideElement(this.loadingOverlay);
    
    // 送信ボタンの通常表示に戻す
    const btnText = utils.getElement('.btn-text', this.sendBtn);
    const btnLoading = utils.getElement('.btn-loading', this.sendBtn);
    
    utils.showElement(btnText);
    utils.hideElement(btnLoading);
  }
  
  showError(message) {
    // エラーモーダルの表示
    const errorModal = utils.getElement('#errorModal');
    const errorMessage = utils.getElement('#errorMessage');
    
    errorMessage.textContent = message;
    utils.showElement(errorModal);
  }
  
  scrollToBottom() {
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }
  
  handleInputChange() {
    const input = this.messageInput.value.trim();
    const isValid = input.length > 0 && input.length <= 1000;
    
    utils.enableElement(this.sendBtn);
    this.sendBtn.disabled = !isValid;
  }
  
  saveSession() {
    const sessionData = {
      sessionId: this.sessionId,
      messages: this.messages,
      timestamp: new Date().toISOString()
    };
    
    utils.sessionStorage.set('chatSession', sessionData);
  }
  
  reset() {
    // セッションをリセット
    this.messages = [];
    this.sessionId = utils.generateUUID();
    this.sessionStorage.remove('chatSession');
    
    // UIをリセット
    this.chatMessages.innerHTML = '';
    this.messageInput.value = '';
    this.suggestButtons.innerHTML = '';
    
    // 初期メッセージを表示
    this.addSystemMessage('お買い物エージェントへようこそ！何をお探しですか？');
    this.updateSuggestions([
      '日傘が欲しい',
      'ノートPCを探している',
      'キッチン用品を買いたい'
    ]);
    
    utils.logger.info('Chat session reset');
  }
  
  // デバッグ用メソッド
  getMessages() {
    return this.messages;
  }
  
  getSessionId() {
    return this.sessionId;
  }
}

// グローバルインスタンス
window.chatManager = new ChatManager(); 