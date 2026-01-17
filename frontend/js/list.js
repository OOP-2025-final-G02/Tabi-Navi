/**
 * 旅行プラン一覧ページ - JavaScript
 */

// ========================================
// 初期化処理
// ========================================

/**
 * ページ読み込み時の初期化
 */
function initializePage() {
  // ここに初期化処理を実装
  // - イベントリスナーの登録
  // - 保存されたプランデータの読み込み
  // - プランカードの動的生成

  // プラン一覧を読み込んで表示
  refreshPlanList();

  // 新規作成ボタンのイベントリスナーを登録
  const btnNewPlan = document.getElementById("btnNewPlan");
  if (btnNewPlan) {
    btnNewPlan.addEventListener("click", handleNewPlanClick);
  }

  // プランカードのクリックイベントを登録
  const planCards = document.querySelectorAll(".plan-card");
  planCards.forEach((card) => {
    card.addEventListener("click", () => {
      const planId = card.getAttribute("data-plan-id");
      handlePlanCardClick(planId);
    });
  });
}

// ========================================
// API通信
// ========================================

/**
 * バックエンドから旅行プラン一覧を取得
 * @returns {Promise<Array>} プランデータの配列
 */
async function fetchTravelPlans() {
  // ここにバックエンドAPIからプランデータを取得する処理を実装
  // 例: GET /api/plans
  // 返り値例: [{ id, destination, departure, startDate, endDate, participants, totalCost, ... }]
  try {
    const API_URL = "http://localhost:8000";
    const response = await fetch(`${API_URL}/api/storage/plans/history`);
    
    if (!response.ok) throw new Error("プラン一覧の取得に失敗しました");
    
    const result = await response.json();
    return result.success ? result.data : [];
  } catch (error) {
    console.error("Fetch error:", error);
    return [];
  }
}

/**
 * 特定のプランの詳細データを取得
 * @param {string|number} planId - プランID
 * @returns {Promise<Object>} プランの詳細データ
 */
async function fetchPlanDetails(planId) {
  // ここに特定のプランの詳細情報を取得する処理を実装
  // 例: GET /api/plans/{planId}
}

/**
 * プランを削除
 * @param {string|number} planId - 削除するプランのID
 * @returns {Promise<boolean>} 削除成功の可否
 */
async function deletePlan(planId) {
  // ここにプラン削除処理を実装
  // 例: DELETE /api/plans/{planId}
  // 削除成功後、プラン一覧を再読み込み
}

// ========================================
// UI描画・更新
// ========================================

/**
 * プランカードを動的に生成してDOMに追加
 * @param {Array} plans - プランデータの配列
 */
function renderPlanCards(plans) {
  // ここにプランカードを生成する処理を実装
  // - planCards コンテナを取得
  // - 各プランデータからHTMLを生成
  // - DOM に追加
  const container = document.getElementById("planCards");
  if (!container) return;

  if (!plans || plans.length === 0) {
    showEmptyState();
    return;
  }

  container.innerHTML = plans
    .map((plan) => createPlanCardHTML(plan))
    .join("");
    
  // イベントリスナー再登録（DOMを書き換えたため）
  const planCards = document.querySelectorAll(".plan-card");
  planCards.forEach((card) => {
    card.addEventListener("click", () => {
      const planId = card.getAttribute("data-plan-id");
      handlePlanCardClick(planId);
    });
  });
}

/**
 * 単一のプランカード HTML を生成
 * @param {Object} plan - プランデータ
 * @returns {string} プランカードのHTML
 */
function createPlanCardHTML(plan) {
  // ここにプランカードのHTMLテンプレートを生成する処理を実装
  // パラメータ例: { id, destination, departure, startDate, endDate, days, participants, totalCost }
  
  // DBのデータ構造に合わせてマッピング
  const input = plan.input_data || {};
  const destination = input.destination || "未定";
  const departure = input.origin || "未定";
  const startDate = input.start_date ? formatDate(input.start_date) : "-";
  const endDate = input.end_date ? formatDate(input.end_date) : "-";
  const days = calculateDays(input.start_date, input.end_date);
  const participants = input.travelers || input.people || 1;
  const cost = plan.total_cost || 0;

  return `
    <div class="plan-card" data-plan-id="${plan.plan_id}">
      <h3 class="card-destination">${destination}</h3>
      <p class="card-departure">
        <span class="icon">📍</span>
        <span>${departure}発</span>
      </p>

      <div class="card-details">
        <div class="detail-item">
          <span class="icon">📅</span>
          <span>${startDate} - ${endDate}</span>
          <span class="badge">${days}日間</span>
        </div>

        <div class="detail-item">
          <span class="icon">👥</span>
          <span>${participants}名</span>
        </div>

        <div class="detail-item detail-cost">
          <span class="icon">💰</span>
          <span class="label">総費用</span>
          <span class="cost">${formatCurrency(cost)}</span>
        </div>
      </div>
    </div>
  `;
}

