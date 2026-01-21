/**
 * 旅行プランをPDFにエクスポートする関数
 */
function exportToPDF() {
  // PDF化する要素を取得（AIが生成したプランのセクションのみ）
  const element = document.querySelector(".schedule-preview-card");

  if (!element) {
    alert("エクスポートするコンテンツが見つかりません。");
    return;
  }

  // PDF化する前にボタンを一時的に非表示
  const buttons = element.querySelectorAll("button");
  buttons.forEach((btn) => (btn.style.display = "none"));

  // PDFのオプション設定
  const opt = {
    margin: 10,
    filename: `旅行プラン_${new Date().toLocaleDateString("ja-JP")}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      letterRendering: true,
    },
    jsPDF: {
      unit: "mm",
      format: "a4",
      orientation: "portrait",
    },
  };

  // PDF生成
  html2pdf()
    .set(opt)
    .from(element)
    .save()
    .then(() => {
      // ボタンを再表示
      buttons.forEach((btn) => (btn.style.display = ""));
      console.log("PDFの生成が完了しました");
    })
    .catch((error) => {
      // エラー時もボタンを再表示
      buttons.forEach((btn) => (btn.style.display = ""));
      console.error("PDF生成エラー:", error);
      alert("PDFの生成に失敗しました。");
    });
}
