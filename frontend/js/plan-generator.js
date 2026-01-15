/**
 * plan-generator.js
 * 旅行プラン生成・管理機能
 */

/**
 * フォーム入力値をlocalStorageに保存し、APIを呼び出す
 */
async function saveFormToStorage() {
  const form = document.getElementById("travel-form");
  if (!form) return;

  const formData = new FormData(form);

  // 開始日と終了日から日数を計算
  const startDate = new Date(formData.get("start-date"));
  const endDate = new Date(formData.get("end-date"));

  // バリデーション: 終了日が開始日より前でないか確認
  if (endDate < startDate) {
    alert("終了日は開始日以降である必要があります");
    return;
  }

  const durationMs = endDate - startDate;
  // Math.floor()で切り捨て（1月10日～1月10日=1日、+1で対応）
  const duration = Math.floor(durationMs / (1000 * 60 * 60 * 24)) + 1;

  // 選択された興味カテゴリを取得
  const selectedCategories = Array.from(
    document.querySelectorAll(".interest-btn.active")
  ).map((btn) => btn.getAttribute("data-category"));
  const interests = selectedCategories.join("、");

  const data = {
    tripTitle: formData.get("trip-title") || "",
    departure: formData.get("departure") || "",
    destination: formData.get("destination") || "",
    startDate: formData.get("start-date") || "",
    endDate: formData.get("end-date") || "",
    budget: parseInt(formData.get("budget")) || 0,
    people: parseInt(formData.get("people")) || 1,
    duration: duration || 1,
    interests: interests || "",
    mustVisit: formData.get("must-visit") || "",
  };

  // localStorageに保存
  localStorage.setItem("travelFormData", JSON.stringify(data));

  // バックエンド API を呼び出す
  try {
    const travelPlan = await callPlanGenerationAPI(data);
    // プランをlocalStorageに保存
    localStorage.setItem("generatedPlan", JSON.stringify(travelPlan));
  } catch (error) {
    console.error("API呼び出しエラー:", error);
    // エラーでもプレビューは表示（ダミーデータで表示）
  }
}

/**
 * バックエンド /api/plans API を呼び出し
 *
 * NOTE for バックエンド担当者:
 * - API_URLは環境変数で管理してください（例：process.env.REACT_APP_API_URL）
 * - 現在のハードコードされたURLを変数化する際の実装参考：
 *   const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
 *   fetch(`${API_URL}/api/plans`, {...})
 *
 * - データフロー: フォーム入力 → localStorage保存 → API送信 → DB保存 を想定
 * - 本来はバックエンド側で認証・認可を実装してください
 */
