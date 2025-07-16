/**
 * メインアプリケーション
 */

class ShoppingAgentApp {
  constructor() {
    this.isInitialized = false;
    this.config = {
      apiBaseUrl: '/api',
      sessionTimeout: 24 * 60 * 60 * 1000, // 24時間
      maxMessageLength: 1000,
      autoSaveInterval: 30000, // 30秒
      retryAttempts: 3,
      retryDelay: 1000
    };
    
    // 初期化
    this.initialize();
  }
  
  async initialize() {
    try {
      utils.logger.info('Initializing Shopping Agent App...');
      
      // テーマ初期化
      if (window.uiManager) {
        window.uiManager.initializeTheme();
      }
      
      // キーボードナビゲーション設定
      this.setupKeyboardNavigation();
      
      // セッション管理
      this.initializeSession();
      
      // 自動保存設定
      this.setupAutoSave();
      
      // エラーハンドリング
      this.setupErrorHandling();
      
      // パフォーマンス監視
      this.setupPerformanceMonitoring();
      
      // アクセシビリティ設定
      this.setupAccessibility();
      
      this.isInitialized = true;
      utils.logger.info('Shopping Agent App initialized successfully');
      
      // 初期化完了通知
      this.showWelcomeMessage();
      
    } catch (error) {
      utils.logger.error('Failed to initialize app:', error);
      this.showError('アプリケーションの初期化に失敗しました');
    }
  }
  
  setupKeyboardNavigation() {
    if (window.uiManager) {
      window.uiManager.setupKeyboardNavigation();
    }
  }
  
  initializeSession() {
    // セッションタイムアウトチェック
    const lastActivity = utils.sessionStorage.get('lastActivity');
    if (lastActivity) {
      const timeSinceLastActivity = Date.now() - new Date(lastActivity).getTime();
      if (timeSinceLastActivity > this.config.sessionTimeout) {
        utils.logger.info('Session expired, clearing data');
        this.clearSession();
      }
    }
    
    // 最終アクティビティ時刻を更新
    utils.sessionStorage.set('lastActivity', new Date().toISOString());
  }
  
  setupAutoSave() {
    // 定期的な自動保存
    setInterval(() => {
      if (window.chatManager) {
        window.chatManager.saveSession();
      }
      utils.sessionStorage.set('lastActivity', new Date().toISOString());
    }, this.config.autoSaveInterval);
  }
  
  setupErrorHandling() {
    // グローバルエラーハンドリング
    window.addEventListener('error', (event) => {
      utils.logger.error('Global error:', event.error);
      this.showError('予期しないエラーが発生しました');
    });
    
    // 未処理のPromise拒否
    window.addEventListener('unhandledrejection', (event) => {
      utils.logger.error('Unhandled promise rejection:', event.reason);
      this.showError('通信エラーが発生しました');
    });
    
    // ネットワーク状態監視
    window.addEventListener('online', () => {
      utils.logger.info('Network connection restored');
      this.showNotification('ネットワーク接続が復旧しました', 'success');
    });
    
    window.addEventListener('offline', () => {
      utils.logger.warn('Network connection lost');
      this.showNotification('ネットワーク接続が切断されました', 'warning');
    });
  }
  
  setupPerformanceMonitoring() {
    // ページ読み込み時間の監視
    window.addEventListener('load', () => {
      const loadTime = performance.now();
      utils.logger.info(`Page loaded in ${loadTime.toFixed(2)}ms`);
      
      if (loadTime > 3000) {
        utils.logger.warn('Slow page load detected');
      }
    });
    
    // メモリ使用量の監視（開発環境のみ）
    if (process.env.NODE_ENV === 'development') {
      setInterval(() => {
        if (performance.memory) {
          const memoryUsage = performance.memory.usedJSHeapSize / 1024 / 1024;
          utils.logger.debug(`Memory usage: ${memoryUsage.toFixed(2)}MB`);
        }
      }, 30000);
    }
  }
  
