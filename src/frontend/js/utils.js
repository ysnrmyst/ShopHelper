/**
 * ユーティリティ関数
 */

// 日付・時刻のフォーマット
const formatTime = (date) => {
  const now = new Date();
  const diff = now - date;
  
  // 1分以内
  if (diff < 60000) {
    return '今';
  }
  
  // 1時間以内
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return `${minutes}分前`;
  }
  
  // 24時間以内
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000);
    return `${hours}時間前`;
  }
  
  // それ以外
  return date.toLocaleTimeString('ja-JP', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 数値のフォーマット（価格表示用）
const formatPrice = (price) => {
  if (!price || price === 0) return '価格未定';
  return `¥${price.toLocaleString()}`;
};

// 文字列の長さ制限
const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// HTMLエスケープ
const escapeHtml = (text) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

// 入力値のバリデーション
const validateInput = (input) => {
  if (!input || typeof input !== 'string') {
    return { isValid: false, error: '入力が必要です' };
  }
  
  const trimmed = input.trim();
  if (trimmed.length === 0) {
    return { isValid: false, error: '入力が必要です' };
  }
  
  if (trimmed.length > 1000) {
    return { isValid: false, error: '1000文字以内で入力してください' };
  }
  
  // XSS対策：危険な文字列をチェック
  const dangerousPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi
  ];
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(trimmed)) {
      return { isValid: false, error: '無効な文字が含まれています' };
    }
  }
  
  return { isValid: true, value: trimmed };
};

// DOM要素の取得（エラーハンドリング付き）
const getElement = (selector, parent = document) => {
  const element = parent.querySelector(selector);
  if (!element) {
    console.warn(`Element not found: ${selector}`);
  }
  return element;
};

// DOM要素の作成
const createElement = (tag, className = '', content = '') => {
  const element = document.createElement(tag);
  if (className) {
    element.className = className;
  }
  if (content) {
    element.textContent = content;
  }
  return element;
};

// 要素の表示・非表示
const showElement = (element) => {
  if (element) {
    element.style.display = '';
    element.classList.remove('hidden');
  }
};

const hideElement = (element) => {
  if (element) {
    element.style.display = 'none';
    element.classList.add('hidden');
  }
};

// 要素の有効・無効
const enableElement = (element) => {
  if (element) {
    element.disabled = false;
    element.classList.remove('disabled');
  }
};

const disableElement = (element) => {
  if (element) {
    element.disabled = true;
    element.classList.add('disabled');
  }
};

// ローカルストレージ操作
const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn('Failed to get from localStorage:', error);
      return defaultValue;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.warn('Failed to set to localStorage:', error);
      return false;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.warn('Failed to remove from localStorage:', error);
      return false;
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.warn('Failed to clear localStorage:', error);
      return false;
    }
  }
};

// セッションストレージ操作
const sessionStorage = {
  get: (key, defaultValue = null) => {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn('Failed to get from sessionStorage:', error);
      return defaultValue;
    }
  },
  
  set: (key, value) => {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.warn('Failed to set to sessionStorage:', error);
      return false;
    }
  },
  
  remove: (key) => {
    try {
      sessionStorage.removeItem(key);
      return true;
    } catch (error) {
      console.warn('Failed to remove from sessionStorage:', error);
      return false;
    }
  },
  
  clear: () => {
    try {
      sessionStorage.clear();
      return true;
    } catch (error) {
      console.warn('Failed to clear sessionStorage:', error);
      return false;
    }
  }
};

// デバウンス関数
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// スロットル関数
const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// ランダムID生成
const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

// UUID生成
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

// 配列の重複除去
const uniqueArray = (array, key = null) => {
  if (!Array.isArray(array)) return [];
  
  if (key) {
    const seen = new Set();
    return array.filter(item => {
      const value = item[key];
      if (seen.has(value)) {
        return false;
      }
      seen.add(value);
      return true;
    });
  }
  
  return [...new Set(array)];
};

// オブジェクトのディープコピー
const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
  return obj;
};

// エラーハンドリング
const handleError = (error, context = '') => {
  console.error(`Error in ${context}:`, error);
  
  // エラーメッセージの生成
  let message = 'エラーが発生しました';
  
  if (error.name === 'NetworkError') {
    message = 'ネットワークエラーが発生しました';
  } else if (error.name === 'TimeoutError') {
    message = 'タイムアウトが発生しました';
  } else if (error.message) {
    message = error.message;
  }
  
  return {
    error: true,
    message,
    details: error
  };
};

// ログ出力
const logger = {
  info: (message, data = null) => {
    console.log(`[INFO] ${message}`, data);
  },
  
  warn: (message, data = null) => {
    console.warn(`[WARN] ${message}`, data);
  },
  
  error: (message, data = null) => {
    console.error(`[ERROR] ${message}`, data);
  },
  
  debug: (message, data = null) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[DEBUG] ${message}`, data);
    }
  }
};

// デバイス判定
const device = {
  isMobile: () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },
  
  isTablet: () => {
    return /iPad|Android(?=.*\bMobile\b)(?=.*\bSafari\b)/i.test(navigator.userAgent);
  },
  
  isDesktop: () => {
    return !device.isMobile() && !device.isTablet();
  }
};

// ブラウザ判定
const browser = {
  isChrome: () => {
    return /Chrome/.test(navigator.userAgent) && !/Edge/.test(navigator.userAgent);
  },
  
  isFirefox: () => {
    return /Firefox/.test(navigator.userAgent);
  },
  
  isSafari: () => {
    return /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
  },
  
  isEdge: () => {
    return /Edge/.test(navigator.userAgent);
  }
};

// エクスポート
window.utils = {
  formatTime,
  formatPrice,
  truncateText,
  escapeHtml,
  validateInput,
  getElement,
  createElement,
  showElement,
  hideElement,
  enableElement,
  disableElement,
  storage,
  sessionStorage,
  debounce,
  throttle,
  generateId,
  generateUUID,
  uniqueArray,
  deepClone,
  handleError,
  logger,
  device,
  browser
}; 