async function callPlanGenerationAPI(formData) {
  const start_date = formData.startDate;
  const end_date = formData.endDate;

  // API リクエスト用データ
  const apiRequest = {
    origin: formData.departure || "東京", // 出発場所を使用
    destination: formData.destination,
    start_date: start_date,
    end_date: end_date,
    budget: parseInt(formData.budget),
    interests: formData.interests
      ? formData.interests.split("、").filter((i) => i.trim())
      : [],
    additional_notes: formData.mustVisit || "",
  };
  // 下記のURLを環境変数で管理してください
  const API_URL = "http://localhost:8000"; // ← 環境変数化予定

  const response = await fetch(`${API_URL}/api/plans`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(apiRequest),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return await response.json();
}

/**
 * フォームをクリア（新規作成時）
 */
function clearForm() {
  const form = document.getElementById("travel-form");
  if (!form) return;

  // フォームのリセット
  form.reset();

  // 興味ボタンをクリア
  document.querySelectorAll(".interest-btn").forEach((btn) => {
    btn.classList.remove("active");
  });

  // localStorageをクリア
  localStorage.removeItem("travelFormData");
  localStorage.removeItem("generatedPlan");

  console.log("✅ フォームをクリアしました");
}
/**
 * localStorageからフォーム入力値を復元
 */
function restoreFormFromStorage() {
  const form = document.getElementById("travel-form");
  if (!form) return;

  const savedData = localStorage.getItem("travelFormData");
  if (savedData) {
    const data = JSON.parse(savedData);

    if (document.getElementById("trip-title"))
      document.getElementById("trip-title").value = data.tripTitle || "";
    if (document.getElementById("departure"))
      document.getElementById("departure").value = data.departure || "";
    if (document.getElementById("destination"))
      document.getElementById("destination").value = data.destination || "";
    if (document.getElementById("start-date"))
      document.getElementById("start-date").value = data.startDate || "";
    if (document.getElementById("end-date"))
      document.getElementById("end-date").value = data.endDate || "";
    if (document.getElementById("budget"))
      document.getElementById("budget").value = data.budget || "";
    if (document.getElementById("people"))
      document.getElementById("people").value = data.people || 1;
    if (document.getElementById("must-visit"))
      document.getElementById("must-visit").value = data.mustVisit || "";

    // 興味カテゴリを復元
    if (data.interests) {
      const categories = data.interests.split("、").filter((i) => i.trim());
      document.querySelectorAll(".interest-btn").forEach((btn) => {
        if (categories.includes(btn.getAttribute("data-category"))) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
      });
    }
  }
}

/**
 * プレビュー画面に入力値と生成プランを表示
 */
function displayPreview() {
  const savedData = localStorage.getItem("travelFormData");
  if (!savedData) return;

  const data = JSON.parse(savedData);

  // プラン概要を更新
  const titleText = data.tripTitle
    ? `${data.tripTitle}`
    : `${data.destination}への旅行プラン`;
  const destEl = document.getElementById("preview-destination");
  if (destEl) destEl.textContent = titleText;

  const summaryParts = [];
  if (data.startDate && data.endDate) {
    const start = new Date(data.startDate).toLocaleDateString("ja-JP");
    const end = new Date(data.endDate).toLocaleDateString("ja-JP");
    summaryParts.push(`${start} ～ ${end}`);
  }
  if (data.duration) summaryParts.push(`${data.duration}日間`);
  if (data.people) summaryParts.push(`${data.people}名`);
  if (data.budget)
    summaryParts.push(`予算: ¥${parseInt(data.budget).toLocaleString()}`);
  if (summaryParts.length > 0) {
    const summaryEl = document.getElementById("preview-summary");
    if (summaryEl) summaryEl.textContent = summaryParts.join(" • ");
  }

  // 入力値表示
  const setPreviewValue = (elementId, value, fallback = "未入力") => {
    const el = document.getElementById(elementId);
    if (el) {
      el.textContent = value || fallback;
      el.className = `preview-value ${!value ? "empty" : ""}`;
    }
  };

  setPreviewValue("preview-destination-value", data.destination);
  setPreviewValue(
    "preview-budget-value",
    data.budget ? `¥${parseInt(data.budget).toLocaleString()}` : ""
  );
  setPreviewValue(
    "preview-duration-value",
    data.duration ? `${data.duration}日間` : ""
  );
  setPreviewValue(
    "preview-people-value",
    data.people ? `${data.people}名` : ""
  );
  setPreviewValue("preview-departure-value", data.departure);
  setPreviewValue("preview-interests-value", data.interests);

  // 生成されたプランを表示
  const generatedPlan = localStorage.getItem("generatedPlan");
  if (generatedPlan) {
    try {
      const plan = JSON.parse(generatedPlan);
      generateSchedulePreview(plan);
    } catch (error) {
      console.error("プランのパースエラー:", error);
      generateSchedulePreview(data);
    }
  } else {
    generateSchedulePreview(data);
  }
}

/**
 * 日程プレビューを生成（API レスポンス または 簡易プレビュー対応）
 */
function generateSchedulePreview(data) {
  const container = document.getElementById("schedule-preview-container");
  if (!container) return;

  container.innerHTML = "";

  // API レスポンス形式かどうかを判定
  if (data.schedules && Array.isArray(data.schedules)) {
    // バックエンド API レスポンス形式
    displayAPISchedule(data);
  } else {
    // 簡易プレビュー形式（フォームデータ）
    displaySimpleSchedule(data);
  }
}

/**
 * バックエンド API のスケジュールを表示
 */
function displayAPISchedule(plan) {
  const container = document.getElementById("schedule-preview-container");

  // タイトルを更新
  const titleElement = document.getElementById("schedule-title");
  if (titleElement) {
    titleElement.textContent = "✨ AIが生成した旅行プラン";
  }

  plan.schedules.forEach((daySchedule) => {
    const dayDiv = document.createElement("div");
    dayDiv.className = "day-preview";

    // 日付ヘッダー
    const dateStr = new Date(daySchedule.date).toLocaleDateString("ja-JP");
    let content = `<div class="day-preview-header">Day ${daySchedule.day} - ${dateStr}</div>`;

    // タイムライン
    if (daySchedule.timeline && Array.isArray(daySchedule.timeline)) {
      daySchedule.timeline.forEach((activity, activityIndex) => {
        content += `
          <div class="timeline-item">
            <div class="timeline-time">${activity.time}</div>
            <div class="timeline-activity">
              <div class="activity-name">${activity.activity}</div>
              <div class="activity-details">
                <span class="location">📍 ${activity.location}</span>
                <span class="cost">¥${activity.cost.toLocaleString()}</span>
                <span class="duration">${activity.duration}分</span>
              </div>
              <div class="activity-notes">${activity.notes}</div>
            </div>
            <div class="activity-actions">
              <button class="btn-edit" onclick="editActivity(${
                daySchedule.day - 1
              }, ${activityIndex})" title="編集">✏️</button>
              <button class="btn-delete" onclick="deleteActivity(${
                daySchedule.day - 1
              }, ${activityIndex})" title="削除">🗑️</button>
            </div>
          </div>
        `;
      });
    }

    // 日毎の費用
    content += `<div class="day-preview-footer">小計: ¥${daySchedule.daily_cost.toLocaleString()}</div>`;

    dayDiv.innerHTML = content;
    container.appendChild(dayDiv);
  });

  // 合計費用を表示
  const totalDiv = document.createElement("div");
  totalDiv.className = "plan-summary-box";
  totalDiv.innerHTML = `
    <div><strong>合計費用:</strong> ¥${plan.total_cost.toLocaleString()}</div>
    <div><strong>合計時間:</strong> ${Math.floor(
      plan.total_duration / 60
    )}時間</div>
  `;
  container.appendChild(totalDiv);
}

/**
 * アクティビティを削除
 */
function deleteActivity(dayIndex, activityIndex) {
  const generatedPlan = localStorage.getItem("generatedPlan");
  if (!generatedPlan) return;

  try {
    const plan = JSON.parse(generatedPlan);

    if (
      plan.schedules[dayIndex] &&
      plan.schedules[dayIndex].timeline[activityIndex]
    ) {
      const activity = plan.schedules[dayIndex].timeline[activityIndex];
      const cost = activity.cost || 0;

      plan.schedules[dayIndex].timeline.splice(activityIndex, 1);
      plan.schedules[dayIndex].daily_cost -= cost;
      plan.total_cost -= cost;
      const duration = activity.duration || 0;
      plan.total_duration -= duration;

      localStorage.setItem("generatedPlan", JSON.stringify(plan));
      displayPreview();
    }
  } catch (error) {
    console.error("Deletion error:", error);
  }
}

/**
 * アクティビティを編集
 */
function editActivity(dayIndex, activityIndex) {
  const generatedPlan = localStorage.getItem("generatedPlan");
  if (!generatedPlan) return;

  try {
    const plan = JSON.parse(generatedPlan);
    const activity = plan.schedules[dayIndex].timeline[activityIndex];

    if (!activity) return;

    const modal = document.getElementById("edit-modal") || createEditModal();

    document.getElementById("edit-time").value = activity.time;
    document.getElementById("edit-activity").value = activity.activity;
    document.getElementById("edit-location").value = activity.location;
    document.getElementById("edit-cost").value = activity.cost;
    document.getElementById("edit-duration").value = activity.duration;
    document.getElementById("edit-notes").value = activity.notes;

    document.getElementById("edit-save").onclick = () => {
      const updatedActivity = {
        time: document.getElementById("edit-time").value,
        activity: document.getElementById("edit-activity").value,
        location: document.getElementById("edit-location").value,
        cost: parseInt(document.getElementById("edit-cost").value),
        duration: parseInt(document.getElementById("edit-duration").value),
        notes: document.getElementById("edit-notes").value,
      };

      const costDiff = updatedActivity.cost - activity.cost;
      const durationDiff = updatedActivity.duration - activity.duration;

      plan.schedules[dayIndex].timeline[activityIndex] = updatedActivity;
      plan.schedules[dayIndex].daily_cost += costDiff;
      plan.total_cost += costDiff;
      plan.total_duration += durationDiff;

      localStorage.setItem("generatedPlan", JSON.stringify(plan));

      modal.style.display = "none";
      displayPreview();
    };

    modal.style.display = "block";
  } catch (error) {
    console.error("Edit error:", error);
  }
}

/**
 * 編集モーダルを作成
 */
function createEditModal() {
  const modal = document.createElement("div");
  modal.id = "edit-modal";
  modal.className = "modal";
  modal.innerHTML = `
    <div class="modal-content">
      <span class="close" onclick="document.getElementById('edit-modal').style.display='none'">&times;</span>
      <h2>Edit Activity</h2>
      <form>
        <div class="form-group">
          <label>Time:</label>
          <input type="time" id="edit-time" required>
        </div>
        <div class="form-group">
          <label>Activity:</label>
          <input type="text" id="edit-activity" required>
        </div>
        <div class="form-group">
          <label>Location:</label>
          <input type="text" id="edit-location" required>
        </div>
        <div class="form-group">
          <label>Cost (¥):</label>
          <input type="number" id="edit-cost" required>
        </div>
        <div class="form-group">
          <label>Duration (min):</label>
          <input type="number" id="edit-duration" required>
        </div>
        <div class="form-group">
          <label>Notes:</label>
          <textarea id="edit-notes" rows="3"></textarea>
        </div>
        <div class="modal-buttons">
          <button type="button" id="edit-save" class="btn btn-primary">Save</button>
          <button type="button" class="btn btn-secondary" onclick="document.getElementById('edit-modal').style.display='none'">Cancel</button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(modal);
  return modal;
}

/**
 * 簡易プレビュー（フォームデータのみ）を表示
 */
function displaySimpleSchedule(data) {
  const container = document.getElementById("schedule-preview-container");

  // 入力値がない場合
  if (!data.duration || parseInt(data.duration) === 0) {
    container.innerHTML =
      '<p style="color: var(--text-secondary); text-align: center;">旅行日数を入力してください</p>';
    return;
  }

  const days = parseInt(data.duration);
  const now = new Date();

  // 日程を生成
  for (let i = 0; i < days; i++) {
    const dayDate = new Date(now);
    dayDate.setDate(dayDate.getDate() + i);
    const dateStr = dayDate.toLocaleDateString("ja-JP");

    const dayDiv = document.createElement("div");
    dayDiv.className = "day-preview";

    let activities = [];
    if (data.interests) {
      const interestList = data.interests.split("、").slice(0, 2); // 最初の2つまで
      activities = interestList.map((interest) => ({
        name: `${interest}体験`,
        time: `${9 + i}:00～${10 + i}:00`,
      }));
    }

    let content = `<div class="day-preview-header">${
      i + 1
    }日目 - ${dateStr}</div>`;

    if (activities.length > 0) {
      activities.forEach((activity) => {
        content += `
          <div class="day-preview-time">${activity.time}</div>
          <div class="day-preview-description">🏷️ ${activity.name}</div>
        `;
      });
    } else {
      content +=
        '<div class="day-preview-description">興味・関心を入力すると、プランが自動生成されます</div>';
    }

    dayDiv.innerHTML = content;
    container.appendChild(dayDiv);
  }
}

/**
 * ページロード時の初期化
 */
window.addEventListener("DOMContentLoaded", () => {
  // window.app オブジェクトにページロードコールバックを設定
  window.app = window.app || {};
  window.app.onPageLoaded = (pageName) => {
    if (pageName === "input-form") {
      const form = document.getElementById("travel-form");
      // 新規作成の場合は古いデータをクリア
      const shouldClearForm = sessionStorage.getItem("clearForm");
      if (shouldClearForm === "true") {
        clearForm();
        sessionStorage.removeItem("clearForm");
      } else {
        // 保存されたフォーム値を復元
        restoreFormFromStorage();
      }
      if (form) {
        // 入力値をリアルタイムでlocalStorageに保存
        //form.addEventListener("input", saveFormToStorage);

        // 興味ボタンのクリック処理
        const interestBtns = document.querySelectorAll(".interest-btn");
        interestBtns.forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.preventDefault();
            btn.classList.toggle("active");
          });
        });

        // フォーム送信
        form.addEventListener("submit", async (e) => {
          e.preventDefault();
          await saveFormToStorage(); // 送信時に保存と API 呼び出し
          router.loadPage("plan-result").then(() => {
            displayPreview(); // プレビュー表示
          });
        });
      }
    } else if (pageName === "plan-result") {
      // plan-result ページが読み込まれたときプレビュー表示
      displayPreview();
    }
  };
});