  setupAccessibility() {
    // フォーカス表示の強化
    const style = document.createElement('style');
    style.textContent = `
      .focus-visible {
        outline: 2px solid #0078d7 !important;
        outline-offset: 2px !important;
      }
    `;
    document.head.appendChild(style);
    
    // フォーカス管理
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
      }
    });
    
    document.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-navigation');
    });
    
    // スキップリンク
    this.createSkipLink();
  }
  
  createSkipLink() {
    const skipLink = utils.createElement('a', 'skip-link');
    skipLink.href = '#chatMessages';
    skipLink.textContent = 'メインコンテンツにスキップ';
    
    Object.assign(skipLink.style, {
      position: 'absolute',
      top: '-40px',
      left: '6px',
      background: '#0078d7',
      color: 'white',
      padding: '8px',
      textDecoration: 'none',
      borderRadius: '4px',
      zIndex: '10000'
    });
    
    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
  }
  
  showWelcomeMessage() {
    // 初回訪問時のウェルカムメッセージ
    const isFirstVisit = !utils.storage.get('hasVisited');
    if (isFirstVisit) {
      setTimeout(() => {
        this.showNotification('お買い物エージェントへようこそ！', 'info', 5000);
        utils.storage.set('hasVisited', true);
      }, 1000);
    }
  }
  
  showError(message) {
    if (window.uiManager) {
      window.uiManager.showErrorModal(message);
    } else {
      alert(message);
    }
  }
  
  showNotification(message, type = 'info', duration = 3000) {
    if (window.uiManager) {
      window.uiManager.showNotification(message, type, duration);
    }
  }
  
  clearSession() {
    // セッション情報をクリア
    utils.sessionStorage.clear();
    
    // チャットマネージャーをリセット
    if (window.chatManager) {
      window.chatManager.reset();
    }
    
    utils.logger.info('Session cleared');
  }
  
  // アプリケーション状態の取得
  getAppState() {
    return {
      isInitialized: this.isInitialized,
      sessionId: window.chatManager ? window.chatManager.getSessionId() : null,
      messageCount: window.chatManager ? window.chatManager.getMessages().length : 0,
      favoritesCount: utils.storage.get('favorites', []).length,
      lastActivity: utils.sessionStorage.get('lastActivity'),
      device: {
        isMobile: utils.device.isMobile(),
        isTablet: utils.device.isTablet(),
        isDesktop: utils.device.isDesktop()
      },
      browser: {
        isChrome: utils.browser.isChrome(),
        isFirefox: utils.browser.isFirefox(),
        isSafari: utils.browser.isSafari(),
        isEdge: utils.browser.isEdge()
      }
    };
  }
  
  // デバッグ情報の出力
  debug() {
    const state = this.getAppState();
    console.group('Shopping Agent App Debug Info');
    console.log('App State:', state);
    console.log('Config:', this.config);
    console.log('Utils available:', !!window.utils);
    console.log('Chat Manager available:', !!window.chatManager);
    console.log('UI Manager available:', !!window.uiManager);
    console.groupEnd();
  }
  
  // アプリケーションの再初期化
  reinitialize() {
    utils.logger.info('Reinitializing app...');
    this.isInitialized = false;
    this.initialize();
  }
}

// アプリケーションの初期化
document.addEventListener('DOMContentLoaded', () => {
  // グローバルアプリケーションインスタンス
  window.app = new ShoppingAgentApp();
  
  // 開発環境でのデバッグ機能
  if (process.env.NODE_ENV === 'development') {
    // グローバルデバッグ関数
    window.debugApp = () => {
      window.app.debug();
    };
    
    // コンソールにデバッグ情報を表示
    setTimeout(() => {
      console.log('Shopping Agent App loaded. Use debugApp() for debug info.');
    }, 1000);
  }
});

// ページ離脱時の処理
window.addEventListener('beforeunload', () => {
  // セッション情報の保存
  if (window.chatManager) {
    window.chatManager.saveSession();
  }
  
  utils.sessionStorage.set('lastActivity', new Date().toISOString());
});

// ページ可視性変更時の処理
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    // ページが表示された時の処理
    utils.logger.info('Page became visible');
    
    // セッションタイムアウトチェック
    const lastActivity = utils.sessionStorage.get('lastActivity');
    if (lastActivity) {
      const timeSinceLastActivity = Date.now() - new Date(lastActivity).getTime();
      if (timeSinceLastActivity > window.app.config.sessionTimeout) {
        utils.logger.info('Session expired during page visibility change');
        window.app.clearSession();
      }
    }
  }
}); 