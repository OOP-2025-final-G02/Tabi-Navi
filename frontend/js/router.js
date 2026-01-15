/**
 * ページルーティングとHTMLインポートを管理するモジュール
 */

class Router {
  constructor() {
    this.container = document.getElementById("app-container");
    this.currentPage = null;

    // ハッシュ変更イベントをリッスン
    window.addEventListener("hashchange", () => this.handleRouteChange());
  }

  /**
   * URLハッシュからページ名を取得
   * @returns {string} ページ名
   */
  getPageFromHash() {
    const hash = window.location.hash;
    // #/page/list -> list
    // #/page/input-form -> input-form
    const match = hash.match(/^#\/page\/(.+)$/);
    return match ? match[1] : "list"; // デフォルトはlist
  }

  /**
   * ハッシュ変更時の処理
   */
  handleRouteChange() {
    const pageName = this.getPageFromHash();
    this.loadPageContent(pageName);
  }

  /**
   * 指定されたページをロードして表示（URLも更新）
   * @param {string} pageName - ページ名（input-form, loading, plan-result, list）
   * @param {boolean} updateUrl - URLを更新するか（デフォルト: true）
   */
  async loadPage(pageName, updateUrl = true) {
    // URLを更新
    if (updateUrl) {
      window.location.hash = `#/page/${pageName}`;
    }

    await this.loadPageContent(pageName);
  }

  /**
   * ページコンテンツをロード（URL更新なし）
   * @param {string} pageName - ページ名
   */
  async loadPageContent(pageName) {
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

    // listページの初期化
    if (pageName === "list" && typeof initializePage === "function") {
      initializePage();
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

  /**
   * 初期化：URLハッシュに基づいてページをロード
   */
  init() {
    const pageName = this.getPageFromHash();
    this.loadPageContent(pageName);
  }
}

// グローバルルーターインスタンス
const router = new Router();
