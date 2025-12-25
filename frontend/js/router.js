/**
 * ページルーティングとHTMLインポートを管理するモジュール
 */

class Router {
  constructor() {
    this.container = document.getElementById("app-container");
    this.currentPage = null;
  }

  /**
   * 指定されたページをロードして表示
   * @param {string} pageName - ページ名（input-form, loading, plan-result）
   */
  async loadPage(pageName) {
    try {
      const response = await fetch(`pages/${pageName}.html`);

      if (!response.ok) {
        throw new Error(`ページの読み込みに失敗: ${pageName}`);
      }

      const html = await response.text();
      this.container.innerHTML = html;
      this.currentPage = pageName;

      // ページロード後のコールバックを実行
      this.onPageLoaded(pageName);
    } catch (error) {
      console.error("Page load error:", error);
      this.showError("ページの読み込みに失敗しました");
    }
  }

  /**
   * ページロード後の処理
   * @param {string} pageName - ロードされたページ名
   */
  onPageLoaded(pageName) {
    // ページ固有の初期化処理
    if (window.app && typeof window.app.onPageLoaded === "function") {
      window.app.onPageLoaded(pageName);
    }
  }

  /**
   * エラーメッセージを表示
   * @param {string} message - エラーメッセージ
   */
  showError(message) {
    this.container.innerHTML = `
            <div class="error-container">
                <p class="error-message">${message}</p>
            </div>
        `;
  }

  /**
   * 現在のページ名を取得
   * @returns {string} 現在のページ名
   */
  getCurrentPage() {
    return this.currentPage;
  }
}

// グローバルルーターインスタンス
const router = new Router();