/**
 * プラン一覧を再読み込みして表示を更新
 */
async function refreshPlanList() {
  // ここにプラン一覧の再読み込み処理を実装
  // - fetchTravelPlans() を呼び出し
  // - renderPlanCards() で再描画
  const plans = await fetchTravelPlans();
  renderPlanCards(plans);
}

/**
 * 空のプラン一覧メッセージを表示
 */
function showEmptyState() {
  // ここにプランがない場合のメッセージ表示処理を実装
  // 例: 「保存されたプランはありません」
  const container = document.getElementById("planCards");
  if (container) {
    container.innerHTML = '<div class="empty-state"><p>保存されたプランはまだありません。<br>「新規作成」からプランを作ってみましょう！</p></div>';
  }
}

// ========================================
// イベントハンドラー
// ========================================

/**
 * 新規作成ボタンクリック時の処理
 */
function handleNewPlanClick() {
  // localStorageをクリア（新規作成時）
  localStorage.removeItem("travelFormData");
  localStorage.removeItem("generatedPlan");
  sessionStorage.setItem("clearForm", "true");
  console.log("新規作成ボタンがクリックされました - データクリア完了");

  // router.js を使用して input-form ページに遷移
  if (typeof router !== "undefined") {
    router.loadPage("input-form");
  }
}

/**
 * プランカードクリック時の処理
 * @param {string|number} planId - プランID
 */
function handlePlanCardClick(planId) {
  // ここにプラン詳細画面への遷移処理を実装
  // router.js を使用して plan-result ページに遷移
  // TODO: プランIDをlocalStorageや他の方法で保持して詳細ページで使用
  if (typeof router !== "undefined") {
    router.loadPage("plan-result");
  }
}

/**
 * プラン削除ボタンクリック時の処理
 * @param {Event} event - イベントオブジェクト
 * @param {string|number} planId - プランID
 */
function handleDeletePlanClick(event, planId) {
  // ここにプラン削除処理を実装
  // - イベント伝播を停止 (event.stopPropagation())
  // - 確認ダイアログを表示
  // - deletePlan() を呼び出し
  // - 成功したら refreshPlanList() で更新
}

// ========================================
// ユーティリティ関数
// ========================================

/**
 * 日付を指定フォーマットで整形
 * @param {string|Date} date - 日付
 * @returns {string} フォーマット済み日付文字列 (例: "3/15")
 */
function formatDate(date) {
  // ここに日付フォーマット処理を実装
  // 例: "2026-03-15" → "3/15"
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return date;
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

/**
 * 日数を計算
 * @param {string|Date} startDate - 開始日
 * @param {string|Date} endDate - 終了日
 * @returns {number} 日数
 */
function calculateDays(startDate, endDate) {
  // ここに日数計算処理を実装
  // 例: 3/15 - 3/18 → 3日間
  if (!startDate || !endDate) return 1;
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffTime = Math.abs(end - start);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
  return diffDays + 1; // 当日含むため+1
}

/**
 * 金額をカンマ区切りでフォーマット
 * @param {number} amount - 金額
 * @returns {string} フォーマット済み金額 (例: "¥145,000")
 */
function formatCurrency(amount) {
  // ここに金額フォーマット処理を実装
  // 例: 145000 → "¥145,000"
  return "¥" + Number(amount).toLocaleString();
}

/**
 * ローディング表示を制御
 * @param {boolean} isLoading - ローディング中かどうか
 */
function toggleLoading(isLoading) {
  // ここにローディング表示の制御処理を実装
  // - isLoading が true の場合: ローディングスピナーを表示
  // - isLoading が false の場合: ローディングスピナーを非表示
}

/**
 * エラーメッセージを表示
 * @param {string} message - エラーメッセージ
 */
function showError(message) {
  // ここにエラー表示処理を実装
  // 例: トーストメッセージやアラートで表示
}

// ページロード時の初期化設定
window.addEventListener("DOMContentLoaded", () => {
  window.app = window.app || {};
  
  // 既存のハンドラを退避（plan-generator.jsなどとの競合回避）
  const previousHandler = window.app.onPageLoaded;

  window.app.onPageLoaded = (pageName) => {
    // 既存のハンドラがあれば実行
    if (previousHandler) {
      previousHandler(pageName);
    }

    // リストページの処理
    if (pageName === "list") {
      initializePage();
    }
  };
});
